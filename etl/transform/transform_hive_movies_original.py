# -*- coding: utf-8 -*-
"""
低CPU批量导入 Hive（Docker 容器内 HiveServer2）
核心优化：
1. 自动创建目标表（解决 Table not found 错误）
2. 列名映射：staging.movie_id → target.asin
3. 保留所有功能：断点续传、限速上传、容器操作
"""

import os
import time
import glob
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import paramiko
from pyhive import hive

# ===================== 配置区 =====================

CLEAN_DIR = r"F:\code\Python\ETL\normalization\merge_clean_1"

HIVE_HOST = "139.196.151.22"
HIVE_PORT = 10000
HIVE_USERNAME = "hive"
HIVE_DATABASE = "movie_dw"
HIVE_TABLE_TARGET = "movies_meta"
HIVE_TABLE_STG = "movies_meta_stg"

# staging 外部表 LOCATION（容器内路径）
STG_LOCATION_IN_CONTAINER = "/tmp/movie_dw/movies_meta_stg"

SSH_HOST = HIVE_HOST
SSH_PORT = 22
SSH_USER = "root"
SSH_PASSWORD = "Software007"  # 建议改用环境变量
SSH_PKEY_PATH = None

HIVE_DOCKER_CONTAINER = "hive-server"

REMOTE_STAGE_BASE = "/tmp/csv_clean_stage"
CONTAINER_STAGE_BASE = "/tmp/csv_clean_stage"
BATCH_FILES = 50
SFTP_BW_LIMIT_MB = 10
SLEEP_BETWEEN_BATCH = 1.0
REMOTE_NICE_IONICE = "nice -n 10 ionice -c2 -n7"

INSERT_MODE = "OVERWRITE"  # OVERWRITE / INTO
VERIFY_AFTER_LOAD = True

STATE_FILE = os.path.join(CLEAN_DIR, ".upload_state.json")

# staging 表列名（CSV 中的列）
STG_COLUMNS = [
    "movie_id", "title", "release_date", "genres", "director",
    "actors", "starring", "versions", "source_files"
]


# ===================== 工具函数 =====================

@dataclass
class SSHConfig:
    host: str
    port: int
    user: str
    password: Optional[str]
    pkey_path: Optional[str]


def list_csv_files(folder: str) -> List[str]:
    files = sorted(glob.glob(os.path.join(folder, "*.csv")))
    return [f for f in files if os.path.isfile(f)]


def chunked(items: List, n: int) -> List[List]:
    return [items[i:i + n] for i in range(0, len(items), n)]


def sha1_full_file(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_state() -> set:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()


def save_state(done_set: set):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(sorted(done_set), f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)


def connect_ssh(cfg: SSHConfig) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    pkey = None
    if cfg.pkey_path:
        try:
            pkey = paramiko.RSAKey.from_private_key_file(cfg.pkey_path)
        except Exception:
            pkey = paramiko.Ed25519Key.from_private_key_file(cfg.pkey_path)

    client.connect(
        hostname=cfg.host,
        port=cfg.port,
        username=cfg.user,
        password=cfg.password,
        pkey=pkey,
        timeout=20,
        allow_agent=True,
        look_for_keys=True,
    )
    return client


def run_ssh(ssh: paramiko.SSHClient, cmd: str, check: bool = True) -> Tuple[int, str, str]:
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="ignore")
    err = stderr.read().decode("utf-8", errors="ignore")
    code = stdout.channel.recv_exit_status()
    if check and code != 0:
        raise RuntimeError(f"[SSH CMD FAILED] code={code}\nCMD: {cmd}\nSTDOUT:\n{out}\nSTDERR:\n{err}")
    return code, out, err


class ThrottledSFTP:
    def __init__(self, sftp: paramiko.SFTPClient, mbps: float):
        self.sftp = sftp
        self.mbps = mbps

    def put(self, local_path: str, remote_path: str):
        if not self.mbps or self.mbps <= 0:
            self.sftp.put(local_path, remote_path)
            return

        rate_bytes = self.mbps * 1024 * 1024
        chunk = 256 * 1024
        with open(local_path, "rb") as lf:
            with self.sftp.open(remote_path, "wb") as rf:
                while True:
                    b = lf.read(chunk)
                    if not b:
                        break
                    start = time.time()
                    rf.write(b)
                    rf.flush()
                    elapsed = time.time() - start
                    target = len(b) / rate_bytes
                    if target > elapsed:
                        time.sleep(target - elapsed)


def hive_query(sql: str):
    """执行单条Hive SQL（不包含分号）"""
    conn = hive.Connection(
        host=HIVE_HOST,
        port=HIVE_PORT,
        username=HIVE_USERNAME,
        database=HIVE_DATABASE,
    )
    cur = conn.cursor()
    cur.execute(sql)
    try:
        rows = cur.fetchall()
    except Exception:
        rows = []
    cur.close()
    conn.close()
    return rows


