#!/bin/bash
set -e

export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root

export HADOOP_HEAPSIZE=512
export HADOOP_NAMENODE_HEAPSIZE=512
export HADOOP_DATANODE_HEAPSIZE=512
export HADOOP_SECONDARYNAMENODE_HEAPSIZE=256
export SPARK_DRIVER_MEMORY=512m
export SPARK_EXECUTOR_MEMORY=512m

echo "=== Starting Hadoop + Spark Services ==="

# SSH 免密
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
fi

# 启动 sshd
/usr/sbin/sshd

# Hadoop 配置目录
CONF_DIR=$HADOOP_HOME/etc/hadoop
mkdir -p $CONF_DIR

# core-site.xml
cat > $CONF_DIR/core-site.xml <<EOF
<?xml version="1.0"?>
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://hadoop-spark:9000</value>
  </property>
</configuration>
EOF

# hdfs-site.xml
cat > $CONF_DIR/hdfs-site.xml <<EOF
<?xml version="1.0"?>
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///hadoop/dfs/name</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///hadoop/dfs/data</value>
  </property>
</configuration>
EOF

# 初始化目录
mkdir -p /hadoop/dfs/name /hadoop/dfs/data

# 格式化 NameNode（只做一次）
if [ ! -d "/hadoop/dfs/name/current" ]; then
    echo "Formatting NameNode..."
    hdfs namenode -format -force -nonInteractive
fi

# 启动 HDFS
echo "Starting HDFS..."
start-dfs.sh

sleep 5

# 启动 Spark Master
if [ "$SPARK_MODE" = "master" ]; then
    echo "Starting Spark Master..."
    start-master.sh
fi

echo "✅ Services started"
tail -f /dev/null
