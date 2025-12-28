import pathlib, time, re, json, os, signal, sys
from typing import Dict, Any, List, Optional
from selectolax.parser import HTMLParser
import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm

# 路径配置
HTML_DIR = pathlib.Path(r"F:\code\Python\pages")  # 改成你的目录
OUT_DIR = pathlib.Path(r"F:\code\Python\ETL\html_parser\out")
OUT_DIR.mkdir(parents=True, exist_ok=True)
PART_PREFIX = "products_part"
PROCESSED_LIST = OUT_DIR / "processed.txt"

ROW_GROUP_SIZE = 1_000  # 根据内存调整

STOP = False  # 收到 Ctrl+C 后置为 True

def on_sigint(signum, frame):
    global STOP
    STOP = True
    print("\n收到中断信号，正在安全退出（会先 flush 缓存）...")

signal.signal(signal.SIGINT, on_sigint)

def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"[\u200e\u200f]", "", text).strip()

def clean_list(lst: List[str]) -> Optional[List[str]]:
    if not lst:
        return None
    cleaned = [clean_text(x) for x in lst if clean_text(x)]
    return cleaned or None

STOP_WORDS = {
    "all", "amazon.com", "movies & tv", "movies &amp; tv",
    "featured categories", "special interests",
    "video lecture", "college", "mathematics",
}
BAD_PATTERNS = re.compile(r"(out of 5 stars|ratings|dpAcr|acrLink|acrStars|var dpAcr|P\.when|A\.declarative)", re.I)

def text_ok(txt, min_len=2, max_len=120, max_words=10):
    t = clean_text(txt)
    if not t: return False
    if t.lower() in STOP_WORDS: return False
    if BAD_PATTERNS.search(t): return False
    if len(t) < min_len or len(t) > max_len: return False
    if len(t.split()) > max_words: return False
    if re.fullmatch(r"[0-9\-\.x\s]+", t.lower()): return False
    return True

def text_ok_lang(txt):
    t = clean_text(txt)
    if not text_ok(t, max_words=30, max_len=150): return False
    if t.lower() in {"subtitled", "subtitles", "captioned"}:
        return False
    return True

def text_ok_edition(txt):
    t = clean_text(txt)
    if not t: return False
    if BAD_PATTERNS.search(t): return False
    if len(t) < 2 or len(t) > 160: return False
    return True

def clean_tree(tree: HTMLParser):
    for n in tree.css("script, style, noscript"):
        n.decompose()

def split_people(val: str):
    parts = re.split(r",|;/|/|;|\u2022|\|", val)
    out = []
    for p in parts:
        c = clean_text(p)
        if text_ok(c):
            out.append(c)
    return out

def extract_kv_rows(tree: HTMLParser, labels_regex: str):
    out = []
    selectors = [
        "#prodDetails tr",
        "#productDetails_detailBullets_sections1 tr",
        "#detailBulletsWrapper li",
        "#detailBullets_feature_div li",
    ]
    for sel in selectors:
        for row in tree.css(sel):
            txt = row.text(separator=" ", strip=True)
            if not txt:
                continue
            if re.search(labels_regex, txt, re.I):
                if ":" in txt:
                    out.append(txt.split(":", 1)[1].strip())
                else:
                    out.append(txt.strip())
    return out

# 日期标准化为 "Month DD, YYYY"
def normalize_date(raw: str) -> Optional[str]:
    t = clean_text(raw)
    if not t:
        return None
    months = {
        "january": "January", "february": "February", "march": "March", "april": "April",
        "may": "May", "june": "June", "july": "July", "august": "August",
        "september": "September", "october": "October", "november": "November", "december": "December",
        "jan": "January", "feb": "February", "mar": "March", "apr": "April",
        "jun": "June", "jul": "July", "aug": "August", "sep": "September", "sept": "September",
        "oct": "October", "nov": "November", "dec": "December",
    }
    m = re.search(r"([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})", t)
    if m:
        mon = months.get(m.group(1).lower())
        if mon:
            return f"{mon} {int(m.group(2))}, {m.group(3)}"
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})", t)
    if m:
        mon = months.get(m.group(2).lower())
        if mon:
            return f"{mon} {int(m.group(1))}, {m.group(3)}"
    m = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", t)
    if m:
        year, mon_num, day = m.group(1), int(m.group(2)), int(m.group(3))
        if 1 <= mon_num <= 12:
            mon = [
                "January","February","March","April","May","June",
                "July","August","September","October","November","December"
            ][mon_num-1]
            return f"{mon} {day}, {year}"
    return None

