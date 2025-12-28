import sys
from pyhive import hive

HOST = "139.196.151.22"
PORT = 10000
USERNAME = "hive"
DATABASE = "movie_dw"      # 目标库（reviews_clean_amazon 所在库）
SOURCE_DB = "movie_dw"     # 源表所在库，如果不在 movie_dw，请改成实际库名
INSERT_MODE = "OVERWRITE"  # 全量用 OVERWRITE，增量追加用 INTO

set_statements = [
    "SET hive.exec.dynamic.partition = true",
    "SET hive.exec.dynamic.partition.mode = nonstrict",
    "SET hive.vectorized.execution.enabled = false",
    "SET hive.auto.convert.join = false",
    "SET hive.stats.autogather = false",
]

insert_statement = f"""
WITH src AS (
  SELECT
    product_id AS asin,
    user_id,
    profile_name,
    helpfulness,
    score,
    review_time,
    summary,
    `text`,
    CASE
      WHEN review_time > 20000000000
        THEN from_unixtime(CAST(review_time/1000 AS BIGINT))
      ELSE from_unixtime(CAST(review_time AS BIGINT))
    END AS ts
  FROM {SOURCE_DB}.reviews_csv_ext
  WHERE review_time IS NOT NULL
)
INSERT {INSERT_MODE} TABLE {DATABASE}.reviews_clean_amazon
PARTITION (year, month)
SELECT
  asin,
  user_id,
  profile_name,
  helpfulness,
  score,
  review_time            AS review_unix,
  summary                AS review_summary,
  `text`                 AS review_text,
  year(ts)               AS year,
  month(ts)              AS month
FROM src
"""

def main():
    try:
        conn = hive.Connection(
            host=HOST,
            port=PORT,
            username=USERNAME,
            database=DATABASE,
            auth="NONE",
        )
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    try:
        cur = conn.cursor()
        for sql in set_statements:
            print(f"Running:\n{sql}\n")
            cur.execute(sql)

        print(f"Running INSERT:\n{insert_statement.strip()}\n")
        cur.execute(insert_statement)

        cur.close()
        print("Migration finished.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()