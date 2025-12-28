import sys
from pyhive import hive

HOST = "139.196.151.22"
PORT = 10000
USERNAME = "hive"
DATABASE = "movie_dw"
SOURCE_DB = "movie_dw"  # 如果源表在 movie_dw，就改为 movie_dw

SQLS = [
    "SET hive.exec.dynamic.partition = true",
    "SET hive.exec.dynamic.partition.mode = nonstrict",
    "SET hive.vectorized.execution.enabled = false",
    "SET hive.auto.convert.join = false",
    "SET hive.stats.autogather = false",
    # 选择 overwrite（全量）或 into（增量追加）
    f"""
    INSERT OVERWRITE TABLE movie_dw.movies_meta_dw
    PARTITION (p_year, p_month)
    SELECT
      asin,
      title,
      release_date,                                -- 如果是 DATE 类型，直接用
      genres,
      director,
      actors,
      starring,
      versions,
      source_files,
      year(release_date)        AS release_year,
      quarter(release_date)     AS release_quarter,
      month(release_date)       AS release_month,
      weekofyear(release_date)  AS release_week,
      year(release_date)        AS p_year,
      month(release_date)       AS p_month
    FROM {SOURCE_DB}.movies_meta
    """
]

def run_queries(conn, sqls):
    cur = conn.cursor()
    for sql in sqls:
        print(f"Running:\n{sql.strip()}\n")
        cur.execute(sql)
    cur.close()

def main():
    try:
        conn = hive.Connection(
            host=HOST,
            port=PORT,
            username=USERNAME,
            database=DATABASE,
            auth="NONE",  # 若有 Kerberos/LDAP，请调整
        )
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    try:
        run_queries(conn, SQLS)
        print("Migration finished.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()