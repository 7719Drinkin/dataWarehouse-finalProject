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
import pandas as pd

# ===================== 配置区 =====================

CLEAN_DIR = r"F:\code\Python\ETL\clean\review"  # Path to the review CSV files

HIVE_HOST = "139.196.151.22"
HIVE_PORT = 10000
HIVE_USERNAME = "hive"
HIVE_DATABASE = "movie_dw"
HIVE_TABLE_TARGET = "reviews_csv_ext"
HIVE_TABLE_STG = "reviews_csv_stg"

# staging 外部表 LOCATION（容器内路径）
STG_LOCATION_IN_CONTAINER = "/tmp/movie_dw/reviews_csv_stg"

SSH_HOST = HIVE_HOST
SSH_PORT = 22
SSH_USER = "root"
SSH_PASSWORD = "Software007"
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

OUT_COLUMNS = [
    "product_id", "user_id", "profile_name", "helpfulness", "score",
    "review_time", "summary", "text"
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
            return set()
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
            try:
                pkey = paramiko.Ed25519Key.from_private_key_file(cfg.pkey_path)
            except Exception as e:
                raise RuntimeError(f"无法读取私钥：{cfg.pkey_path}，错误：{e}")

    client.connect(
        hostname=cfg.host,
        port=cfg.port,
        username=cfg.user,
        password=cfg.password,
        pkey=pkey,
        timeout=20,
        banner_timeout=20,
        auth_timeout=20,
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
    # 注意：sql 里不要带 ';'
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
    for stmt in statements:
        s = stmt.strip()
        if not s:
            continue
        # 保险：去掉末尾分号（有些人手滑加了）
        s = s.rstrip().rstrip(";").strip()
        hive_query(s)


# ===================== 数据处理与加载 =====================

def process_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)

    # Convert review_time (time) from Unix timestamp to bigint
    df['review_time'] = df['time'].apply(lambda x: int(x))

    # Ensure column names match the target table structure
    df.rename(columns={
        'productId': 'product_id',
        'userId': 'user_id',
        'profileName': 'profile_name',
        'helpfulness': 'helpfulness',
        'score': 'score',
        'time': 'review_time',
        'summary': 'summary',
        'text': 'text'
    }, inplace=True)

    return df





def build_insert_sql() -> List[str]:
    settings = [
        "SET hive.exec.parallel=false",
        "SET mapreduce.job.reduces=1",
        "SET hive.exec.reducers.bytes.per.reducer=1073741824",
        "SET hive.vectorized.execution.enabled=false",
    ]

    insert_kw = "INSERT INTO TABLE" if INSERT_MODE.upper() == "INTO" else "INSERT OVERWRITE TABLE"

    # ✅ 关键：不要 USE，不要分号，表全限定名
    insert_stmt = f"""
{insert_kw} {HIVE_DATABASE}.{HIVE_TABLE_TARGET}
SELECT
  product_id,
  user_id,
  profile_name,
  helpfulness,
  score,
  review_time,
  summary,
  text
FROM {HIVE_DATABASE}.{HIVE_TABLE_STG}
""".strip()

    return settings + [insert_stmt]


def build_create_stg_table_sql() -> List[str]:
    # Define the columns for the staging table (same as the target table)
    cols = ",\n  ".join([f"{c} STRING" for c in OUT_COLUMNS])

    # Build the SQL statement to create the external staging table in Hive
    return [
        f"CREATE DATABASE IF NOT EXISTS {HIVE_DATABASE}",
        f"""
CREATE EXTERNAL TABLE IF NOT EXISTS {HIVE_DATABASE}.{HIVE_TABLE_STG} (
  {cols}
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  "separatorChar" = ",",
  "quoteChar"     = "\\""
)
STORED AS TEXTFILE
LOCATION '{STG_LOCATION_IN_CONTAINER}'
TBLPROPERTIES ('skip.header.line.count'='1')
""".strip()
    ]


# ===================== 宿主机 -> 容器：复制批次 CSV 到表 LOCATION =====================

def host_dir_to_container_location_cmd(host_batch_dir: str) -> str:
    if not HIVE_DOCKER_CONTAINER:
        raise RuntimeError("HIVE_DOCKER_CONTAINER 为空，但当前脚本按容器模式编排。请填容器名。")

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
    files = list_csv_files(CLEAN_DIR)
    if not files:
        raise RuntimeError(f"目录里没找到 csv：{CLEAN_DIR}")

    print(f"[LOCAL] found {len(files)} csv files in: {CLEAN_DIR}")

    done = load_state()
    todo = []
    for fp in files:
        base = os.path.basename(fp)
        sig = sha1_full_file(fp)
        key = f"{base}::{sig}"
        if key not in done:
            todo.append((fp, base, sig, key))

    if not todo:
        print("[SKIP] 没有需要上传的新文件（续写机制判定全部已完成）。")
    else:
        print(f"[PLAN] todo files: {len(todo)} (resume enabled)")

    print("[HIVE] ensuring staging external table ...")
    hive_exec_many(build_create_stg_table_sql())
    print("[HIVE] staging table ensured:", f"{HIVE_DATABASE}.{HIVE_TABLE_STG}")

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
            print(f"[PLAN] upload batches={len(batches)} (batch_size={BATCH_FILES})")

            for bi, batch in enumerate(batches, start=1):
                host_batch_dir = f"{stage_root}/batch_{bi:04d}"
                run_ssh(ssh, f"mkdir -p {host_batch_dir}")

                print(f"\n[BATCH {bi}/{len(batches)}] upload -> {host_batch_dir}")
                for fp, base, sig, key in batch:
                    remote_name = f"{os.path.splitext(base)[0]}_{sig[:10]}.csv"
                    rp = f"{host_batch_dir}/{remote_name}"
                    tsftp.put(fp, rp)
                    print(f"  uploaded: {base} -> {remote_name}")

                print(f"[BATCH {bi}] docker cp -> container, then cp -> {STG_LOCATION_IN_CONTAINER}")
                cmd = host_dir_to_container_location_cmd(host_batch_dir)
                run_ssh(ssh, cmd, check=True)

                for _, _, _, key in batch:
                    done.add(key)
                save_state(done)

                if SLEEP_BETWEEN_BATCH and SLEEP_BETWEEN_BATCH > 0:
                    time.sleep(SLEEP_BETWEEN_BATCH)

            sftp.close()
            print("\n[OK] uploaded + copied into container LOCATION. (resume state updated)")

        finally:
            ssh.close()

    print("\n[HIVE] preparing insert into target table ...")
    insert_sqls = build_insert_sql()
    print(f"[HIVE] inserting ({INSERT_MODE}) into {HIVE_DATABASE}.{HIVE_TABLE_TARGET} ...")
    hive_exec_many(insert_sqls)
    print("[HIVE] insert done.")

    if VERIFY_AFTER_LOAD:
        rows = hive_query(f"SELECT product_id, user_id, profile_name FROM {HIVE_DATABASE}.{HIVE_TABLE_TARGET} LIMIT 5")
        print("[VERIFY] sample rows:")
        for r in rows:
            print("  ", r)

    print("\n[DONE]")


if __name__ == "__main__":
    main()
