# -*- coding: utf-8 -*-
"""
CSV导入MySQL - 智能字段类型检测版
专为超长影评数据优化
"""

import os
import pandas as pd
import re
from sqlalchemy import create_engine, text
from sqlalchemy.types import TEXT  # ✅ 通用SQLAlchemy类型
from sqlalchemy.dialects.mysql import MEDIUMTEXT, LONGTEXT  # ✅ MySQL特有类型
from sqlalchemy.exc import SQLAlchemyError
import glob
from tqdm import tqdm

# ===================== 配置区 =====================
CSV_DIR = r"F:\code\Python\ETL\normalization\merge_clean_1"
DATABASE_NAME = "amazon_movies"
TABLE_NAME = "movies_clean"

MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "zd205428",
    "charset": "utf8mb4"
}

BATCH_SIZE = 5000
CHUNK_SIZE = 10000


# ===================== 核心函数 =====================

def clean_column_name(col: str) -> str:
    """清理列名"""
    return re.sub(r'[^\w]', '_', str(col), flags=re.UNICODE)


def get_mysql_engine(db_name: str = None):
    """创建MySQL连接"""
    db_path = f"/{db_name}" if db_name else ""
    return create_engine(
        f"mysql+mysqlconnector://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@"
        f"{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}{db_path}",
        connect_args={"charset": MYSQL_CONFIG["charset"]},
        pool_pre_ping=True
    )


def detect_and_create_table(engine, csv_files: list, table: str):
    """
    智能检测字段长度并创建表
    """
    print("🔍 正在分析字段长度...")

    # 采样分析
    sample_df = pd.read_csv(csv_files[0], nrows=1000)

    column_types = {}
    for col in sample_df.columns:
        clean_name = clean_column_name(col)

        # 默认TEXT类型对象
        field_type = TEXT()

        # 如果是文本列，检查最大字节长度
        if sample_df[col].dtype == 'object':
            max_bytes = sample_df[col].dropna().astype(str).apply(
                lambda x: len(x.encode('utf-8'))
            ).max()

            # 如果接近TEXT上限(65535)或超过，使用MEDIUMTEXT
            if max_bytes > 60000:
                field_type = MEDIUMTEXT()
                print(f"  ⚠️  列 '{col}' 最大 {max_bytes:,} 字节 → MEDIUMTEXT")

        column_types[clean_name] = field_type

    # 创建表
    columns_def = []
    for col, dtype_obj in column_types.items():
        # 从类型对象获取类型名
        type_name = dtype_obj.__class__.__name__.upper()
        columns_def.append(f"`{col}` {type_name}")

    sql = f"CREATE TABLE IF NOT EXISTS `{table}` ({', '.join(columns_def)}) CHARSET=utf8mb4"

    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()

    print(f"✅ 表 `{table}` 已创建")
    return column_types


def csv_to_mysql(csv_path: str, engine, table: str, column_types: dict, batch: int):
    """安全导入CSV"""
    total_success, total_failed = 0, 0

    # 分块读取
    chunk_iter = pd.read_csv(csv_path, chunksize=CHUNK_SIZE, low_memory=False)

    with tqdm(desc=f"导入 {os.path.basename(csv_path)}", unit="行") as pbar:
        for chunk in chunk_iter:
            # 清理列名和数据
            chunk.columns = [clean_column_name(col) for col in chunk.columns]
            chunk = chunk.where(pd.notnull(chunk), None)

            # 构建dtype映射（只包含存在的列）
            dtype_map = {}
            for col in chunk.columns:
                if col in column_types:
                    dtype_map[col] = column_types[col]

            try:
                # 批量插入
                chunk.to_sql(
                    name=table,
                    con=engine,
                    if_exists='append',
                    index=False,
                    method='multi',
                    chunksize=batch,
                    dtype=dtype_map
                )
                total_success += len(chunk)
            except SQLAlchemyError as e:
                # 错误处理
                engine.dispose()
                engine = get_mysql_engine(DATABASE_NAME)

                for _, row in chunk.iterrows():
                    try:
                        pd.DataFrame([row]).to_sql(
                            name=table,
                            con=engine,
                            if_exists='append',
                            index=False
                        )
                        total_success += 1
                    except:
                        total_failed += 1
                        with open("import_errors.log", "a", encoding="utf-8") as f:
                            f.write(f"失败行: {row.to_dict()}\n")

            pbar.update(len(chunk))

    return total_success, total_failed


def main():
    files = sorted(glob.glob(os.path.join(CSV_DIR, "*.csv")))
    if not files:
        print("❌ 未找到CSV文件")
        return

    print(f"📁 找到 {len(files)} 个文件")

    # 创建数据库
    engine = get_mysql_engine()
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}`"))
        conn.commit()

    # 检测字段并创建表
    engine = get_mysql_engine(DATABASE_NAME)
    column_types = detect_and_create_table(engine, files, TABLE_NAME)

    # 导入所有文件
    total_success, total_failed = 0, 0
    for i, f in enumerate(files, 1):
        success, failed = csv_to_mysql(f, engine, TABLE_NAME, column_types, BATCH_SIZE)
        total_success += success
        total_failed += failed
        print(f"✅ {i}/{len(files)} - {os.path.basename(f)}: {success:,} 成功, {failed:,} 失败")

    # 最终结果
    with engine.connect() as conn:
        final_count = conn.execute(text(f"SELECT COUNT(*) FROM `{TABLE_NAME}`")).scalar()

    print(f"\n🎉 完成！总成功: {total_success:,} | 失败: {total_failed:,} | 表行数: {final_count:,}")

    if total_failed > 0:
        print("⚠️  部分行导入失败，查看 import_errors.log")


if __name__ == "__main__":
    main()