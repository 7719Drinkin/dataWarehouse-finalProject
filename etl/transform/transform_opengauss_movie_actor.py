# -*- coding: utf-8 -*-
"""
movie_actor 直灌 openGauss
CSV -> 139.196.151.22:5432 / movie_dw.movie_actor
"""
import psycopg2

CSV_FILE   = r"F:\code\Python\ETL\movie_actor.csv"
TABLE_NAME = "movie_actor"

DB = dict(host="139.196.151.22",
          port=5432,
          user="gaussdb",
          password="GaussDB@2025",   # 换成真实密码
          dbname="movie_dw")

def main():
    conn = psycopg2.connect(**DB)
    cur  = conn.cursor()

    # 1. 建表（目标类型一次到位）
    cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
    cur.execute(f"""
    CREATE TABLE {TABLE_NAME}(
        movie_id text,
        actor_id text,
        is_lead  boolean
    )
    """)

    # 2. 文本 COPY（9.x 通用）
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        cur.copy_expert(f"COPY {TABLE_NAME} FROM STDIN WITH CSV HEADER", f)

    # 3. 就地 cast（空串→NULL，失败→NULL）
    cur.execute(f"""
    UPDATE {TABLE_NAME}
      SET is_lead = NULLIF(is_lead,'')::boolean
    """)

    conn.commit()
    print(f"[OK] {TABLE_NAME} 灌库完成，共 {cur.rowcount} 行")
    cur.close(); conn.close()

if __name__ == "__main__":
    main()