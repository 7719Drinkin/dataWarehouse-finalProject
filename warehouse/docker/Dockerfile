FROM openjdk:8-jdk-slim

ENV HADOOP_HOME=/opt/hadoop
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin:$SPARK_HOME/sbin

# 安装依赖
RUN apt-get update && apt-get install -y curl ssh rsync procps net-tools && rm -rf /var/lib/apt/lists/*

# 复制本地 tar 包
COPY hadoop-3.3.5.tar.gz /tmp/
COPY spark-3.5.7-bin-hadoop3-scala2.13.tgz /tmp/

# 解压
RUN tar -zxf /tmp/hadoop-3.3.5.tar.gz -C /opt/ && mv /opt/hadoop-3.3.5 $HADOOP_HOME && \
    tar -zxf /tmp/spark-3.5.7-bin-hadoop3-scala2.13.tgz -C /opt/ && mv /opt/spark-3.5.7-bin-hadoop3-scala2.13 $SPARK_HOME && \
    rm -rf /tmp/*.tar.gz

# Hadoop 配置
RUN echo "export JAVA_HOME=/usr/local/openjdk-8" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# 开放端口
EXPOSE 9870 8080 50070 50075 50090 4040 7077

CMD ["/bin/bash"]