def hive_exec_many(statements: List[str]):
    """批量执行Hive SQL（自动去除分号）"""
    for stmt in statements:
        s = stmt.strip().rstrip(";").strip()
        if s:
            hive_query(s)


# ===================== Hive SQL 构建 =====================

def build_create_stg_table_sql() -> List[str]:
    """创建 staging 外部表（读取CSV）"""
    cols = ",\n  ".join([f"{c} STRING" for c in STG_COLUMNS])
    return [
        f"CREATE DATABASE IF NOT EXISTS {HIVE_DATABASE}",
        f"""
CREATE EXTERNAL TABLE IF NOT EXISTS {HIVE_DATABASE}.{HIVE_TABLE_STG} (
  {cols}
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar"     = "\\"",
  "escapeChar"    = "\\\\"
)
STORED AS TEXTFILE
LOCATION '{STG_LOCATION_IN_CONTAINER}'
TBLPROPERTIES ("skip.header.line.count"="1")
""".strip()
    ]


def build_create_target_table_sql() -> List[str]:
    """创建目标表（ARRAY类型，列名asin）"""
    return [
        f"CREATE DATABASE IF NOT EXISTS {HIVE_DATABASE}",
        f"""
CREATE TABLE IF NOT EXISTS {HIVE_DATABASE}.{HIVE_TABLE_TARGET} (
  asin               STRING,
  title              STRING,
  release_date       DATE,
  genres             ARRAY<STRING>,
  director           ARRAY<STRING>,
  actors             ARRAY<STRING>,
  starring           ARRAY<STRING>,
  versions           ARRAY<STRING>,
  source_files       ARRAY<STRING>
)
STORED AS ORC
TBLPROPERTIES ("orc.compress"="ZLIB")
""".strip()
    ]


def detect_from_json_supported() -> bool:
    """检测Hive是否支持from_json函数"""
    try:
        hive_query("SELECT from_json('[\"a\",\"b\"]','array<string>') AS x")
        return True
    except Exception:
        return False


def expr_json_array_to_array(col: str, use_from_json: bool) -> str:
    """将JSON字符串转换为Hive数组"""
    if use_from_json:
        return f"from_json({col}, 'array<string>')"
    # Fallback: 去除[]和引号后split
    cleaned = f"regexp_replace(regexp_replace({col}, '^\\\\[|\\\\]$', ''), '\\\"', '')"
    return f"IF(trim({cleaned})='', array(), split({cleaned}, ','))"


def build_insert_sql(use_from_json: bool) -> List[str]:
    """构建INSERT SQL（movie_id -> asin）"""
    settings = [
        "SET hive.exec.parallel=false",
        "SET mapreduce.job.reduces=1",
        "SET hive.exec.reducers.bytes.per.reducer=1073741824",
        "SET hive.vectorized.execution.enabled=false",
    ]

    genres = expr_json_array_to_array("genres", use_from_json)
    director = expr_json_array_to_array("director", use_from_json)
    actors = expr_json_array_to_array("actors", use_from_json)
    starring = expr_json_array_to_array("starring", use_from_json)
    versions = expr_json_array_to_array("versions", use_from_json)
    source_files = expr_json_array_to_array("source_files", use_from_json)

    insert_kw = "INSERT INTO TABLE" if INSERT_MODE.upper() == "INTO" else "INSERT OVERWRITE TABLE"

    insert_stmt = f"""
{insert_kw} {HIVE_DATABASE}.{HIVE_TABLE_TARGET}
SELECT
  movie_id AS asin,  -- ✅ 关键：列名映射
  title,
  CAST(release_date AS DATE) AS release_date,
  {genres}       AS genres,
  {director}     AS director,
  {actors}       AS actors,
  {starring}     AS starring,
  {versions}     AS versions,
  {source_files} AS source_files
FROM {HIVE_DATABASE}.{HIVE_TABLE_STG}
""".strip()

    return settings + [insert_stmt]


def host_dir_to_container_location_cmd(host_batch_dir: str) -> str:
    """构建Docker复制命令"""
    if not HIVE_DOCKER_CONTAINER:
        raise RuntimeError("HIVE_DOCKER_CONTAINER 不能为空")

    batch_name = os.path.basename(host_batch_dir.rstrip("/"))
    container_batch_dir = f"{CONTAINER_STAGE_BASE}/{batch_name}"

    prep_inner = f"rm -rf {container_batch_dir} && mkdir -p {container_batch_dir} && mkdir -p {STG_LOCATION_IN_CONTAINER}"
    prep = f"docker exec {HIVE_DOCKER_CONTAINER} bash -lc {json.dumps(prep_inner)}"

    copy_in = f"docker cp {host_batch_dir}/. {HIVE_DOCKER_CONTAINER}:{container_batch_dir}/"

    move_inner = f"cp -f {container_batch_dir}/*.csv {STG_LOCATION_IN_CONTAINER}/"
    move = f"docker exec {HIVE_DOCKER_CONTAINER} bash -lc {json.dumps(move_inner)}"

    return f"{REMOTE_NICE_IONICE} bash -lc {json.dumps(prep + ' && ' + copy_in + ' && ' + move)}"


