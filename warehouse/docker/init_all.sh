#!/usr/bin/env bash
set -euo pipefail

# -------------------------------
# detect docker compose
# -------------------------------
if command -v docker compose >/dev/null 2>&1; then
    DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
else
    echo "❌ docker compose not installed"
    exit 1
fi

BASE_DIR=$(cd "$(dirname "$0")" && pwd)
cd $BASE_DIR

echo "▶ Starting docker compose..."
$DC up -d

# -------------------------------
# Wait for openGauss
# -------------------------------
echo "▶ Waiting for openGauss to be ready..."
for i in {1..40}; do
  if docker exec opengauss bash -c "gsql -d postgres -U omm -c 'SELECT 1;'" >/dev/null 2>&1; then
    echo "✔ openGauss ready"
    break
  fi
  echo "  ...waiting openGauss ($i/40)"
  sleep 5
done

if docker exec opengauss bash -c "test -f /docker-entrypoint-initdb.d/init.sql"; then
  echo "▶ Applying openGauss init.sql ..."
  docker exec -i opengauss gsql -d postgres -U omm -f /docker-entrypoint-initdb.d/init.sql
  echo "✔ openGauss init.sql applied"
fi

# -------------------------------
# Wait for HiveServer2
# -------------------------------
echo "▶ Waiting for HiveServer2..."
for i in {1..40}; do
  if docker exec hive-server bash -c "/opt/hive/bin/beeline -u 'jdbc:hive2://localhost:10000' -e 'show databases;'" >/dev/null 2>&1; then
    echo "✔ Hive ready"
    break
  fi
  echo "  ...waiting Hive ($i/40)"
  sleep 5
done

echo "▶ Applying Hive init.hql..."
docker cp hive/init.hql hive-server:/opt/hive-init/init.hql || true
docker exec hive-server bash -c "/opt/hive/bin/beeline -u 'jdbc:hive2://localhost:10000' -f /opt/hive-init/init.hql" || true
echo "✔ Hive init.hql applied"

# -------------------------------
# Wait for Neo4j
# -------------------------------
echo "▶ Waiting for Neo4j..."
for i in {1..30}; do
  if docker exec neo4j bash -c "curl -s http://localhost:7474/" >/dev/null 2>&1; then
    echo "✔ Neo4j ready"
    break
  fi
  echo "  ...waiting Neo4j ($i/30)"
  sleep 3
done

echo "▶ Applying Neo4j init.cypher..."
docker cp neo4j/init.cypher neo4j:/init.cypher || true
docker exec neo4j bash -c "cat /init.cypher | /var/lib/neo4j/bin/cypher-shell -u neo4j -p neo4j_password" || true
echo "✔ Neo4j init.cypher applied"

echo "🎉 ALL INITIALIZATION COMPLETE"