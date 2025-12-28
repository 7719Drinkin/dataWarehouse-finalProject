import pandas as pd
import os

# ==============  路径配置  ==============
folder_path   = r'F:\code\Python\ETL\normalization\merge'
output_folder = r'F:\code\Python\ETL\normalization\merge_clean_1'
os.makedirs(output_folder, exist_ok=True)

csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# 非电影关键词
non_movie_keywords = [
    'CDs & Vinyl', 'Books', 'Music Videos & Concerts', 'TV', 'Video Games',
    'Exercise', 'Workout', 'Aerobic', 'Yoga', 'Pilates', 'Fitness',
    'Educational', 'Instructional', 'Learning', 'Tutorial', 'Lecture',
    'Course', 'Seminar', 'Workshop', 'How-to', 'Guide',
    'Music Video', 'Concert', 'Performance', 'Live',
    'Documentary', 'Documentaries',
    'Sermon', 'Sermons', 'Worship', 'Bible', 'Gospel', 'Christian', 'Church',
    'Ministry', 'Prayer', 'Faith', 'Religion', 'Spiritual',
    'Children', 'Kids', 'Family', 'Educational', 'Learning',
    'Workbook', 'Textbook', 'Study', 'Student', 'Teacher',
    'Algebra', 'Mathematics', 'Math', 'Calculus', 'Geometry',
    'Dance', 'Dancing', 'Choreography',
    'Business', 'Marketing', 'Management', 'Training',
    'Cooking', 'Recipe', 'Food', 'Culinary',
    'Sports', 'Athletic', 'Coaching', 'Training',
    'Health', 'Medical', 'Nursing', 'Medicine'
]

movie_keywords = ['prime video', 'movies', 'blu-ray', 'anime', 'movie', 'film']

def valid(v):
    return pd.notna(v) and str(v).strip() not in ('', '[]', '{}', 'nan', 'None')


def is_non_movie(row):
    asin = str(row.get('movie_id', ''))
    versions = str(row.get('versions', ''))

    # 1. 非电影关键词
    for kw in non_movie_keywords:
        if kw.lower() in versions.lower():
            return True

    # 2. 电影关键词
    for kw in movie_keywords:
        if kw.lower() in versions.lower():
            return False

    # 3. 有导演/演员
    if valid(row.get('director')) or valid(row.get('actors')) or valid(row.get('starring')):
        return False

    # 4. 全空
    return True


# ==============  记录非电影ASIN  ==============
for file_name in csv_files:
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path).reset_index(drop=True)

    # 用布尔数组判断哪些是非电影
    non_movie_mask = df.apply(is_non_movie, axis=1)

    # 记录非电影ASIN
    non_movie_df = df[non_movie_mask].copy()
    non_movie_asins = non_movie_df['movie_id'].dropna().astype(str).tolist()

    # 将非电影的ASIN写入对应的文件
    non_movie_asins_file = os.path.join(output_folder, f"non_movie_asins_{file_name}")
    with open(non_movie_asins_file, 'w', encoding='utf-8') as f:
        for asin in non_movie_asins:
            f.write(f"{asin}\n")

    print(f"{file_name}  记录了 {len(non_movie_asins)} 个非电影ASIN")


# ==============  删除非电影记录  ==============
total_deleted = 0                       # ← 新增计数器

for file_name in csv_files:
    file_path   = os.path.join(folder_path, file_name)
    df          = pd.read_csv(file_path).reset_index(drop=True)

    # 读取对应的非电影 ASIN 文件
    non_movie_asins_file = os.path.join(output_folder, f"non_movie_asins_{file_name}")
    with open(non_movie_asins_file, 'r', encoding='utf-8') as f:
        non_movie_asins = [line.strip() for line in f.readlines()]

    total_deleted += len(non_movie_asins)   # ← 累加

    # 删除并保存
    df_cleaned = df[~df['movie_id'].isin(non_movie_asins)]
    out_file   = os.path.join(output_folder, f"cleaned_{file_name}")
    df_cleaned.to_csv(out_file, index=False)

    print(f"{file_name}  删除了 {len(non_movie_asins)} 个非电影记录，已保存为 {out_file}")

print(f'\n===== 总计：共删除 {total_deleted} 个非电影 ASIN =====')

