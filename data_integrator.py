import os
import json
import pandas as pd
import sqlite3
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_integrator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NewsDataIntegrator")

class NewsDataIntegrator:
    def __init__(self, config_file="config.json"):
        """
        初始化数据集成器
        
        参数:
        config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.processed_dir = self.config["data_paths"]["output_dir"]
        self.db_file = self.config["integration"]["target_db_file"]
        self.table_name = self.config["integration"]["table_name"]
        
        # 确保目录存在
        db_dir = os.path.dirname(self.db_file)
        if db_dir:  # 只有当数据库文件包含目录路径时才创建目录
            os.makedirs(db_dir, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
    
    def _load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置文件时出错: {str(e)}")
            # 返回默认配置
            return {
                "data_paths": {
                    "output_dir": "data/processed"
                },
                "integration": {
                    "target_db_file": "news_database.db",
                    "table_name": "news_articles"
                }
            }
    
    def _init_database(self):
        """初始化数据库和表"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 创建新闻文章表
            cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                publish_time TIMESTAMP,
                source TEXT,
                url TEXT,
                processed_at TIMESTAMP,
                imported_at TIMESTAMP
            )
            ''')
            
            # 创建索引
            cursor.execute(f'''
            CREATE INDEX IF NOT EXISTS idx_title ON {self.table_name} (title)
            ''')
            cursor.execute(f'''
            CREATE INDEX IF NOT EXISTS idx_publish_time ON {self.table_name} (publish_time)
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"数据库初始化完成: {self.db_file}")
        except Exception as e:
            logger.error(f"初始化数据库时出错: {str(e)}")
    
    def get_processed_files(self):
        """获取处理后的数据文件"""
        files = []
        for filename in os.listdir(self.processed_dir):
            if filename.endswith('.csv'):
                files.append(os.path.join(self.processed_dir, filename))
        return files
    
    def import_to_database(self, file_path):
        """
        将处理后的数据导入到数据库
        
        参数:
        file_path: 处理后的数据文件路径
        
        返回:
        导入的记录数
        """
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding='utf-8')
            if df.empty:
                logger.warning(f"文件 {file_path} 没有数据，跳过导入")
                return 0
            
            # 添加导入时间戳
            df['imported_at'] = datetime.now()
            
            # 连接数据库
            conn = sqlite3.connect(self.db_file)
            
            # 导入数据
            records_count = len(df)
            df.to_sql(self.table_name, conn, if_exists='append', index=False)
            
            conn.close()
            logger.info(f"已将 {records_count} 条记录从 {file_path} 导入到数据库")
            return records_count
        except Exception as e:
            logger.error(f"导入数据到数据库时出错: {str(e)}")
            return 0
    
    def move_imported_file(self, file_path, imported_dir="data/imported"):
        """
        移动已导入的文件到导入完成目录
        
        参数:
        file_path: 已导入的文件路径
        imported_dir: 导入完成目录
        """
        try:
            os.makedirs(imported_dir, exist_ok=True)
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_path = os.path.join(imported_dir, f"{timestamp}_{filename}")
            os.rename(file_path, new_path)
            logger.info(f"已移动导入完成的文件 {file_path} 到 {new_path}")
        except Exception as e:
            logger.error(f"移动已导入文件时出错: {str(e)}")
    
    def export_to_json(self, output_file="news_data.json", limit=None):
        """
        将数据库中的新闻数据导出为JSON文件
        
        参数:
        output_file: 输出的JSON文件路径
        limit: 限制导出的记录数，None表示导出所有记录
        
        返回:
        导出的记录数
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # 连接数据库
            conn = sqlite3.connect(self.db_file)
            
            # 构建查询
            query = f"SELECT * FROM {self.table_name} ORDER BY publish_time DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            # 读取数据
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                logger.warning(f"没有数据可导出")
                return 0
            
            # 转换日期时间列为字符串格式
            for col in df.columns:
                if 'time' in col.lower() or 'date' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
            
            # 转换为字典列表
            records = df.to_dict(orient='records')
            
            # 保存为JSON文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=4)
            
            logger.info(f"已将 {len(records)} 条记录导出到 {output_file}")
            return len(records)
        except Exception as e:
            logger.error(f"导出数据到JSON文件时出错: {str(e)}")
            return 0
    
    def integrate(self):
        """集成所有处理后的数据到数据库"""
        files = self.get_processed_files()
        if not files:
            logger.info("没有新的处理后文件需要导入")
            return
        
        logger.info(f"发现 {len(files)} 个处理后文件需要导入")
        total_records = 0
        
        for file_path in files:
            logger.info(f"正在导入文件: {file_path}")
            records = self.import_to_database(file_path)
            total_records += records
            
            if records > 0:
                self.move_imported_file(file_path)
        
        logger.info(f"数据集成完成，共导入 {total_records} 条记录")
        
        # 导入完成后，自动导出为JSON文件
        if total_records > 0:
            self.export_to_json()

def main():
    integrator = NewsDataIntegrator()
    integrator.integrate()
    
    # 如果需要单独导出JSON文件
    # integrator.export_to_json()
    
    # 如果需要定期运行，可以取消下面的注释
    # while True:
    #     integrator.integrate()
    #     logger.info("等待下一次集成...")
    #     time.sleep(600)  # 每10分钟运行一次

if __name__ == "__main__":
    main() 