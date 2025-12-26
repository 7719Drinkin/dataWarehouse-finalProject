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
  if docker exec -u omm opengauss bash -c "export LD_LIBRARY_PATH=/usr/local/opengauss/lib:\$LD_LIBRARY_PATH && /usr/local/opengauss/bin/gsql -d postgres -U omm -c 'SELECT 1;'" >/dev/null 2>&1; then
    echo "✔ OpenGauss ready"
    break
  fi
  echo "  ...waiting OpenGauss ($i/40)"
  sleep 5
done

echo "▶ Applying OpenGauss init.sql..."
docker cp "$BASE_DIR/opengauss/init.sql" opengauss:/init.sql
docker exec -u omm opengauss bash -c "export LD_LIBRARY_PATH=/usr/local/opengauss/lib:\$LD_LIBRARY_PATH && /usr/local/opengauss/bin/gsql -d postgres -U omm -f /init.sql"
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
# 使用宿主机挂载的 /warehouse 目录确保可写
docker exec hive-server bash -c "mkdir -p /tmp/hive-init && cp /opt/hive-init/init.hql /tmp/hive-init/init.hql"
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

echo ""
echo "═══════════════════════════════════════"
echo "▶ Resource Limits Verification"
echo "═══════════════════════════════════════"

# 检查CPU限制
CPU_NANO=$(docker inspect hive-server --format='{{.HostConfig.NanoCpus}}')
if [ "$CPU_NANO" = "1500000000" ]; then
    echo "✅ CPU限制: 1.5 cores (正确)"
else
    echo "❌ CPU限制: $CPU_NANO (期望: 1500000000)"
fi

# 检查内存限制
MEMORY=$(docker inspect hive-server --format='{{.HostConfig.Memory}}')
if [ "$MEMORY" = "4294967296" ]; then
    echo "✅ 内存限制: 4GB (正确)"
else
    echo "❌ 内存限制: $MEMORY (期望: 4294967296)"
fi

echo ""
echo "▶ Current resource usage:"
docker stats hive-server --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""
echo "💡 Use 'docker stats hive-server' to monitor in real-time"

echo "🎉 ALL INITIALIZATION COMPLETE"
