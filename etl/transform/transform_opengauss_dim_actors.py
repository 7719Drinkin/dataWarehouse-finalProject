# -*- coding: utf-8 -*-
"""
专供 dim_actors 一张表
CSV -> openGauss 139.196.151.22:5432 / movie_dw.dim_actors
"""

import csv
import psycopg2

CSV_PATH  = r"F:\code\Python\ETL\dim_actors.csv"   # 本地文件
TABLE_NAME = "dim_actors"                           # 目标表名

DB = dict(host="139.196.151.22",
          port=5432,
          user="gaussdb",
          password="GaussDB@2025",   # 换成真实密码
          dbname="movie_dw")

def main():
    conn = psycopg2.connect(**DB)
    cur  = conn.cursor()

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = [c.strip() for c in next(reader)]
        cols   = ",".join(header)
        create = ",".join([f"{c} TEXT" for c in header])

        # 建表（仅 TEXT 类型）
        cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        cur.execute(f"CREATE TABLE {TABLE_NAME} ({create})")

        # COPY 入库
        cur.copy_expert(f"COPY {TABLE_NAME} ({cols}) FROM STDIN WITH CSV HEADER", f)

    conn.commit()
    print(f"[OK] {CSV_PATH} 已导入 {TABLE_NAME} ，{cur.rowcount} 行")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()