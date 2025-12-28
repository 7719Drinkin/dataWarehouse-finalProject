# settings.py
from pathlib import Path
BOT_NAME = "amazon_crawler"

SPIDER_MODULES = ["amazon_crawler.spiders"]
NEWSPIDER_MODULE = "amazon_crawler.spiders"
# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# failed.txt 和 new_files.txt 自动放在项目根目录
FAILED_FILE = PROJECT_ROOT / "failed.txt"
NEW_FILES_LIST = PROJECT_ROOT / "new_files.txt"
DELETED_FILE = PROJECT_ROOT / "deleted_files.txt"
MONITOR_DIR = PROJECT_ROOT / "pages"
ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 2

DOWNLOADER_MIDDLEWARES = {
    "amazon_crawler.middlewares.RandomSleepMiddleware": 410,
    "amazon_crawler.middlewares.RandomUserAgentMiddleware": 420,
    # 如果你想使用单个代理，则继续启用:
    # "amazon_crawler.middlewares.SingleProxyMiddleware": 430,
}


DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
EXTENSIONS = {
    'amazon_crawler.extension.file_monitor.FileMonitorExtension': 500,
}


# 文件大小阈值（KB）
MONITOR_MIN_SIZE_KB = 450
# 小文件比例阈值（例如：0.5 表示 50%）
MONITOR_SMALL_FILE_RATIO = 0.8
# 检查间隔：10 分钟 = 600 秒
MONITOR_CHECK_INTERVAL = 600

# 发现小文件后的暂停时间（例如：60 分钟）
MONITOR_PAUSE_SECONDS = 1800

RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 403]

FEED_EXPORT_ENCODING = 'utf-8'
LOG_LEVEL = "INFO"