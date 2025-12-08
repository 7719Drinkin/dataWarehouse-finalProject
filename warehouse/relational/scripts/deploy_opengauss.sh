#!/bin/bash
# 参考版本，请勿直接运行
# 部署 openGauss (假设使用 tar 包安装)
set -e

echo "Starting openGauss deployment..."

# 示例：使用 Docker 运行 openGauss 容器（快速）
docker run -d --name opengauss -e GS_PASSWORD=YourPassword -p 5432:5432 containers.opengauss.org/opengauss:latest

# 等待数据库启动
sleep 20

# 执行 DDL 文件
docker cp ../../ddl/. opengauss:/ddl
docker exec -i opengauss bash -c "psql -U gaussdb -d postgres -f /ddl/dim_movies.sql"
# Repeat for other DDL

echo "openGauss deployed and DDL applied."