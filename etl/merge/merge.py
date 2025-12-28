import json
import re
import pandas as pd
from sqlalchemy import create_engine, text

# =====================
# 配置
# =====================
DB_URL = "mysql+pymysql://root:zd205428@localhost:3306/amazon_movies?charset=utf8mb4"
ENGINE = create_engine(
    DB_URL,
    pool_size=8,
    max_overflow=16,
    pool_recycle=3600,
    pool_pre_ping=True,
)
BATCH_SIZE = 500  # 可调

# =====================
# 规范化函数
# =====================
def canonicalize_title(title: str) -> str:
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r"\(.*?\)|\[.*?\]", " ", t)
    t = re.sub(
        r"\b(vhs|dvd|blu[-\s]?ray|4k|uhd|widescreen|collector'?s edition|box set|gift set|"
        r"director'?s cut|special edition|extended|combo|steelbook)\b",
        " ",
        t,
    )
    t = re.sub(r"[^a-z0-9\s']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def extract_year(date_str: str):
    if not date_str:
        return None
    m = re.match(r"(\d{4})", str(date_str))
    return int(m.group(1)) if m else None

def parse_date_safe(val):
    if val is None:
        return None
    s = str(val).strip()
    if s == "" or s.lower() == "nat" or s == "0000-00-00":
        return None
    ts = pd.to_datetime(s, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.date()

def canonicalize_person(name: str) -> str:
    if not name:
        return ""
    n = name.strip()
    n = n.replace(".", " ").replace(",", " , ")
    n = re.sub(r"\s+", " ", n).strip()
    if "," in n:
        parts = [p.strip() for p in n.split(",") if p.strip()]
        if len(parts) == 2:
            n = f"{parts[1]} {parts[0]}"
    n = n.lower()
    n = re.sub(r"[^a-z0-9\s']", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n

def json_or_list_to_list(val):
    if val is None or val == "":
        return []
    if isinstance(val, list):
        return val
    try:
        return json.loads(val)
    except Exception:
        return [val]

def to_json_or_null(val):
    if val is None or val == "":
        return None
    if isinstance(val, str):
        try:
            json.loads(val)
            return val
        except Exception:
            return json.dumps(val)
    return json.dumps(val)

# =====================
# DDL
# =====================
DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS movie_dim (
      movie_sk       BIGINT AUTO_INCREMENT PRIMARY KEY,
      canonical_title VARCHAR(512),
      release_year   INT,
      movie_key      VARCHAR(600) UNIQUE,
      created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      KEY idx_movie_title (canonical_title),
      KEY idx_movie_year (release_year)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS person_dim (
      person_sk      BIGINT AUTO_INCREMENT PRIMARY KEY,
      canonical_name VARCHAR(256),
      name_key       VARCHAR(300) UNIQUE,
      created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      KEY idx_person_name (canonical_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS movie_version_fct (
      version_sk     BIGINT AUTO_INCREMENT PRIMARY KEY,
      movie_sk       BIGINT,
      source_movie_id VARCHAR(64),
      raw_title      VARCHAR(512),
      raw_release_date DATE,
      raw_genres     JSON,
      raw_director   JSON,
      raw_actors     JSON,
      raw_starring   JSON,
      raw_versions   JSON,
      raw_source_files JSON,
      source_table   VARCHAR(128),
      created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      KEY idx_mv_movie_sk (movie_sk),
      FOREIGN KEY (movie_sk) REFERENCES movie_dim(movie_sk)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS movie_person_bridge (
      movie_sk    BIGINT,
      person_sk   BIGINT,
      role_type   ENUM('director','actor','starring'),
      PRIMARY KEY (movie_sk, person_sk, role_type),
      KEY idx_bridge_movie (movie_sk),
      KEY idx_bridge_person (person_sk),
      FOREIGN KEY (movie_sk) REFERENCES movie_dim(movie_sk),
      FOREIGN KEY (person_sk) REFERENCES person_dim(person_sk)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    # 合并后表，结构与原 movies 相同
    """
    CREATE TABLE IF NOT EXISTS movies_merge (
      movie_id VARCHAR(64) PRIMARY KEY,
      title VARCHAR(512),
      release_date DATE,
      genres JSON,
      director JSON,
      actors JSON,
      starring JSON,
      versions JSON,
      source_files JSON
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
]

# =====================
# 批工具
# =====================
def chunk_iterable(iterable, size):
    buf = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

# =====================
# 主 ETL
# =====================
def run_etl():
    with ENGINE.begin() as conn:
        for ddl in DDL_STATEMENTS:
            conn.execute(text(ddl))

    # 读源表
    with ENGINE.begin() as conn:
        df = pd.read_sql("SELECT * FROM movies", conn)

    # 规范化缓存
    records = []
    for _, row in df.iterrows():
        raw_title = row["title"]
        canon_title = canonicalize_title(raw_title)
        year = extract_year(str(row.get("release_date") or ""))
        raw_date = parse_date_safe(row.get("release_date"))
        records.append({
            "movie_id": row["movie_id"],
            "canon_title": canon_title,
            "year": year,
            "raw_title": raw_title,
            "raw_date": raw_date,
            "genres": to_json_or_null(row.get("genres")),
            "director": to_json_or_null(row.get("director")),
            "actors": to_json_or_null(row.get("actors")),
            "starring": to_json_or_null(row.get("starring")),
            "versions": to_json_or_null(row.get("versions")),
            "source_files": to_json_or_null(row.get("source_files")),
        })

    # movie_dim
    with ENGINE.begin() as conn:
        for batch in chunk_iterable(records, BATCH_SIZE):
            params = []
            for r in batch:
                movie_key = f"{r['canon_title']}__{r['year'] or ''}"
                params.append({
                    "canonical_title": r["canon_title"],
                    "release_year": r["year"],
                    "movie_key": movie_key
                })
            conn.execute(text("""
                INSERT IGNORE INTO movie_dim (canonical_title, release_year, movie_key)
                VALUES (:canonical_title, :release_year, :movie_key)
            """), params)

    # movie_key 映射
    with ENGINE.begin() as conn:
        movie_dim_map = {}
        rows = conn.execute(text("SELECT movie_sk, movie_key FROM movie_dim")).mappings().all()
        for r in rows:
            movie_dim_map[r["movie_key"]] = r["movie_sk"]

    # person_dim
    person_keys = set()
    for r in records:
        for role in ("director", "actors", "starring"):
            names = json_or_list_to_list(r.get(role[:-1] if role.endswith('s') else role))
            for n in names:
                canon_name = canonicalize_person(n)
                if canon_name:
                    person_keys.add(canon_name)

    with ENGINE.begin() as conn:
        for batch in chunk_iterable(list(person_keys), BATCH_SIZE):
            params = [{"canonical_name": n, "name_key": n} for n in batch]
            conn.execute(text("""
                INSERT IGNORE INTO person_dim (canonical_name, name_key)
                VALUES (:canonical_name, :name_key)
            """), params)

    with ENGINE.begin() as conn:
        person_map = {}
        rows = conn.execute(text("SELECT person_sk, name_key FROM person_dim")).mappings().all()
        for r in rows:
            person_map[r["name_key"]] = r["person_sk"]

    # movie_version_fct
    with ENGINE.begin() as conn:
        for batch in chunk_iterable(records, BATCH_SIZE):
            params = []
            for r in batch:
                movie_key = f"{r['canon_title']}__{r['year'] or ''}"
                movie_sk = movie_dim_map.get(movie_key)
                params.append({
                    "movie_sk": movie_sk,
                    "source_movie_id": r["movie_id"],
                    "raw_title": r["raw_title"],
                    "raw_release_date": r["raw_date"],
                    "raw_genres": r["genres"],
                    "raw_director": r["director"],
                    "raw_actors": r["actors"],
                    "raw_starring": r["starring"],
                    "raw_versions": r["versions"],
                    "raw_source_files": r["source_files"],
                    "source_table": "movies"
                })
            conn.execute(text("""
                INSERT INTO movie_version_fct
                (movie_sk, source_movie_id, raw_title, raw_release_date, raw_genres, raw_director,
                 raw_actors, raw_starring, raw_versions, raw_source_files, source_table)
                VALUES (:movie_sk, :source_movie_id, :raw_title, :raw_release_date, :raw_genres,
                        :raw_director, :raw_actors, :raw_starring, :raw_versions, :raw_source_files, :source_table)
            """), params)

    # movie_person_bridge
    with ENGINE.begin() as conn:
        for batch in chunk_iterable(records, BATCH_SIZE):
            bridge_params = []
            for r in batch:
                movie_key = f"{r['canon_title']}__{r['year'] or ''}"
                movie_sk = movie_dim_map.get(movie_key)
                if not movie_sk:
                    continue
                for role_col, role_type in [("director", "director"), ("actors", "actor"), ("starring", "starring")]:
                    names = json_or_list_to_list(r.get(role_col))
                    for n in names:
                        canon_name = canonicalize_person(n)
                        if not canon_name:
                            continue
                        person_sk = person_map.get(canon_name)
                        if not person_sk:
                            continue
                        bridge_params.append({
                            "movie_sk": movie_sk,
                            "person_sk": person_sk,
                            "role_type": role_type
                        })
            if bridge_params:
                conn.execute(text("""
                    INSERT IGNORE INTO movie_person_bridge (movie_sk, person_sk, role_type)
                    VALUES (:movie_sk, :person_sk, :role_type)
                """), bridge_params)

# =====================
# 构建/刷新 movies_merge（结构与 movies 相同）
# 规则：每个 movie_sk 选一个代表行：
# 1) release_date 最早的行；若都为空则按 movie_id 升序；
# 2) 代表行的原始列直接写回（不聚合），保证结构相同。
# 如果 movie_id 在多个合并簇中重复，使用 ON DUPLICATE KEY UPDATE 跳过已有。
# =====================
def build_movies_merge():
    truncate_sql = "TRUNCATE TABLE movies_merge;"
    insert_sql = """
    INSERT INTO movies_merge (movie_id, title, release_date, genres, director, actors, starring, versions, source_files)
    SELECT t.source_movie_id,
           t.raw_title,
           t.raw_release_date,
           t.raw_genres,
           t.raw_director,
           t.raw_actors,
           t.raw_starring,
           t.raw_versions,
           t.raw_source_files
    FROM (
        SELECT f.*,
               ROW_NUMBER() OVER (
                   PARTITION BY f.movie_sk
                   ORDER BY
                     CASE WHEN f.raw_release_date IS NULL THEN 1 ELSE 0 END,
                     f.raw_release_date ASC,
                     f.source_movie_id ASC
               ) AS rn
        FROM movie_version_fct f
    ) t
    WHERE t.rn = 1
    ON DUPLICATE KEY UPDATE movie_id = movie_id;  -- 无操作，跳过重复
    """
    with ENGINE.begin() as conn:
        conn.execute(text(truncate_sql))
        conn.execute(text(insert_sql))

# =====================
# 溯源查询示例
# =====================
def run_queries():
    with ENGINE.begin() as conn:
        r1 = conn.execute(text("""
            SELECT COUNT(DISTINCT m.movie_sk) AS harry_potter_movies
            FROM movie_dim m
            JOIN movie_version_fct f ON m.movie_sk = f.movie_sk
            WHERE m.canonical_title LIKE '%harry potter%';
        """)).mappings().all()[0]
        print("哈利波特电影数（合并后）:", r1)

        r2 = conn.execute(text("""
            SELECT COUNT(*) AS harry_potter_versions
            FROM movie_dim m
            JOIN movie_version_fct f ON m.movie_sk = f.movie_sk
            WHERE m.canonical_title LIKE '%harry potter%';
        """)).mappings().all()[0]
        print("哈利波特版本数（网页行）:", r2)

        r3 = conn.execute(text("""
            SELECT COUNT(*) AS hp1_webpages
            FROM movie_dim m
            JOIN movie_version_fct f ON m.movie_sk = f.movie_sk
            WHERE m.canonical_title LIKE '%harry potter%' AND m.canonical_title REGEXP 'stone|philosopher|sorcerer';
        """)).mappings().all()[0]
        print("哈利波特第一部合并后网页数:", r3)

if __name__ == "__main__":
    run_etl()
    build_movies_merge()  # 生成/刷新与原结构相同的去重表
    run_queries()