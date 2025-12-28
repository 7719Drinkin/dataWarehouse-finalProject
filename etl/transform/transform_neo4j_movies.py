# 追加/更新 年、月、季度、周 属性
import pandas as pd
from py2neo import Graph

graph = Graph("bolt://139.196.151.22:7687", auth=("neo4j", "neo4j_password"))

df = pd.read_csv(r"F:\code\Python\ETL\dim_movies.csv",
                 usecols=['movie_id','release_year','release_month',
                          'release_quarter','release_week'])

for _,r in df.iterrows():
    if pd.isna(r['movie_id']):
        continue
    graph.run("""
        MERGE (m:Movie {id:$movie_id})
        SET m.release_year   = coalesce($year,   m.release_year),
            m.release_month  = coalesce($month,  m.release_month),
            m.release_quarter= coalesce($quarter,m.release_quarter),
            m.release_week   = coalesce($week,   m.release_week)
    """, movie_id=r['movie_id'],
        year   = None if pd.isna(r['release_year'])   else int(r['release_year']),
        month  = None if pd.isna(r['release_month'])  else int(r['release_month']),
        quarter= None if pd.isna(r['release_quarter'])else int(r['release_quarter']),
        week   = None if pd.isna(r['release_week'])   else int(r['release_week']))

print("Movie 节点的时间字段已追加/更新完成！")