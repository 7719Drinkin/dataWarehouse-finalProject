#!/bin/bash
# 参考版本，请勿直接运行
# 伪指令: 在单机上部署 Hive (需要 Java + Hadoop 安装)
set -e

echo "This script outlines steps for Hive setup. For production follow Apache official docs."
# Download Hive (example)
HIVE_VER=3.1.2
wget https://archive.apache.org/dist/hive/hive-${HIVE_VER}/apache-hive-${HIVE_VER}-bin.tar.gz
tar -xzf apache-hive-${HIVE_VER}-bin.tar.gz -C /opt/
ln -s /opt/apache-hive-${HIVE_VER}-bin /opt/hive

# Configure HIVE_HOME, add to PATH, configure hive-site.xml to point metastore DB

echo "Hive binaries installed. Configure hive-site.xml and start metastore and hive server2."