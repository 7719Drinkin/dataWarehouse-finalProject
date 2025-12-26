# Hadoop + Spark 单节点镜像
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/openjdk:8u342-jdk-bullseye

# ===== 基础环境变量 =====
ENV HADOOP_HOME=/opt/hadoop
ENV SPARK_HOME=/opt/spark
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin:$SPARK_HOME/sbin

# ===== 使用华为云 Debian 源 & 安装依赖 =====
RUN sed -i 's@deb.debian.org@repo.huaweicloud.com@g' /etc/apt/sources.list && \
    sed -i 's@security.debian.org@repo.huaweicloud.com@g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y \
        curl \
        openssh-server \
        rsync \
        procps \
        net-tools && \
    rm -rf /var/lib/apt/lists/*

# ===== SSH 运行目录（非常关键）=====
RUN mkdir -p /run/sshd

# ===== 复制 Hadoop / Spark =====
COPY hadoop-3.3.5.tar.gz /tmp/
COPY spark-3.5.7-bin-hadoop3-scala2.13.tgz /tmp/

RUN tar -zxf /tmp/hadoop-3.3.5.tar.gz -C /opt/ && \
    mv /opt/hadoop-3.3.5 $HADOOP_HOME && \
    tar -zxf /tmp/spark-3.5.7-bin-hadoop3-scala2.13.tgz -C /opt/ && \
    mv /opt/spark-3.5.7-bin-hadoop3-scala2.13 $SPARK_HOME && \
    rm -rf /tmp/*.tar.gz

# ===== 自动设置 JAVA_HOME =====
RUN JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java)))) && \
    echo "export JAVA_HOME=$JAVA_HOME" >> $HADOOP_CONF_DIR/hadoop-env.sh

# ===== Hadoop 目录准备 =====
RUN mkdir -p /hadoop/dfs/name /hadoop/dfs/data && \
    chmod -R 755 /hadoop

# ===== 复制启动脚本 =====
COPY start_hadoop.sh /start_hadoop.sh
RUN chmod +x /start_hadoop.sh

# ===== 端口 =====
EXPOSE 9870 8080 7077 4040

# ===== 启动 =====
CMD ["/start_hadoop.sh"]
