# src/main.py
import os
import pandas as pd
from fetch_news import load_news
from analyze_news import extract_stock_codes
from fetch_stock import get_stock_data
from decision import decide_trade

def main():
    # 加载新闻数据
    news_file = os.path.join("data", "raw_news", "news_data.json")
    news = load_news(news_file)
    news_text = news.get("content", "")
    
    if not news_text:
        print("新闻内容为空，请检查数据文件。")
        return

    # 使用 Doubao API 分析新闻，提取股票代码
    stock_codes = extract_stock_codes(news_text)
    print("提取到的股票代码：", stock_codes)
    
    # 遍历股票代码，从 Tushare 获取数据
    stock_data_list = []
    for code in stock_codes:
        data = get_stock_data(code)
        if not data.empty:
            stock_data_list.append(data)
        else:
            print(f"未找到股票 {code} 的数据")
    
    if stock_data_list:
        all_stock_data = pd.concat(stock_data_list, ignore_index=True)
        # 这里假设新闻情绪为“积极”，实际中可从 API 结果解析得到
        sentiment = "积极"
        decision = decide_trade(sentiment, all_stock_data)
        print("交易建议：", decision)
    else:
        print("没有获取到有效的股票数据。")

if __name__ == "__main__":
    main()