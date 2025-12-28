import gzip
import csv

input_file = "movies.txt.gz"  # ← 换成你的路径
output_file = "reviews.csv"

fields = [
    "productId", "userId", "profileName",
    "helpfulness", "score", "time",
    "summary", "text"
]


def safe_split(line):
    """安全解析 key: value 结构，如果没有值则返回空字符串"""
    parts = line.split(":", 1)
    if len(parts) == 2:
        return parts[1].strip()
    return ""  # 避免 IndexError


with gzip.open(input_file, "rt", encoding="latin-1") as f, \
        open(output_file, "w", newline="", encoding="utf-8") as out:
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()

    current = {}

    for line in f:
        line = line.strip()

        # 逐行判断并解析
        if line.startswith("product/productId:"):
            current["productId"] = safe_split(line)
        elif line.startswith("review/userId:"):
            current["userId"] = safe_split(line)
        elif line.startswith("review/profileName:"):
            current["profileName"] = safe_split(line)
        elif line.startswith("review/helpfulness:"):
            current["helpfulness"] = safe_split(line)
        elif line.startswith("review/score:"):
            current["score"] = safe_split(line)
        elif line.startswith("review/time:"):
            current["time"] = safe_split(line)
        elif line.startswith("review/summary:"):
            current["summary"] = safe_split(line)
        elif line.startswith("review/text:"):
            current["text"] = safe_split(line)

            # text 是 block 的最后一行
            writer.writerow(current)
            current = {}
