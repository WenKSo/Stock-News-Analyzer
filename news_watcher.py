import os
import sys
import json
import time
import logging
import hashlib
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 将项目根目录添加到系统路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入需要的模块
from news_data_pipeline import NewsDataPipeline

# 添加src目录到系统路径
src_dir = os.path.join(os.path.dirname(__file__), 'src')
if os.path.exists(src_dir):
    sys.path.append(src_dir)
    try:
        from main import process_news_data
        MAIN_MODULE_AVAILABLE = True
    except ImportError as e:
        logging.error(f"无法导入main模块: {e}")
        MAIN_MODULE_AVAILABLE = False
else:
    MAIN_MODULE_AVAILABLE = False
    logging.error("src目录不存在，无法导入main模块")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_watcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NewsWatcher")

class NewsWatcher:
    def __init__(self, config_file="config.json"):
        """
        初始化新闻监视器
        
        参数:
        config_file: 配置文件路径
        """
        # 加载配置
        self.config = self._load_config(config_file)
        
        # 获取配置项
        self.input_dir = self.config.get("data_paths", {}).get("input_dir", "data/raw")
        self.output_dir = self.config.get("data_paths", {}).get("output_dir", "data/processed")
        self.news_data_file = self.config.get("output_json_file", "data/news_data.json")
        self.processed_records_file = self.config.get("watcher", {}).get("processed_records_file", "data/processed_records.json")
        self.check_interval = self.config.get("watcher", {}).get("check_interval_seconds", 30)
        
        # 加载已处理记录
        self.processed_records = self.load_processed_records()
        
        # 初始化数据处理流水线
        self.pipeline = NewsDataPipeline(config_file)
        
        # 确保目录存在
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.news_data_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.processed_records_file), exist_ok=True)
        
        # 如果文件不存在，创建一个空的JSON文件
        if not os.path.exists(self.news_data_file):
            with open(self.news_data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
                
        # 记录已处理的raw文件
        self.processed_raw_files = {}
        # 读取上次处理时的文件状态（如果存在）
        self.raw_files_state_file = os.path.join(os.path.dirname(self.processed_records_file), "raw_files_state.json")
        self.load_raw_files_state()
    
    def _load_config(self, config_file):
        """加载配置文件"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"配置文件 {config_file} 不存在，使用默认配置")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"加载配置文件时出错: {str(e)}")
            logger.info("使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            "data_paths": {
                "input_dir": "data/raw",
                "output_dir": "data/processed",
                "archive_dir": "data/archive"
            },
            "processing": {
                "interval_minutes": 1,
                "run_continuously": True
            },
            "integration": {
                "target_db_file": "news_database.db",
                "table_name": "news_articles"
            },
            "output_json_file": "data/news_data.json",
            "watcher": {
                "enabled": True,
                "check_interval_seconds": 30,
                "processed_records_file": "data/processed_records.json"
            }
        }
    
    def load_processed_records(self):
        """加载已处理的记录"""
        if os.path.exists(self.processed_records_file):
            try:
                with open(self.processed_records_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载已处理记录时出错: {str(e)}")
                return {}
        return {}
    
    def save_processed_records(self):
        """保存已处理的记录"""
        try:
            with open(self.processed_records_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_records, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"保存已处理记录时出错: {str(e)}")
    
    def load_raw_files_state(self):
        """加载raw目录文件的状态"""
        if os.path.exists(self.raw_files_state_file):
            try:
                with open(self.raw_files_state_file, 'r', encoding='utf-8') as f:
                    self.processed_raw_files = json.load(f)
                logger.info(f"已加载 {len(self.processed_raw_files)} 个原始文件的处理状态")
            except Exception as e:
                logger.error(f"加载raw文件状态时出错: {str(e)}")
                self.processed_raw_files = {}
        else:
            self.processed_raw_files = {}
    
    def save_raw_files_state(self):
        """保存raw目录文件的状态"""
        try:
            with open(self.raw_files_state_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_raw_files, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"保存raw文件状态时出错: {str(e)}")
    
    def generate_record_id(self, news):
        """生成记录ID（基于内容的哈希）"""
        # 组合标题和内容，或者其他可以唯一标识新闻的字段
        data_to_hash = news.get('title', '') + news.get('content', '')
        if not data_to_hash:
            # 如果没有标题和内容，使用整个记录的JSON字符串
            data_to_hash = json.dumps(news, sort_keys=True)
        
        # 生成MD5哈希
        return hashlib.md5(data_to_hash.encode('utf-8')).hexdigest()
    
    def get_raw_files_info(self):
        """获取raw目录下的文件信息"""
        if not os.path.exists(self.input_dir):
            logger.warning(f"输入目录 {self.input_dir} 不存在")
            return []
            
        # 获取raw目录下的所有文件（包括子目录）
        files = []
        
        # 递归扫描目录函数
        def scan_directory(directory):
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    # 如果是目录，递归扫描
                    scan_directory(item_path)
                elif os.path.isfile(item_path):
                    # 仅处理JSON和CSV文件
                    if item_path.endswith('.json') or item_path.endswith('.csv'):
                        mtime = os.path.getmtime(item_path)
                        size = os.path.getsize(item_path)
                        files.append({
                            'path': item_path,
                            'name': item,
                            'mtime': mtime,
                            'size': size,
                            'mtime_str': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                        })
        
        # 开始递归扫描
        scan_directory(self.input_dir)
        
        return files
    
    def has_new_raw_files(self):
        """检查raw目录是否有新文件或文件变化"""
        files_info = self.get_raw_files_info()
        
        if not files_info:
            logger.debug("raw目录中没有文件")
            return False
        
        # 检查文件是否有变化
        has_new = False
        for file_info in files_info:
            file_path = file_info['path']
            # 计算文件的指纹（使用修改时间和大小）
            file_fingerprint = f"{file_info['mtime']}_{file_info['size']}"
            
            # 如果文件不在记录中或者文件有变化
            if file_path not in self.processed_raw_files or self.processed_raw_files[file_path] != file_fingerprint:
                logger.info(f"检测到新文件或文件变化: {file_path} (修改时间: {file_info['mtime_str']}, 大小: {file_info['size']}字节)")
                has_new = True
                # 更新文件指纹
                self.processed_raw_files[file_path] = file_fingerprint
        
        # 保存raw文件状态
        if has_new:
            self.save_raw_files_state()
            
        return has_new
    
    def process_news_data(self, new_records):
        """使用main模块处理新闻数据"""
        if not MAIN_MODULE_AVAILABLE:
            logger.warning("main模块不可用，无法进行新闻分析")
            return False
        
        try:
            # 导入时已经尝试过导入process_news_data
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
            logger.info(f"开始使用main.process_news_data处理 {len(new_records)} 条记录...")
            process_news_data(new_records, output_dir)
            logger.info("新闻分析处理完成")
            return True
        except Exception as e:
            logger.error(f"调用process_news_data处理新闻时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def print_news_data_summary(self, news_data):
        """打印新闻数据摘要"""
        if not news_data:
            logger.info("新闻数据为空")
            return
            
        logger.info(f"新闻数据摘要 (共 {len(news_data)} 条):")
        for i, news in enumerate(news_data[:3]):  # 仅打印前3条
            title = news.get('title', '无标题')
            if len(title) > 30:
                title = title[:30] + "..."
            logger.info(f"  {i+1}. {title}")
        
        if len(news_data) > 3:
            logger.info(f"  ... 还有 {len(news_data) - 3} 条记录")
    
    def process_new_data(self, force_pipeline_run=False):
        """处理新的数据"""
        try:
            # 检查raw目录是否有新文件
            has_new_raw = self.has_new_raw_files()
            
            # 如果有新文件或强制运行
            if has_new_raw or force_pipeline_run:
                # 运行数据处理流水线（处理raw目录中的文件并更新news_data.json）
                logger.info("检测到raw目录有新数据或强制运行流水线，开始处理...")
                self.pipeline.run_pipeline()
            else:
                logger.debug("raw目录没有新数据，跳过处理流水线")
            
            # 不管raw目录是否有新数据，都检查news_data.json中是否有未处理的记录
            # 读取更新后的新闻数据
            if not os.path.exists(self.news_data_file):
                logger.warning(f"新闻数据文件 {self.news_data_file} 不存在")
                return
            
            with open(self.news_data_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            # 打印数据摘要
            self.print_news_data_summary(news_data)
            
            if not news_data:
                logger.info("没有新闻数据可处理")
                return
            
            # 筛选出新的记录
            new_records = []
            for news in news_data:
                record_id = self.generate_record_id(news)
                if record_id not in self.processed_records:
                    new_records.append(news)
                    # 将其标记为已处理
                    self.processed_records[record_id] = {
                        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "title": news.get('title', '无标题')
                    }
                    logger.info(f"找到新记录: {news.get('title', '无标题')[:30]}... (ID: {record_id[:8]})")
                else:
                    logger.debug(f"记录已处理过: {news.get('title', '无标题')[:30]}... (ID: {record_id[:8]})")
            
            # 保存已处理记录
            self.save_processed_records()
            
            # 如果有新记录，处理它们
            if new_records:
                logger.info(f"发现 {len(new_records)} 条新的新闻记录，开始处理...")
                # 调用main模块中的process_news_data处理新闻
                self.process_news_data(new_records)
            else:
                logger.info("没有新的新闻记录需要处理")
                
        except Exception as e:
            logger.error(f"处理新数据时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

class RawFileHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        super().__init__()
        self.watcher = watcher
        self.last_processed = 0
        # 设置一个合理的防抖时间（秒）
        self.debounce_seconds = 3
    
    def on_created(self, event):
        # 只处理文件创建事件
        if not event.is_directory and (event.src_path.endswith('.json') or event.src_path.endswith('.csv')):
            if event.src_path.startswith(self.watcher.input_dir):
                self._handle_event(event)
    
    def on_modified(self, event):
        # 只处理文件修改事件
        if not event.is_directory and (event.src_path.endswith('.json') or event.src_path.endswith('.csv')):
            if event.src_path.startswith(self.watcher.input_dir):
                self._handle_event(event)
            
    def _handle_event(self, event):
        current_time = time.time()
        # 防抖：确保在短时间内多次触发事件只处理一次
        if current_time - self.last_processed > self.debounce_seconds:
            logger.info(f"检测到raw目录文件变化: {event.src_path}")
            self.last_processed = current_time
            # 强制运行流水线处理
            self.watcher.process_new_data(force_pipeline_run=True)

class NewsDataFileHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        super().__init__()
        self.watcher = watcher
        self.last_processed = 0
        # 设置一个合理的防抖时间（秒）
        self.debounce_seconds = 2
    
    def on_modified(self, event):
        # 只处理目标文件的修改事件
        if not event.is_directory and event.src_path.endswith(self.watcher.news_data_file):
            current_time = time.time()
            # 防抖：确保在短时间内多次触发事件只处理一次
            if current_time - self.last_processed > self.debounce_seconds:
                logger.info(f"检测到新闻数据文件变化: {event.src_path}")
                self.last_processed = current_time
                # 由于文件变化可能是由pipeline引起的，我们不强制运行流水线
                self.watcher.process_new_data(force_pipeline_run=False)

def main():
    # 创建实例并传入配置文件路径
    config_file = "config.json"
    watcher = NewsWatcher(config_file)
    
    # 首次运行，处理现有数据
    logger.info("首次运行，处理现有数据...")
    watcher.process_new_data(force_pipeline_run=True)
    
    # 设置文件系统监视器：监控raw目录
    logger.info(f"开始监视raw目录 {watcher.input_dir} 的变化...")
    raw_event_handler = RawFileHandler(watcher)
    raw_observer = Observer()
    raw_observer.schedule(raw_event_handler, path=watcher.input_dir, recursive=True)
    raw_observer.start()
    
    # 设置文件系统监视器：监控news_data.json文件
    logger.info(f"开始监视文件 {watcher.news_data_file} 的变化...")
    news_data_event_handler = NewsDataFileHandler(watcher)
    news_data_observer = Observer()
    news_data_observer.schedule(news_data_event_handler, path=os.path.dirname(watcher.news_data_file), recursive=False)
    news_data_observer.start()
    
    try:
        while True:
            # 每隔一段时间主动检查一次（作为备选机制）
            time.sleep(watcher.check_interval)  # 使用配置的检查间隔
            watcher.process_new_data()
    except KeyboardInterrupt:
        raw_observer.stop()
        news_data_observer.stop()
    
    raw_observer.join()
    news_data_observer.join()

if __name__ == "__main__":
    main() 