# ===================== 主流程 =====================

def main():
    """主执行流程：上传CSV -> 加载到Hive"""
    files = list_csv_files(CLEAN_DIR)
    if not files:
        raise RuntimeError(f"目录中未找到CSV文件: {CLEAN_DIR}")

    print(f"[LOCAL] 找到 {len(files)} 个CSV文件: {CLEAN_DIR}")

    # 加载续传状态
    done = load_state()
    todo = []
    for fp in files:
        base = os.path.basename(fp)
        sig = sha1_full_file(fp)
        key = f"{base}::{sig}"
        if key not in done:
            todo.append((fp, base, sig, key))

    if not todo:
        print("[SKIP] 无新文件需要上传（续传机制生效）")
    else:
        print(f"[PLAN] 待上传文件: {len(todo)}个")

    # 确保 staging 表存在
    print("[HIVE] 确保 staging 外部表存在...")
    hive_exec_many(build_create_stg_table_sql())
    print(f"[HIVE] staging 表已就绪: {HIVE_DATABASE}.{HIVE_TABLE_STG}")

    # 上传文件到容器
    if todo:
        ssh_cfg = SSHConfig(
            host=SSH_HOST,
            port=SSH_PORT,
            user=SSH_USER,
            password=SSH_PASSWORD,
            pkey_path=SSH_PKEY_PATH,
        )
        ssh = connect_ssh(ssh_cfg)
        try:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            stage_root = f"{REMOTE_STAGE_BASE}/{HIVE_TABLE_TARGET}_{ts}"
            run_ssh(ssh, f"mkdir -p {stage_root}")

            sftp = ssh.open_sftp()
            tsftp = ThrottledSFTP(sftp, SFTP_BW_LIMIT_MB)

            batches = chunked(todo, BATCH_FILES)
            print(f"[PLAN] 上传批次: {len(batches)} (每批{BATCH_FILES}个)")

            for bi, batch in enumerate(batches, start=1):
                host_batch_dir = f"{stage_root}/batch_{bi:04d}"
                run_ssh(ssh, f"mkdir -p {host_batch_dir}")

                print(f"\n[BATCH {bi}/{len(batches)}] 上传至 {host_batch_dir}")
                for fp, base, sig, key in batch:
                    remote_name = f"{os.path.splitext(base)[0]}_{sig[:10]}.csv"
                    rp = f"{host_batch_dir}/{remote_name}"
                    tsftp.put(fp, rp)
                    print(f"  已上传: {base} -> {remote_name}")

                print(f"[BATCH {bi}] Docker复制到容器...")
                cmd = host_dir_to_container_location_cmd(host_batch_dir)
                run_ssh(ssh, cmd, check=True)

                # 更新状态
                for _, _, _, key in batch:
                    done.add(key)
                save_state(done)

                if SLEEP_BETWEEN_BATCH and SLEEP_BETWEEN_BATCH > 0:
                    time.sleep(SLEEP_BETWEEN_BATCH)

            sftp.close()
            print("\n[OK] 文件上传完成（状态已保存）")

        finally:
            ssh.close()

    # ✅ 关键修复：确保目标表存在
    print("\n[HIVE] 确保目标表存在...")
    hive_exec_many(build_create_target_table_sql())
    print(f"[HIVE] 目标表已就绪: {HIVE_DATABASE}.{HIVE_TABLE_TARGET}")

    # 执行数据插入
    print("\n[HIVE] 准备插入数据...")
    use_from_json = detect_from_json_supported()
    print(f"[HIVE] from_json 支持: {use_from_json}")

    insert_sqls = build_insert_sql(use_from_json)
    print(f"[HIVE] 执行插入 ({INSERT_MODE}) 到 {HIVE_DATABASE}.{HIVE_TABLE_TARGET}...")
    hive_exec_many(insert_sqls)
    print("[HIVE] 插入完成")

    # 验证
    if VERIFY_AFTER_LOAD:
        rows = hive_query(
            f"SELECT asin, title, release_date FROM {HIVE_DATABASE}.{HIVE_TABLE_TARGET} LIMIT 5"
        )
        print("\n[VERIFY] 样例数据:")
        for r in rows:
            print(f"  {r}")

    # 完成信息
    print("\n" + "=" * 50)
    print("ETL 流程完成!")
    print(f"  目标表: {HIVE_DATABASE}.{HIVE_TABLE_TARGET}")
    print(f"  staging表: {HIVE_DATABASE}.{HIVE_TABLE_STG}")
    print(f"  容器路径: {STG_LOCATION_IN_CONTAINER}")
    print(f"  状态文件: {STATE_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    main()