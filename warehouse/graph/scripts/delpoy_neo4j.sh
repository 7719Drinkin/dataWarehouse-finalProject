#!/bin/bash
# 参考版本，请勿直接运行
# 用于向远程 Neo4j Aura 实例提交约束和基础导入脚本（通过 HTTP Query API）
# 请替换 NEO4J_API_KEY 或 使用 Basic auth

NEO4J_QUERY_URL="https://cce74607.databases.neo4j.io/db/neo4j/query/v2"
AUTH_USER="neo4j"
AUTH_PASS="<YOUR_PASSWORD>" # 你在 Neo4j Aura 控制台获得的密码

# 创建约束示例
curl -s -X POST ${NEO4J_QUERY_URL} \
  -H "Content-Type: application/json; charset=UTF-8" \
  -u ${AUTH_USER}:${AUTH_PASS} \
  -d '{"statements":[{"cypher":"CREATE CONSTRAINT movie_id_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.id IS UNIQUE;"}]}'

echo "Neo4j constraints applied (response code: $?)."