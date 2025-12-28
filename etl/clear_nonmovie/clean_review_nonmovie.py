import pandas as pd
import os
import math

# 设置文件路径
asin_file = r'F:\code\Python\ETL\normalization\merge_clean\all_movie_asins.txt'
reviews_file = r'F:\code\Python\ETL\reviews.csv'
output_dir = r'F:\code\Python\ETL\clean\review'

# 创建输出目录
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 1. 读取ASIN列表
print("正在读取ASIN列表...")
with open(asin_file, 'r', encoding='utf-8') as f:
    movie_asins = set(line.strip() for line in f if line.strip())

print(f"从 {asin_file} 中读取到 {len(movie_asins)} 个ASIN")

# 2. 读取review文件
print("正在读取review文件...")
try:
    # 尝试不同编码读取文件
    try:
        reviews_df = pd.read_csv(reviews_file, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            reviews_df = pd.read_csv(reviews_file, encoding='latin-1')
        except UnicodeDecodeError:
            reviews_df = pd.read_csv(reviews_file, encoding='ISO-8859-1')

    print(f"原始review文件共有 {len(reviews_df)} 行数据")
    print("列名：", reviews_df.columns.tolist())

    # 根据用户信息，ASIN列名为'productId'
    asin_column = 'productId'

    if asin_column not in reviews_df.columns:
        print(f"错误：在review文件中找不到列 '{asin_column}'")
        print("review文件的列名：", reviews_df.columns.tolist())

        # 尝试查找可能的ASIN列
        possible_columns = []
        for col in reviews_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['asin', 'product', 'item', 'movie', 'id']):
                possible_columns.append(col)

        if possible_columns:
            print(f"可能的ASIN列：{possible_columns}")
            asin_column = possible_columns[0]
            print(f"将使用 '{asin_column}' 作为ASIN列")
        else:
            exit(1)

    print(f"使用列 '{asin_column}' 作为ASIN标识")

    # 3. 过滤数据，只保留movie_asins中的ASIN
    print("正在过滤数据...")

    # 确保productId列为字符串类型
    reviews_df[asin_column] = reviews_df[asin_column].astype(str)

    # 过滤数据
    filtered_df = reviews_df[reviews_df[asin_column].isin(movie_asins)].copy()

    print(f"过滤后保留 {len(filtered_df)} 行数据")
    print(f"删除了 {len(reviews_df) - len(filtered_df)} 行数据")

    if len(filtered_df) == 0:
        print("警告：过滤后没有数据！请检查ASIN匹配是否正确")
        print("前10个电影ASIN示例：", list(movie_asins)[:10])
        print("前10个review ASIN示例：", reviews_df[asin_column].head(10).tolist())

    # 4. 将数据拆分为10000份
    print("正在拆分数据...")

    # 计算每份的行数
    total_rows = len(filtered_df)
    chunk_size = math.ceil(total_rows / 10000)  # 向上取整

    # 拆分并保存
    for i in range(10000):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_rows)

        if start_idx >= total_rows:
            break  # 如果起始索引超出数据范围，停止

        chunk_df = filtered_df.iloc[start_idx:end_idx]

        # 生成文件名（5位数字编号）
        output_file = os.path.join(output_dir, f"reviews_part_{i + 1:05d}.csv")

        # 保存到CSV
        chunk_df.to_csv(output_file, index=False, encoding='utf-8')

        # 显示进度（每1000份显示一次，减少输出）
        if (i + 1) % 1000 == 0 or i == 0 or i == 9999:
            print(f"  已保存第 {i + 1:5d}/10000 份，包含 {len(chunk_df)} 行数据")

    # 计算实际生成的文件数
    actual_file_count = min(10000, math.ceil(total_rows / chunk_size))

    # 5. 生成报告
    report_file = os.path.join(output_dir, "split_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Review文件拆分报告\n")
        f.write("=" * 60 + "\n")
        f.write(f"ASIN来源文件: {asin_file}\n")
        f.write(f"原始review文件: {reviews_file}\n")
        f.write(f"输出目录: {output_dir}\n\n")
        f.write(f"原始review文件行数: {len(reviews_df):,}\n")
        f.write(f"过滤后review文件行数: {len(filtered_df):,}\n")
        f.write(f"删除的行数: {len(reviews_df) - len(filtered_df):,}\n")
        f.write(f"拆分为文件数: {actual_file_count}\n")
        f.write(f"每份文件大约行数: {chunk_size}\n")
        f.write(f"实际总输出行数: {total_rows:,}\n\n")
        f.write("前10个拆分文件:\n")

        # 列出前10个生成的文件
        split_files = [f for f in os.listdir(output_dir) if f.startswith('reviews_part_') and f.endswith('.csv')]
        split_files_sorted = sorted(split_files)

        # 只显示前10个
        for file in split_files_sorted[:10]:
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path)
            f.write(f"  {file}: {file_size:,} bytes\n")

        # 如果文件很多，显示省略信息
        if len(split_files_sorted) > 20:
            f.write(f"  ...（省略 {len(split_files_sorted) - 20} 个文件）...\n")

        # 显示后10个
        for file in split_files_sorted[-10:]:
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path)
            f.write(f"  {file}: {file_size:,} bytes\n")

        # 添加样本数据信息
        f.write("\n样本数据信息:\n")
        f.write(f"使用的ASIN列: {asin_column}\n")
        f.write(f"电影ASIN数量: {len(movie_asins)}\n")
        f.write(f"匹配到的电影ASIN数量: {filtered_df[asin_column].nunique()}\n")

        # 显示前5个匹配的ASIN
        if len(filtered_df) > 0:
            top_asins = filtered_df[asin_column].value_counts().head(10)
            f.write("\n前10个出现最多的ASIN:\n")
            for asin, count in top_asins.items():
                f.write(f"  {asin}: {count} 条评论\n")

    print("\n" + "=" * 50)
    print(f"处理完成！")
    print(f"原始数据: {len(reviews_df):,} 行")
    print(f"过滤后数据: {len(filtered_df):,} 行")
    print(f"删除数据: {len(reviews_df) - len(filtered_df):,} 行")
    print(f"拆分为 {actual_file_count} 个文件")
    print(f"输出目录: {output_dir}")
    print(f"详细报告: {report_file}")

    # 显示一些统计信息
    if len(filtered_df) > 0:
        print(f"\n匹配到的唯一ASIN数量: {filtered_df[asin_column].nunique()}")
        print(f"电影ASIN总数: {len(movie_asins)}")
        print(f"匹配比例: {filtered_df[asin_column].nunique() / len(movie_asins) * 100:.2f}%")

except FileNotFoundError as e:
    print(f"错误：找不到文件 - {e}")
except Exception as e:
    print(f"处理过程中发生错误: {e}")
    import traceback

    traceback.print_exc()

