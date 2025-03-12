import os
import json
import pandas as pd
import time
from datetime import datetime
import logging
import re
import html
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NewsDataProcessor")

class NewsDataProcessor:
    def __init__(self, input_dir, output_dir, archive_dir=None):
        """
        初始化数据处理器
        
        参数:
        input_dir: 八爪鱼采集器输出数据的目录
        output_dir: 处理后数据的输出目录
        archive_dir: 处理完成后原始数据的归档目录
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.archive_dir = archive_dir
        
        # 确保目录存在
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        if archive_dir:
            os.makedirs(archive_dir, exist_ok=True)
    
    def get_new_files(self):
        """获取输入目录中尚未处理的新文件"""
        files = []
        for filename in os.listdir(self.input_dir):
            if filename.endswith('.json') or filename.endswith('.csv'):
                files.append(os.path.join(self.input_dir, filename))
        return files
    
    def clean_text(self, text):
        """
        清理文本内容，去除HTML标签、CSS样式和多余的空白字符
        
        参数:
        text: 需要清理的文本
        
        返回:
        清理后的文本
        """
        if not isinstance(text, str):
            return text
        
        # 先处理一些常见的CSS样式定义，完全移除它们
        css_patterns = [
            r'ct_hqimg\s*\{[^\}]*\}',
            r'\.hqimg_wrapper\s*\{[^\}]*\}',
            r'[a-zA-Z0-9_\-\.]+\s*\{[^\}]*\}',  # 通用CSS规则
            r'<style[^>]*>.*?</style>'  # 样式标签
        ]
        
        for pattern in css_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL)
            
        # 解码HTML实体
        text = html.unescape(text)
        
        # 使用BeautifulSoup去除HTML标签
        try:
            # 只有当文本看起来像HTML时才使用BeautifulSoup
            if '<' in text and '>' in text:
                soup = BeautifulSoup(text, 'html.parser')
                text = soup.get_text()
        except:
            # 如果BeautifulSoup处理失败，使用正则表达式去除HTML标签
            text = re.sub(r'<[^>]+>', ' ', text)
        
        # 去除常见的CSS类名和ID
        text = re.sub(r'(class|id|style)=["\'][^"\']+["\']', ' ', text)
        
        # 去除JavaScript代码
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.DOTALL)
        
        # 去除可能的URL
        text = re.sub(r'https?://\S+', '', text)
        
        # 去除常见的无意义文本
        patterns_to_remove = [
            r'图片来源：.*?网络',
            r'来源：.*?网',
            r'编辑：.*?[\s,，。；;]',
            r'记者：.*?[\s,，。；;]',
            r'责任编辑：.*?[\s,，。；;]',
            r'作者：.*?[\s,，。；;]',
            r'发布时间：.*?[\s,，。；;]',
            r'更新时间：.*?[\s,，。；;]'
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text)
        
        # 去除多余的空白字符（空格、制表符、换行符等）
        text = re.sub(r'\s+', ' ', text)
        
        # 去除特殊控制字符
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)
        
        # 最终修剪
        text = text.strip()
        
        return text
    
    def clean_news_data(self, df):
        """
        清理新闻数据
        
        参数:
        df: 包含新闻数据的DataFrame
        
        返回:
        清理后的DataFrame
        """
        # 根据实际数据结构调整以下清理步骤
        if df.empty:
            return df
            
        # 1. 删除重复行
        df = df.drop_duplicates()
        
        # 2. 处理缺失值
        # 根据具体情况填充或删除缺失值
        df = df.dropna(subset=['title', 'content'])  # 删除标题或内容为空的行
        
        # 3. 格式化日期时间字段
        if 'publish_time' in df.columns:
            try:
                df['publish_time'] = pd.to_datetime(df['publish_time'])
            except:
                logger.warning("无法转换publish_time字段为日期时间格式")
        
        # 4. 文本清理
        if 'title' in df.columns:
            df['title'] = df['title'].apply(lambda x: self.clean_text(x))
            # 删除清理后标题为空的行
            df = df[df['title'].str.strip() != '']
            
        if 'content' in df.columns:
            df['content'] = df['content'].apply(lambda x: self.clean_text(x))
            # 删除清理后内容为空的行
            df = df[df['content'].str.strip() != '']
            
        # 5. 添加处理时间戳
        df['processed_at'] = datetime.now()
        
        # 6. 删除内容过短的行（可能是无效内容）
        if 'content' in df.columns:
            df = df[df['content'].str.len() > 20]  # 内容至少20个字符
            
        # 7. 删除标题过短的行
        if 'title' in df.columns:
            df = df[df['title'].str.len() > 5]  # 标题至少5个字符
        
        return df
    
    def load_file(self, file_path):
        """
        加载数据文件
        
        参数:
        file_path: 文件路径
        
        返回:
        DataFrame对象
        """
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return pd.DataFrame(data)
                else:
                    return pd.DataFrame([data])
            elif file_path.endswith('.csv'):
                return pd.read_csv(file_path, encoding='utf-8')
            else:
                logger.error(f"不支持的文件格式: {file_path}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"加载文件 {file_path} 时出错: {str(e)}")
            return pd.DataFrame()
    
    def save_processed_data(self, df, original_filename):
        """
        保存处理后的数据
        
        参数:
        df: 处理后的DataFrame
        original_filename: 原始文件名
        """
        if df.empty:
            logger.warning(f"没有数据可保存，跳过 {original_filename}")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(original_filename))[0]
        output_file = os.path.join(self.output_dir, f"{base_name}_processed_{timestamp}.csv")
        
        try:
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"已保存处理后的数据到 {output_file}")
        except Exception as e:
            logger.error(f"保存处理后的数据时出错: {str(e)}")
    
    def archive_file(self, file_path):
        """
        归档已处理的文件
        
        参数:
        file_path: 要归档的文件路径
        """
        if not self.archive_dir:
            return
            
        try:
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = os.path.join(self.archive_dir, f"{timestamp}_{filename}")
            os.rename(file_path, archive_path)
            logger.info(f"已归档文件 {file_path} 到 {archive_path}")
        except Exception as e:
            logger.error(f"归档文件 {file_path} 时出错: {str(e)}")
    
    def process(self):
        """处理所有新文件"""
        files = self.get_new_files()
        if not files:
            logger.info("没有新文件需要处理")
            return
            
        logger.info(f"发现 {len(files)} 个新文件需要处理")
        
        for file_path in files:
            logger.info(f"正在处理文件: {file_path}")
            
            # 加载数据
            df = self.load_file(file_path)
            if df.empty:
                logger.warning(f"文件 {file_path} 没有有效数据，跳过")
                continue
                
            # 清理数据
            cleaned_df = self.clean_news_data(df)
            
            # 保存处理后的数据
            self.save_processed_data(cleaned_df, file_path)
            
            # 归档原始文件
            self.archive_file(file_path)
            
        logger.info("所有文件处理完成")

def main():
    # 配置目录
    input_dir = "data/raw"  # 八爪鱼采集器输出数据的目录
    output_dir = "data/processed"  # 处理后数据的输出目录
    archive_dir = "data/archive"  # 处理完成后原始数据的归档目录
    
    processor = NewsDataProcessor(input_dir, output_dir, archive_dir)
    
    # 运行一次处理
    processor.process()
    
    # 如果需要定期运行，可以取消下面的注释
    # while True:
    #     processor.process()
    #     logger.info("等待下一次处理...")
    #     time.sleep(600)  # 每10分钟运行一次

if __name__ == "__main__":
    main() 