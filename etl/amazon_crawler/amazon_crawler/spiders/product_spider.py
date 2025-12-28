# product_spider.py
import os
import scrapy
import mysql.connector
from pathlib import Path


class ProductSpider(scrapy.Spider):
    name = "amazon_crawler"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 先不初始化需要settings的属性
        self.save_dir = None
        self.failed_file = None
        self.new_files_list = None
        self.existing_files = set()
        self.product_ids = []
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider._init_settings()
        return spider
        
    def _init_settings(self):
        """初始化需要settings的配置"""
        self.save_dir = Path(self.settings.get("MONITOR_DIR"))
        self.save_dir.mkdir(exist_ok=True)

        self.failed_file = Path(self.settings.get("FAILED_FILE"))
        self.new_files_list = Path(self.settings.get("NEW_FILES_LIST"))

        # 🚨 路径验证
        self.log("=== 路径配置验证 ===")
        self.log(f"MONITOR_DIR: {self.save_dir.absolute()}")
        self.log(f"FAILED_FILE: {self.failed_file.absolute()}")
        self.log(f"NEW_FILES_LIST: {self.new_files_list.absolute()}")
        self.log(f"FAILED_FILE 是否存在: {self.failed_file.exists()}")
        self.log("===================")

        # 加载需要跳过的ASIN
        self.existing_files = self._get_existing_files()

        # 连接数据库获取ASIN列表
        try:
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="zd205428",
                database="amazon_movies"
            )
            cursor = db.cursor()
            cursor.execute("SELECT DISTINCT productId FROM reviews")
            self.product_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            db.close()

            self.total = len(self.product_ids)
            self.log(f"总ASIN数量: {self.total}")
            self.log(f"已存在/失败ASIN数量: {len(self.existing_files)}")
            self.log(f"待处理ASIN数量: {self.total - len(self.existing_files)}")

        except Exception as e:
            self.log(f"数据库连接失败: {e}")
            self.product_ids = []

    def _get_existing_files(self):
        """获取需要跳过的ASIN - 🚨 修复：确保正确读取所有来源"""
        existing = set()

        # 1. 检查已下载的成功文件 (pages目录中的.html文件)
        save_path = Path(self.save_dir)
        self.log(f"检查下载目录: {save_path.absolute()}")
        
        if save_path.exists():
            html_files = list(save_path.glob("*.html"))
            self.log(f"找到 {len(html_files)} 个HTML文件在下载目录中")
            
            for file_path in html_files:
                asin = file_path.stem
                existing.add(asin)
                if len(existing) <= 5:  # 只记录前5个，避免日志过多
                    self.log(f"发现已下载文件: {asin}")

        # 2. 检查网络请求失败记录 (failed.txt)
        self.log(f"检查失败文件: {self.failed_file.absolute()}")
        self.log(f"失败文件是否存在: {self.failed_file.exists()}")
        
        if self.failed_file.exists():
            try:
                with open(self.failed_file, 'r', encoding='utf-8') as f:
                    failed_asins = set()
                    lines = f.readlines()
                    self.log(f"失败文件行数: {len(lines)}")
                    
                    for line_num, line in enumerate(lines, 1):
                        asin = line.strip()
                        if asin:
                            failed_asins.add(asin)
                            if len(failed_asins) <= 5:  # 只记录前5个
                                self.log(f"第{line_num}行读取到失败ASIN: '{asin}'")
                        else:
                            self.log(f"第{line_num}行为空行")
                    
                    self.log(f"从 failed.txt 读取到 {len(failed_asins)} 个失败ASIN")
                    existing.update(failed_asins)
                    
            except Exception as e:
                self.log(f"读取 failed.txt 失败: {e}")
                # 输出更详细的错误信息
                import traceback
                self.log(f"错误详情: {traceback.format_exc()}")
        else:
            self.log("失败文件不存在，跳过读取")

        self.log(f"总计需要跳过的ASIN数量: {len(existing)}")
        
        # 验证最终结果
        sample_existing = list(existing)[:10] if existing else []
        if sample_existing:
            self.log(f"existing_files 中的示例ASIN (前10个): {sample_existing}")
        else:
            self.log("⚠️ 警告: existing_files 为空！")
            
        return existing


    def start_requests(self):
        """生成请求 - 🚨 修复：确保正确跳过已处理的ASIN"""
        processed_count = 0
        new_count = 0
        
        # 验证 product_ids 和 existing_files
        self.log(f"数据库中的ASIN数量: {len(self.product_ids)}")
        self.log(f"需要跳过的ASIN数量: {len(self.existing_files)}")
        
        for asin in self.product_ids:
            # 跳过已成功下载或网络失败的ASIN
            if asin in self.existing_files:
                processed_count += 1
                if processed_count <= 10:  # 只记录前10个跳过的，避免日志过多
                    self.log(f"跳过已处理ASIN: {asin}")
                continue

            new_count += 1
            url = f"https://www.amazon.com/dp/{asin}"

            if new_count <= 10:  # 只记录前10个新请求，避免日志过多
                self.log(f"生成新请求 ({new_count}): {asin}")

            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"asin": asin},
                errback=self.err_handler
            )

        self.log(f"请求生成完成: 跳过 {processed_count} 个已处理ASIN, 生成 {new_count} 个新请求")
        
        # 如果新请求数量为0，说明可能有逻辑问题
        if new_count == 0 and len(self.product_ids) > 0:
            self.log("⚠️ 警告: 没有生成任何新请求！可能的原因:")
            self.log(f"  - 数据库ASIN数量: {len(self.product_ids)}")
            self.log(f"  - 跳过的ASIN数量: {len(self.existing_files)}")
            self.log(f"  - 可能所有ASIN都已被处理")

    def parse(self, response):
        """处理响应 - 只要200状态码就保存"""
        asin = response.meta["asin"]
        filename = f"{asin}.html"
        filepath = f"{self.save_dir}/{filename}"

        # 只要状态码是200就保存
        if response.status == 200:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
            self.log(f"下载成功: {asin}")
            
            # 记录到新文件列表
            self._record_new_file(filename)
        else:
            self.log(f"下载失败: {asin} (状态码: {response.status})")
            # 记录到失败文件
            self._record_failed_asin(asin)

    def err_handler(self, failure):
        """处理请求错误 - 一律记录到失败文件"""
        asin = failure.request.meta["asin"]

        self.log(f"下载失败: {asin} (网络错误)")
        # 记录到失败文件
        self._record_failed_asin(asin)

    def _record_new_file(self, filename):
        """记录新文件到新文件列表"""
        try:
            with open(self.new_files_list, "a", encoding="utf-8") as f:
                f.write(f"{filename}\n")
            self.log(f"已记录新文件: {filename}")
        except Exception as e:
            self.log(f"记录新文件失败: {filename}, 错误: {e}")

    def _record_failed_asin(self, asin):
        """记录失败的ASIN到失败文件"""
        try:
            with open(self.failed_file, "a", encoding="utf-8") as f:
                f.write(f"{asin}\n")
            self.log(f"已记录失败ASIN: {asin}")
        except Exception as e:
            self.log(f"记录失败ASIN失败: {asin}, 错误: {e}")