#!/usr/bin/env bash
set -euo pipefail
set -x

# Detect docker compose
if command -v docker compose >/dev/null 2>&1; then
    DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
else
    echo "❌ docker compose not installed"
    exit 1
fi

BASE_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$BASE_DIR"

echo "▶ Building Hadoop+Spark image..."
docker build -t hdfs-spark:latest .

echo "▶ Starting all containers..."
$DC up -d

######################################
# OpenGauss initialization
######################################
echo "▶ Waiting for OpenGauss..."
for i in {1..40}; do
  if docker exec opengauss bash -c "gsql -d postgres -U omm -c 'SELECT 1;'" >/dev/null 2>&1; then
    echo "✔ OpenGauss ready"
    break
  fi
  echo "  ...waiting OpenGauss ($i/40)"
  sleep 5
done

echo "▶ Applying OpenGauss init.sql..."
docker cp "$BASE_DIR/opengauss/init.sql" opengauss:/init.sql
docker exec opengauss bash -c "/usr/local/opengauss/bin/gsql -d postgres -U omm -f /init.sql"
echo "✔ OpenGauss init.sql applied"

######################################
# Hive initialization
######################################
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
docker exec hive-server bash -c "/opt/hive/bin/beeline -u 'jdbc:hive2://localhost:10000' -f /tmp/hive-init/init.hql"
echo "✔ Hive init.hql applied"

######################################
# Neo4j initialization
######################################
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
docker cp "$BASE_DIR/neo4j/init.cypher" neo4j:/init.cypher
docker exec neo4j bash -c "cat /init.cypher | /var/lib/neo4j/bin/cypher-shell -u neo4j -p neo4j_password"
echo "✔ Neo4j init.cypher applied"

echo "🎉 ALL INITIALIZATION COMPLETE"
