# -*- coding: utf-8 -*-
"""
dim_movies 专用加载器
CSV -> openGauss 139.196.151.22:5432 / movie_dw.dim_movies
支持 PostgreSQL 数组类型（text[]）
"""

import csv
import psycopg2
import json

CSV_PATH   = r"F:\code\Python\ETL\dim_movies.csv"
TABLE_NAME = "dim_movies"

DB = dict(host="139.196.151.22",
          port=5432,
          user="gaussdb",
          password="GaussDB@2025",   # 换成真实密码
          dbname="movie_dw")

def to_pg_array(text):
    """把 CSV 里的 JSON 数组字符串转成 PostgreSQL 数组字面量"""
    if not text or text.strip() in ("[]", ""):
        return "{}"
    try:
        lst = json.loads(text)          # 解析 JSON 数组
        return "{" + ",".join(str(v).replace('"', '\\"') for v in lst) + "}"
    except Exception:
        return "{}"

def main():
    conn = psycopg2.connect(**DB)
    cur  = conn.cursor()

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        # 建表（与 DDL 一致）
        cur.execute(f"""
        DROP TABLE IF EXISTS {TABLE_NAME};
        CREATE TABLE {TABLE_NAME}(
            movie_id        text,
            title           text,
            release_date    timestamp,
            release_year    int,
            release_quarter int,
            release_month   int,
            release_week    int,
            genres          text[],
            director        text[],
            versions        text[]
        );
        """)

        # 批量插入
        sql = f"""
        INSERT INTO {TABLE_NAME}
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        for r in rows:
            cur.execute(sql, (
                r["movie_id"],
                r["title"],
                r["release_date"] or None,
                int(r["release_year"]) if r["release_year"] else None,
                int(r["release_quarter"]) if r["release_quarter"] else None,
                int(r["release_month"]) if r["release_month"] else None,
                int(r["release_week"]) if r["release_week"] else None,
                to_pg_array(r["genres"]),
                to_pg_array(r["director"]),
                to_pg_array(r["versions"])
            ))

    conn.commit()
    print(f"[OK] {CSV_PATH} 已导入 {TABLE_NAME} ，{len(rows)} 行")
    cur.close(); conn.close()

if __name__ == "__main__":
    main()