# -*- coding: utf-8 -*-
"""
fact_reviews 直灌 openGauss（9.x 兼容）
先文本落库，再就地 UPDATE 转成目标类型；跑完即可用
"""
import psycopg2

CSV_FILE   = r"F:\code\Python\ETL\fact_reviews.csv"
TABLE_NAME = "fact_reviews"

DB = dict(host="139.196.151.22",
          port=5432,
          user="gaussdb",
          password="GaussDB@2025",
          dbname="movie_dw")

def main():
    conn = psycopg2.connect(**DB)
    cur  = conn.cursor()

    # 1. 直接建成目标类型
    cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
    cur.execute(f"""
    CREATE TABLE {TABLE_NAME}(
        review_id      bigint,
        movie_id       text,
        user_id        text,
        profile_name   text,
        helpfulness    text,
        score          numeric(3,1),
        review_time    timestamp,
        review_year    int,
        review_quarter int,
        review_month   int,
        review_week    int,
        review_summary text,
        review_text    text
    )
    """)

    # 2. 文本 COPY（9.x 通用语法）
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        cur.copy_expert(f"COPY {TABLE_NAME} FROM STDIN WITH CSV HEADER", f)

    # 3. 就地 cast（空串变 NULL，失败变 NULL）
    cur.execute(f"""
    UPDATE {TABLE_NAME}
      SET review_id      = NULLIF(review_id,'')::bigint,
          score          = NULLIF(score,'')::numeric(3,1),
          review_time    = NULLIF(review_time,'')::timestamp,
          review_year    = NULLIF(review_year,'')::int,
          review_quarter = NULLIF(review_quarter,'')::int,
          review_month   = NULLIF(review_month,'')::int,
          review_week    = NULLIF(review_week,'')::int
    """)

    conn.commit()
    print(f"[OK] {TABLE_NAME} 灌库+cast 完成，共 {cur.rowcount} 行")
    cur.close(); conn.close()

if __name__ == "__main__":
    main()