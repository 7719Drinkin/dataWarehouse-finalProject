# file_monitor.py
import os
from twisted.internet import task, reactor
from scrapy import signals
from datetime import datetime
from threading import Lock

class FileMonitorExtension:

    def __init__(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        self.is_paused = False
        self.monitoring_started = False

        # 从 settings 获取所有路径和配置
        self.files_dir = self.settings.get("MONITOR_DIR")
        self.new_files_list = self.settings.get("NEW_FILES_LIST")
        self.failed_file = self.settings.get("FAILED_FILE")
        self.threshold_kb = self.settings.get("MONITOR_MIN_SIZE_KB", 400)
        self.check_interval = self.settings.get("MONITOR_CHECK_INTERVAL", 600)
        self.pause_seconds = self.settings.get("MONITOR_PAUSE_SECONDS", 3600)
        # 可选 deleted 文件用于调试
        self.deleted_log_file = self.settings.get("DELETED_FILE", os.path.join(os.path.dirname(self.files_dir), "deleted_files.txt"))
        # 在初始化时记录路径信息
        crawler.spider.logger.info(f"[FileMonitor] 监控目录: {self.files_dir}")
        crawler.spider.logger.info(f"[FileMonitor] 新文件列表: {self.new_files_list}")
        crawler.spider.logger.info(f"[FileMonitor] 失败文件: {self.failed_file}")
        crawler.spider.logger.info(f"[FileMonitor] 删除记录文件: {os.path.abspath(self.deleted_log_file)}")
        
        self.small_file_ratio_threshold = self.settings.get("MONITOR_SMALL_FILE_RATIO", 0.5)
        # 异步安全锁
        self.lock = Lock()
        self.looping_call = None

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_opened(self, spider):
        spider.logger.info(
            f"[FileMonitor] 监控目录: {os.path.abspath(self.files_dir)}, "
            f"每 {self.check_interval}s 检测新文件是否小于 {self.threshold_kb}KB"
        )
        # 初始化 new_files_list（异步安全）
        self._clear_new_files_list()
        spider.logger.info(f"[FileMonitor] 文件监控将在60秒后启动")
        reactor.callLater(60, self.start_monitoring)

    def start_monitoring(self):
        if self.monitoring_started:
            return
        self.monitoring_started = True
        self.crawler.spider.logger.info(f"[FileMonitor] 启动定期文件监控，每 {self.check_interval} 秒检查一次")
        self.looping_call = task.LoopingCall(self.check_new_files)
        self.looping_call.start(self.check_interval, now=True)

    def spider_closed(self, spider):
        if self.looping_call and self.looping_call.running:
            self.looping_call.stop()
        spider.logger.info("[FileMonitor] 文件监控已停止")

    def _clear_new_files_list(self):
        try:
            with self.lock:
                with open(self.new_files_list, 'w', encoding='utf-8') as f:
                    f.write("")
            self.crawler.spider.logger.info(f"[FileMonitor] 已清空新文件列表")
        except Exception as e:
            self.crawler.spider.logger.error(f"[FileMonitor] 清空新文件列表失败: {e}")

    def _get_new_files_to_check(self):
        """异步安全读取并清空 new_files_list"""
        if not os.path.exists(self.new_files_list):
            return set()
        new_files = set()
        try:
            with self.lock:
                with open(self.new_files_list, 'r', encoding='utf-8') as f:
                    for line in f:
                        filename = line.strip()
                        if filename:
                            new_files.add(filename)
                # 读取后立即清空
                with open(self.new_files_list, 'w', encoding='utf-8') as f:
                    f.write("")
        except Exception as e:
            self.crawler.spider.logger.error(f"[FileMonitor] 读取新文件列表失败: {e}")
        return new_files

    def _record_new_file(self, filename):
        """异步安全记录新文件"""
        try:
            with self.lock:
                with open(self.new_files_list, "a", encoding="utf-8") as f:
                    f.write(f"{filename}\n")
        except Exception as e:
            self.crawler.spider.logger.error(f"[FileMonitor] 记录新文件失败: {filename}, 错误: {e}")

    def check_new_files(self):
        """检查新文件"""
        if not self.monitoring_started:
            return

        self.crawler.spider.logger.info(f"[FileMonitor] 开始检查新文件")

        if not os.path.exists(self.files_dir):
            self.crawler.spider.logger.warning(f"[FileMonitor] 监控目录不存在: {self.files_dir}")
            return

        new_files = self._get_new_files_to_check()

        if not new_files:
            self.crawler.spider.logger.info(f"[FileMonitor] 没有发现新文件，跳过检查")
            return

        self.crawler.spider.logger.info(f"[FileMonitor] 发现 {len(new_files)} 个新文件待检查")

        small_files = []
        valid_files = []


        for fname in new_files:
            fpath = os.path.join(self.files_dir, fname)

            if not os.path.exists(fpath):
                self.crawler.spider.logger.warning(f"[FileMonitor] 文件不存在: {fname}")
                continue

            size_kb = os.path.getsize(fpath) / 1024.0
            self.crawler.spider.logger.debug(f"[FileMonitor] 检查文件: {fname} - {size_kb:.2f}KB")

            if size_kb < self.threshold_kb:
                small_files.append((fname, size_kb))
                try:
                    os.remove(fpath)
                    self.crawler.spider.logger.debug(
                        f"[FileMonitor] 删除过小文件: {fname} - {size_kb:.2f}KB (阈值: {self.threshold_kb}KB)"
                    )
                    # 可选：记录到 deleted_files.txt，仅调试用
                    with self.lock:
                        with open(self.deleted_log_file, "a", encoding="utf-8") as f:
                            f.write(f"{datetime.now()} - {fname} - {size_kb:.2f}KB\n")
                except Exception as e:
                    self.crawler.spider.logger.error(f"[FileMonitor] 删除文件失败: {fname}, 错误: {e}")
            else:
                valid_files.append((fname, size_kb))
        total_checked=len(small_files)+len(valid_files)
        if total_checked > 3:
            small_file_ratio = len(small_files) / total_checked
        else:
            small_file_ratio = 0
        self.crawler.spider.logger.info(
            f"[FileMonitor] 检查完成: 共检查 {total_checked} 个新文件, "
            f"发现 {len(small_files)} 个小文件, "
            f"小文件比例: {small_file_ratio*100:.1f}% (阈值: {self.small_file_ratio_threshold*100}%)"
        )
        if (small_file_ratio > self.small_file_ratio_threshold and 
            total_checked >= 3 and  # 至少检查了3个文件才触发，避免样本太少
            not self.is_paused):
            
            self.crawler.spider.logger.warning(
                f"[FileMonitor] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
                f"小文件比例 {small_file_ratio*100:.1f}% 超过阈值 {self.small_file_ratio_threshold*100}%, "
                f"暂停爬虫 {self.pause_seconds} 秒"
            )
            self.handle_pause()
        elif small_file_ratio > self.small_file_ratio_threshold:
            self.crawler.spider.logger.info(
                f"[FileMonitor] 小文件比例 {small_file_ratio*100:.1f}% 超过阈值, "
                f"但检查文件数 {total_checked} 太少，不暂停爬虫"
            )
    def handle_pause(self):
        """处理暂停逻辑"""
        self.is_paused = True
        self.crawler.engine.pause()
        reactor.callLater(self.pause_seconds, self.resume_crawler)

    def resume_crawler(self):
        self.is_paused = False
        self.crawler.spider.logger.info("[FileMonitor] 恢复爬取")
        self.crawler.engine.unpause()
