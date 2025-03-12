import os
import json
import argparse
import logging
from data_integrator import NewsDataIntegrator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ExportJSON")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='从数据库导出新闻数据为JSON文件')
    parser.add_argument('--output', '-o', default='data/news_data.json', help='输出的JSON文件路径')
    parser.add_argument('--limit', '-l', type=int, default=None, help='限制导出的记录数')
    parser.add_argument('--config', '-c', default='config.json', help='配置文件路径')
    args = parser.parse_args()
    
    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 初始化数据集成器
    integrator = NewsDataIntegrator(args.config)
    
    # 导出JSON文件
    records_exported = integrator.export_to_json(args.output, args.limit)
    
    if records_exported > 0:
        logger.info(f"成功导出 {records_exported} 条记录到 {args.output}")
    else:
        logger.warning(f"没有记录被导出")

if __name__ == "__main__":
    main() 