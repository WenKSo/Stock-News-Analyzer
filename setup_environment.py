import os
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Setup")

def setup_environment():
    """设置必要的目录结构和初始环境"""
    logger.info("开始设置环境...")
    
    # 加载配置文件
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        logger.warning(f"配置文件 {config_file} 不存在，使用默认配置")
        config = {
            "data_paths": {
                "input_dir": "data/raw",
                "output_dir": "data/processed",
                "archive_dir": "data/archive"
            },
            "integration": {
                "target_db_file": "news_database.db"
            }
        }
    
    # 创建数据目录
    dirs_to_create = [
        config["data_paths"]["input_dir"],
        config["data_paths"]["output_dir"],
        config["data_paths"]["archive_dir"],
        "data/imported"  # 导入完成的数据目录
    ]
    
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"已创建目录: {dir_path}")
    
    # 创建示例数据文件（可选）
    create_example_data = input("是否创建示例数据文件？(y/n): ").lower() == 'y'
    if create_example_data:
        create_example_data_files(config["data_paths"]["input_dir"])
    
    logger.info("环境设置完成！")
    logger.info(f"请将八爪鱼采集器的输出目录设置为: {os.path.abspath(config['data_paths']['input_dir'])}")
    logger.info("然后运行 python news_data_pipeline.py 开始处理数据")

def create_example_data_files(input_dir):
    """创建示例数据文件"""
    logger.info("创建示例数据文件...")
    
    # 示例JSON数据
    example_json_data = [
        {
            "title": "示例新闻标题1",
            "content": "这是示例新闻内容1，用于测试数据处理流程。",
            "publish_time": "2023-07-01 08:30:00",
            "source": "示例新闻源1",
            "url": "https://example.com/news/1"
        },
        {
            "title": "示例新闻标题2",
            "content": "这是示例新闻内容2，用于测试数据处理流程。",
            "publish_time": "2023-07-01 09:15:00",
            "source": "示例新闻源2",
            "url": "https://example.com/news/2"
        }
    ]
    
    # 保存JSON示例数据
    json_file_path = os.path.join(input_dir, "example_news_data.json")
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(example_json_data, f, ensure_ascii=False, indent=4)
    logger.info(f"已创建示例JSON数据文件: {json_file_path}")
    
    # 示例CSV数据
    csv_file_path = os.path.join(input_dir, "example_news_data.csv")
    with open(csv_file_path, 'w', encoding='utf-8') as f:
        f.write("title,content,publish_time,source,url\n")
        f.write("示例CSV新闻标题1,这是示例CSV新闻内容1，用于测试数据处理流程。,2023-07-01 10:30:00,示例CSV新闻源1,https://example.com/news/csv/1\n")
        f.write("示例CSV新闻标题2,这是示例CSV新闻内容2，用于测试数据处理流程。,2023-07-01 11:15:00,示例CSV新闻源2,https://example.com/news/csv/2\n")
    logger.info(f"已创建示例CSV数据文件: {csv_file_path}")

if __name__ == "__main__":
    setup_environment() 