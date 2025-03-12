import os
import json
import time
import logging
import schedule
from datetime import datetime
from data_processor import NewsDataProcessor
from data_integrator import NewsDataIntegrator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NewsDataPipeline")

class NewsDataPipeline:
    def __init__(self, config_file="config.json"):
        """
        初始化数据处理流水线
        
        参数:
        config_file: 配置文件路径
        """
        logger.info(f"正在加载配置文件: {config_file}")
        self.config = self._load_config(config_file)
        
        # 确保配置中包含所有必要的键
        self._ensure_config_keys()
        
        self.input_dir = self.config["data_paths"]["input_dir"]
        self.output_dir = self.config["data_paths"]["output_dir"]
        self.archive_dir = self.config["data_paths"]["archive_dir"]
        self.interval_minutes = self.config["processing"]["interval_minutes"]
        self.run_continuously = self.config["processing"]["run_continuously"]
        
        # 确保所有目录存在
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
        
        logger.info(f"初始化数据处理器和集成器")
        # 初始化处理器和集成器
        self.processor = NewsDataProcessor(self.input_dir, self.output_dir, self.archive_dir)
        self.integrator = NewsDataIntegrator(config_file)
    
    def _ensure_config_keys(self):
        """确保配置中包含所有必要的键"""
        # 检查并设置默认值
        if "data_paths" not in self.config:
            self.config["data_paths"] = {}
        
        if "input_dir" not in self.config["data_paths"]:
            self.config["data_paths"]["input_dir"] = "data/raw"
            
        if "output_dir" not in self.config["data_paths"]:
            self.config["data_paths"]["output_dir"] = "data/processed"
            
        if "archive_dir" not in self.config["data_paths"]:
            self.config["data_paths"]["archive_dir"] = "data/archive"
            
        if "processing" not in self.config:
            self.config["processing"] = {}
            
        if "interval_minutes" not in self.config["processing"]:
            self.config["processing"]["interval_minutes"] = 10
            
        if "run_continuously" not in self.config["processing"]:
            self.config["processing"]["run_continuously"] = False
            
        if "integration" not in self.config:
            self.config["integration"] = {}
            
        if "target_db_file" not in self.config["integration"]:
            self.config["integration"]["target_db_file"] = "news_database.db"
            
        if "table_name" not in self.config["integration"]:
            self.config["integration"]["table_name"] = "news_articles"
    
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
                "interval_minutes": 10,
                "run_continuously": False
            },
            "integration": {
                "target_db_file": "news_database.db",
                "table_name": "news_articles"
            },
            "data_cleaning": {
                "remove_duplicates": True,
                "drop_empty_content": True,
                "required_fields": ["title", "content", "publish_time", "source"]
            }
        }
    
    def run_pipeline(self):
        """运行完整的数据处理流水线"""
        logger.info("开始运行数据处理流水线...")
        
        try:
            # 步骤1: 处理新数据
            logger.info("步骤1: 处理新数据")
            self.processor.process()
            
            # 步骤2: 将处理后的数据集成到数据库
            logger.info("步骤2: 将处理后的数据集成到数据库")
            self.integrator.integrate()
            
            # 步骤3: 导出为JSON文件，用于现有系统
            logger.info("步骤3: 导出为JSON文件，用于现有系统")
            json_output_file = self.config.get("output_json_file", "data/news_data.json")
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(json_output_file), exist_ok=True)
            
            records_exported = self.integrator.export_to_json(json_output_file)
            if records_exported > 0:
                logger.info(f"已将 {records_exported} 条记录导出到 {json_output_file}")
            
            logger.info("数据处理流水线运行完成")
        except Exception as e:
            logger.error(f"运行数据处理流水线时出错: {str(e)}")
    
    def start(self):
        """启动数据处理流水线"""
        logger.info(f"数据处理流水线启动，间隔时间: {self.interval_minutes} 分钟")
        
        # 立即运行一次
        self.run_pipeline()
        
        if self.run_continuously:
            # 设置定时任务
            schedule.every(self.interval_minutes).minutes.do(self.run_pipeline)
            
            # 持续运行
            while True:
                schedule.run_pending()
                time.sleep(1)

def main():
    pipeline = NewsDataPipeline()
    pipeline.start()

if __name__ == "__main__":
    main() 