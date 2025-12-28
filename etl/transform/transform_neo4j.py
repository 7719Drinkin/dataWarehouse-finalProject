# -*- coding:utf-8 -*-
"""
一次性把 Amazon 电影数据灌入 Neo4j
依赖：py2neo ≥ 50，pandas
"""
import uuid
import os
import re
import json
import glob
import pandas as pd
from py2neo import Graph, Node, Relationship, NodeMatcher
from itertools import combinations

# ----------------------- 连接 -----------------------
graph = Graph("bolt://139.196.151.22:7687", auth=("neo4j", "neo4j_password"))
matcher = NodeMatcher(graph)

# ---------- 工具：把文件夹里所有 csv 拼成一个 DataFrame ----------
def read_csv_folder(folder_path):
    files = glob.glob(os.path.join(folder_path, "*.csv"))
    if not files:
        raise FileNotFoundError(f"目录 {folder_path} 下没有找到 csv 文件")
    dfs = [pd.read_csv(f) for f in files]
    return pd.concat(dfs, ignore_index=True)

# ---------- 安全解析：把各类“数组/集合字符串”统一转 List[str] ----------
def safe_literal_list(s: str) -> list[str]:
    if pd.isna(s) or str(s).strip() == '':
        return []
    s = str(s).strip()
    # 1. 合法 JSON 优先
    if (s.startswith('[') and s.endswith(']')) or \
       (s.startswith('{') and s.endswith('}')):
        try:
            val = json.loads(s)
            return list(val) if isinstance(val, (list, set, tuple)) else []
        except Exception:
            pass
    # 2. 去掉外层 {} 后按逗号切
    inner = re.sub(r'^[{}]+|[{}]+$', '', s)
    return [x.strip() for x in inner.split(',') if x.strip()]

# ---------- 读数据 ----------
movie_df       = read_csv_folder(r"F:\code\Python\ETL\normalization\merge_clean_1")
review_df      = read_csv_folder(r"F:\code\Python\ETL\clean\review")
actor_df       = pd.read_csv(r"F:\code\Python\ETL\dim_actors.csv")
director_df    = pd.read_csv(r"F:\code\Python\ETL\dim_movies.csv")   # 含导演/类型/版本
movie_actor_df = pd.read_csv(r"F:\code\Python\ETL\movie_actor.csv")

# ---------- 统一 review_df 列名（兼容 userId/productId/profileName/time 等） ----------
rename_map = {
    'userId': 'user_id',
    'profileName': 'profile_name',
    'productId': 'product_id',
    'time': 'review_time'
}
review_df = review_df.rename(columns={c: rename_map.get(c, c) for c in review_df.columns})

# -------------- 跳过 1~3 步，直接从库里把节点读回来 --------------
movie_nodes = {m['id']: m for m in matcher.match("Movie")}
actor_nodes = {a['id']: a for a in matcher.match("Actor")}      # 修正变量名
dir_nodes   = {d['name']: d for d in matcher.match("Director")}

# ----------------------- 4. 导 User -----------------------
print(4, "importing users")
user_nodes = {}
for _, row in review_df.iterrows():
    uid = row.get('user_id')
    if pd.isna(uid):
        continue
    if uid not in user_nodes:
        u = Node("User", id=uid, profile_name=row.get('profile_name'))
        graph.merge(u, "User", "id")
        user_nodes[uid] = u

# ----------------------- 5. 关系 ACTED_IN -----------------------
print(5, "ACTED_IN")
for _, row in movie_actor_df.iterrows():
    m = movie_nodes.get(row['movie_id'])
    a = actor_nodes.get(row['actor_id'])
    if not (m and a):
        continue
    rel = Relationship(a, "ACTED_IN", m)
    rel['is_lead'] = bool(row['is_lead'])
    graph.merge(rel)

# ----------------------- 6. 关系 DIRECTED -----------------------
print(6, "DIRECTED")
for _, row in director_df.iterrows():
    m = movie_nodes.get(row['movie_id'])
    if not m:
        continue
    for d_name in safe_literal_list(row['director']):
        d = dir_nodes.get(d_name)
        if not d:  # 兜底：万一没有就现场建
            d = Node("Director", name=d_name, uuid=str(uuid.uuid4()))
            graph.merge(d, "Director", "name")
            dir_nodes[d_name] = d
        rel = Relationship(d, "DIRECTED", m)
        graph.merge(rel)

# ----------------------- 7. 关系 RATED -----------------------
print(7, "RATED")
for _, row in review_df.iterrows():
    uid   = row.get('user_id')
    mid   = row.get('product_id')  # 评论表里对应电影/产品 ID
    score = row.get('score')
    summ  = row.get('summary')
    text  = row.get('text')
    tm    = row.get('review_time')

    u = user_nodes.get(uid)
    m = movie_nodes.get(mid)
    if not (u and m):
        continue
    rel = Relationship(u, "RATED", m)
    rel['score']       = score
    rel['summary']     = summ
    rel['review_text'] = text
    rel['review_time'] = tm
    graph.merge(rel)

# ----------------------- 8. 关系 CO_ACTED_WITH -----------------------
print(8, "CO_ACTED_WITH")
for mid, group in movie_actor_df.groupby('movie_id'):
    aids = group['actor_id'].tolist()
    for a1, a2 in combinations(aids, 2):
        n1, n2 = actor_nodes.get(a1), actor_nodes.get(a2)
        if n1 and n2:
            rel = Relationship(n1, "CO_ACTED_WITH", n2)
            graph.merge(rel)

# ----------------------- 9. 关系 COLLABORATED_WITH -----------------------
print(9, "COLLABORATED_WITH")
collab = {}
for _, row in movie_actor_df.iterrows():
    mid = row['movie_id']
    aid = row['actor_id']
    dirs = safe_literal_list(
        director_df.loc[director_df['movie_id'] == mid, 'director'].iloc[0]
    ) if mid in director_df['movie_id'].values else []
    for d_name in dirs:
        collab[(d_name, aid)] = collab.get((d_name, aid), 0) + 1

for (d_name, aid), cnt in collab.items():
    d = dir_nodes.get(d_name)
    a = actor_nodes.get(aid)
    if d and a:
        rel = Relationship(d, "COLLABORATED_WITH", a)
        rel['movies_count'] = cnt
        graph.merge(rel)

print("All nodes & relations imported successfully!")