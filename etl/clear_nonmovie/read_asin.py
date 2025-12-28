import pandas as pd
import os

# 设置文件夹路径
folder_path = r'F:\code\Python\ETL\normalization\merge_clean'

# 获取所有CSV文件
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# 用于存储所有ASIN
all_asins = []

# 处理每个CSV文件
for file_name in csv_files:
    file_path = os.path.join(folder_path, file_name)

    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)

        # 检查是否包含movie_id或asin列
        if 'movie_id' in df.columns:
            asin_column = 'movie_id'
        elif 'asin' in df.columns:
            asin_column = 'asin'
        else:
            print(f"文件 {file_name} 中未找到movie_id或asin列，跳过...")
            continue

        # 提取ASIN并添加到列表
        asins = df[asin_column].dropna().astype(str).tolist()
        all_asins.extend(asins)

        print(f"文件 {file_name} 处理完成，提取 {len(asins)} 个ASIN")

    except Exception as e:
        print(f"处理文件 {file_name} 时出错: {e}")

# 去重并排序
all_asins = sorted(list(set(all_asins)))

# 保存到文件
output_file = os.path.join(folder_path, "all_movie_asins.txt")

with open(output_file, 'w', encoding='utf-8') as f:
    for asin in all_asins:
        f.write(f"{asin}\n")

print("\n" + "=" * 50)
print(f"处理完成！")
print(f"共处理 {len(csv_files)} 个CSV文件")
print(f"提取到 {len(all_asins)} 个唯一ASIN")
print(f"ASIN列表已保存到: {output_file}")

# 可选：生成一个简短的报告
report_file = os.path.join(folder_path, "asin_extraction_report.txt")
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("ASIN提取报告\n")
    f.write("=" * 60 + "\n")
    f.write(f"处理的文件夹: {folder_path}\n")
    f.write(f"处理的CSV文件数: {len(csv_files)}\n")
    f.write(f"提取的唯一ASIN数: {len(all_asins)}\n")
    f.write("\n处理的文件列表:\n")

    for file_name in csv_files:
        f.write(f"  - {file_name}\n")

print(f"详细报告已保存到: {report_file}")