def extract_release(tree: HTMLParser):
    node = tree.css_first("span[data-automation-id='release-year-badge']")
    if node:
        raw = clean_text(node.text(strip=True))
        norm = normalize_date(raw)
        return norm or raw

    label_regex = r"(release date|date first available|publication date)"
    date_regex = r"(?i)(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}"
    selectors = [
        "#detailBullets_feature_div li",
        "#detailBulletsWrapper li",
        "#prodDetails tr",
        "#productDetails_detailBullets_sections1 tr",
        "#productDetails_db_sections tr",
        "#productDetails tr",
        "#productDetailsTable tr",
        "table#productDetails_table tr",
        "table#productDetails_techSpec_section_1 tr",
    ]

    for sel in selectors:
        for li in tree.css(sel):
            raw = li.text(separator=" ", strip=True)
            if not raw:
                continue

            if re.search(label_regex, raw, re.I):
                parts = re.split(r":", raw, maxsplit=1)
                candidate = parts[1] if len(parts) == 2 else re.sub(rf"^{label_regex}\s*", "", raw, flags=re.I)
                candidate = clean_text(candidate)
                norm = normalize_date(candidate)
                return norm or candidate or clean_text(raw)

            if re.search(date_regex, raw):
                candidate = clean_text(raw)
                norm = normalize_date(candidate)
                return norm or candidate

    for node in tree.css("*"):
        txt = clean_text(node.text(strip=True))
        if not txt:
            continue
        if re.fullmatch(label_regex, txt, flags=re.I):
            sib = node.next
            while sib and not clean_text(sib.text(strip=True)):
                sib = sib.next
            if sib:
                candidate = clean_text(sib.text(strip=True))
                norm = normalize_date(candidate)
                return norm or candidate

    return None

def normalize_language(cand: str) -> Optional[str]:
    if not cand:
        return None
    t = clean_text(cand)
    t = t.lstrip(":：").strip()
    for sep in [",", "|", ";", "/"]:
        if sep in t:
            t = t.split(sep, 1)[0].strip()
            break
    return t or None

def normalize_edition(cand: str) -> Optional[str]:
    if not cand:
        return None
    t = clean_text(cand)
    t = t.lstrip(":：").strip()
    for sep in [",", "|", ";", "/"]:
        if sep in t:
            t = t.split(sep, 1)[0].strip()
            break
    return t or None

def extract_inline_cast_director(tree: HTMLParser):
    """解析标题下方 byline 的演员/导演行：Actor -> starring；Director -> directors"""
    inline_starring = []
    inline_directors = []
    selectors = [
        "#bylineInfo a",
        "#bylineInfo_feature_div a",
        "div#bylineInfo_feature_div a",
        "div#bylineInfo a",
    ]
    for sel in selectors:
        for a in tree.css(sel):
            name = clean_text(a.text(strip=True))
            if not name:
                continue
            full = clean_text(a.parent.text(separator=" ", strip=True))
            roles = re.findall(r"\(([^)]+)\)", full)
            if not roles:
                continue
            for r in roles:
                r_low = r.lower()
                if "actor" in r_low or "cast" in r_low or "starring" in r_low:
                    inline_starring.append(name)
                if "director" in r_low:
                    inline_directors.append(name)
    return clean_list(dict.fromkeys(inline_starring)), clean_list(dict.fromkeys(inline_directors))

