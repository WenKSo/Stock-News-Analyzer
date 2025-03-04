import os
import sys
from volcenginesdkarkruntime import Ark
import akshare as ak

# 获取当前文件的绝对路径，然后获取其上一级目录（项目根目录）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从config导入常量
from config.config import ARK_API_KEY

# 配置 DeepSeek
client = Ark(
    api_key=ARK_API_KEY,
    timeout=1800,
)

def analyze_news(news_text):
    """
    分析新闻内容，提取相关的股票代码
    确保只返回已上市的A股股票代码
    """
    prompt = f"""
    分析以下新闻内容，并提取与之最相关的股票代码。
    
    要求：
    1. 只提取已经在A股上市的公司股票代码
    2. 不要提取未上市公司（如华为、字节跳动等）
    3. 如果新闻中没有明确提到已上市公司，请回复"无相关上市公司"
    4. 你的回答只需要输出1个股票代码，不要参杂其他内容
    5. 股票代码格式为6位数字，如"600519"或"000001"
    
    新闻内容：{news_text}
    """
    
    response = client.chat.completions.create(
        model="deepseek-r1-distill-qwen-32b-250120",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    if hasattr(response.choices[0].message, 'reasoning_content'):
        print(response.choices[0].message.reasoning_content)
    
    # 获取AI返回的股票代码
    stock_code = response.choices[0].message.content.strip()
    
    # 验证返回的是否为有效的股票代码
    if stock_code == "无相关上市公司":
        return stock_code
    
    # 尝试验证股票代码是否为已上市股票
    try:
        # 获取所有A股股票列表
        stock_list = ak.stock_zh_a_spot_em()
        # 检查返回的股票代码是否在列表中
        if stock_code in stock_list['代码'].values:
            print(f"验证通过：{stock_code} 是已上市的A股股票")
            return stock_code
        else:
            # 如果不在列表中，尝试添加市场后缀
            if stock_code.startswith(('0', '3')):
                formatted_code = f"{stock_code}.SZ"
            elif stock_code.startswith(('6', '9')):
                formatted_code = f"{stock_code}.SH"
            else:
                formatted_code = stock_code
            print(f"股票代码 {stock_code} 不在A股列表中，转换为 {formatted_code}")
            return formatted_code
    except Exception as e:
        print(f"验证股票代码时出错: {e}")
        # 如果验证过程出错，仍然返回原始代码，但在后续处理中会再次验证
        return stock_code 