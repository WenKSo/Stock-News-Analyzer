import os
import json
#import tushare as ts
import sys
from volcenginesdkarkruntime import Ark

# 获取当前文件的绝对路径，然后获取其上一级目录（项目根目录）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置 Tushare API
# ts.set_token('your_tushare_token')
# pro = ts.pro_api()

# 配置 DeepSeek
from config.config import ARK_API_KEY

client = Ark(
    api_key=ARK_API_KEY,
    timeout=1800,
)

def analyze_news(news_text):
    response = client.chat.completions.create(
        model="deepseek-r1-distill-qwen-32b-250120",
        messages=[
            {"role": "user", "content": f"分析以下新闻内容，并提取与之最相关的股票代码（最多3个）,注意只需要输出3个股票代码：{news_text}"}
        ]
    )
    if hasattr(response.choices[0].message, 'reasoning_content'):
        print(response.choices[0].message.reasoning_content)
    return response.choices[0].message.content

# def get_stock_data(stock_code):
#     # 获取股票基本信息
#     stock_info = pro.daily(ts_code=stock_code)
#     # 获取股票基本面数据
#     stock_basic = pro.stock_basic(ts_code=stock_code)
#     return stock_info, stock_basic

def analyze_stock(news_text, stock_data):
    response = client.chat.completions.create(
        model="deepseek-r1-distill-qwen-32b-250120",
        messages=[
            {"role": "user", "content": f"根据以下新闻内容和股票数据，分析是否应该入手该股票：\n新闻内容：{news_text}\n股票数据：{stock_data}"}
        ]
    )
    if hasattr(response.choices[0].message, 'reasoning_content'):
        print(response.choices[0].message.reasoning_content)
    return response.choices[0].message.content

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(__file__)
    # 构造 data 目录下的 JSON 文件路径
    json_path = os.path.join(current_dir, '..', 'data', 'news_data.json')

    # 假设你已经使用八爪鱼爬虫爬取了新闻数据，并保存为 news_data.json
    with open(json_path, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    for news in news_data:
        news_text = news['content']
        # 分析新闻并提取相关股票代码
        stock_codes = analyze_news(news_text)
        print(f"相关股票代码：{stock_codes}")
        
            # for stock_code in stock_codes.split(','):
            #     # 获取股票数据
            #     stock_info, stock_basic = get_stock_data(stock_code.strip())
            #     # 综合分析
            #     analysis_result = analyze_stock(news_text, {'info': stock_info, 'basic': stock_basic})
            #     print(f"股票代码：{stock_code}\n分析结果：{analysis_result}")

if __name__ == "__main__":
    main()