def parse_html(path: pathlib.Path) -> dict:
    html = path.read_text(encoding="utf-8", errors="ignore")
    tree = HTMLParser(html)
    clean_tree(tree)

    asin = None
    if (node := tree.css_first("[data-asin]")):
        asin = node.attributes.get("data-asin")
    if not asin:
        m = re.search(r"([A-Z0-9]{10})", path.stem)
        if m:
            asin = m.group(1)

    title = None
    for sel in ["h1[data-automation-id='title']", "#productTitle", "span#title", "h1#title"]:
        node = tree.css_first(sel)
        if node:
            title = clean_text(node.text(strip=True))
            if title:
                break
    if not title:
        if (img := tree.css_first("img[data-testid='base-image']")):
            title = clean_text(img.attributes.get("alt", ""))
    if not title:
        if (meta := tree.css_first("meta[property='og:title']")):
            raw = clean_text(meta.attributes.get("content", ""))
            title = clean_text(raw.split(":")[0]) or raw
    if not title:
        if (meta := tree.css_first("meta[name='title']")):
            raw = clean_text(meta.attributes.get("content", ""))
            title = clean_text(raw.split(":")[0]) or raw

    release = extract_release(tree)

    genres = []
    for n in tree.css("#wayfinding-breadcrumbs_feature_div a, a[href*='genre']"):
        val = n.text(strip=True)
        if text_ok(val) and not re.search(r"(categories|featured|special)", val, re.I):
            genres.append(clean_text(val))
    for g in extract_kv_rows(tree, r"Genre"):
        genres.extend(split_people(g))
    genres = clean_list(dict.fromkeys(genres))

    directors = []
    for d in extract_kv_rows(tree, r"Director"):
        directors.extend(split_people(d))
    directors = clean_list(dict.fromkeys([d for d in directors if text_ok(d)]))

    actors = []
    for a in extract_kv_rows(tree, r"(Actor|Cast)"):
        actors.extend(split_people(a))
    actors = clean_list(dict.fromkeys([a for a in actors if text_ok(a)]))

    # 主演：只从 Starring/Stars
    starring = []
    for s in extract_kv_rows(tree, r"(Starring|Stars)"):
        starring.extend(split_people(s))
    starring = clean_list(dict.fromkeys([s for s in starring if text_ok(s)]))

    # 标题下 byline：Actor -> starring；Director -> directors
    inline_starring, inline_directors = extract_inline_cast_director(tree)
    if inline_starring:
        starring = clean_list(dict.fromkeys((starring or []) + inline_starring))
    if inline_directors:
        directors = clean_list(dict.fromkeys((directors or []) + inline_directors))

    edition = None
    for txt in extract_kv_rows(tree, r"(Edition|Format|Media Format|Subtitle|Subtitles)"):
        cleaned = normalize_edition(txt)
        if cleaned and text_ok_edition(cleaned):
            edition = cleaned
            break

    language = None
    for txt in extract_kv_rows(tree, r"(Language)"):
        cand = normalize_language(txt)
        if text_ok_lang(cand):
            language = cand
            break
    if not language:
        for li in tree.css("li"):
            txt = li.text(separator=" ", strip=True)
            if re.search(r"(Language)", txt, re.I):
                cand = normalize_language(txt.split(":", 1)[-1])
                if text_ok_lang(cand):
                    language = cand
                    break

    return {
        "asin": clean_text(asin) or None,
        "title": title or None,
        "release_date": release or None,
        "genres": genres,
        "directors": directors,
        "actors": actors,
        "starring": starring,
        "edition": edition or None,
        "language": language or None,
        "source": "amazon_html",
        "extracted_at": int(time.time()),
    }

def load_processed() -> set:
    if not PROCESSED_LIST.exists():
        return set()
    with PROCESSED_LIST.open("r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def append_processed(paths: List[str]):
    if not paths:
        return
    with PROCESSED_LIST.open("a", encoding="utf-8") as f:
        for p in paths:
            f.write(p + "\n")
        f.flush()

def next_part_index() -> int:
    existing = list(OUT_DIR.glob(f"{PART_PREFIX}_*.parquet"))
    if not existing:
        return 1
    nums = []
    for p in existing:
        m = re.search(rf"{PART_PREFIX}_(\d+)\.parquet", p.name)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1

def write_chunk(buffer, schema, part_idx):
    tmp_path = OUT_DIR / f"{PART_PREFIX}_{part_idx}.tmp"
    final_path = OUT_DIR / f"{PART_PREFIX}_{part_idx}.parquet"
    table = pa.Table.from_pylist(buffer, schema=schema)
    pq.write_table(table, tmp_path)
    os.replace(tmp_path, final_path)

def main():
    schema = pa.schema([
        ("asin", pa.string()),
        ("title", pa.string()),
        ("release_date", pa.string()),
        ("genres", pa.list_(pa.string())),
        ("directors", pa.list_(pa.string())),
        ("actors", pa.list_(pa.string())),
        ("starring", pa.list_(pa.string())),
        ("edition", pa.string()),
        ("language", pa.string()),
        ("source", pa.string()),
        ("extracted_at", pa.int64()),
    ])

    processed = load_processed()
    files = [p for p in HTML_DIR.glob("*.html") if str(p) not in processed]
    print(f"待处理: {len(files)}, 已处理: {len(processed)}")

    buffer = []
    pending_paths = []
    part_idx = next_part_index()

    try:
        for path in tqdm(files, desc="parse html"):
            if STOP:
                break
            row = parse_html(path)
            buffer.append(row)
            pending_paths.append(str(path))

            if len(buffer) >= ROW_GROUP_SIZE:
                write_chunk(buffer, schema, part_idx)
                append_processed(pending_paths)
                buffer.clear()
                pending_paths.clear()
                part_idx += 1

    finally:
        if buffer:
            write_chunk(buffer, schema, part_idx)
            append_processed(pending_paths)
        print("安全退出，缓存已落盘。")

if __name__ == "__main__":
    main()