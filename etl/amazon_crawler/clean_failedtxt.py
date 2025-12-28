def remove_duplicates(filename):
    # 读取文件内容
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 使用集合来去重，同时保持顺序
    seen = set()
    unique_lines = []

    for line in lines:
        line = line.strip()  # 去除首尾空白字符
        if line and line not in seen:  # 非空且未出现过
            seen.add(line)
            unique_lines.append(line)

    # 写回文件
    with open(filename, 'w', encoding='utf-8') as f:
        for line in unique_lines:
            f.write(line + '\n')

    print(f"已删除重复行，原始行数: {len(lines)}，去重后行数: {len(unique_lines)}")


# 使用示例
if __name__ == "__main__":
    remove_duplicates("failed.txt")