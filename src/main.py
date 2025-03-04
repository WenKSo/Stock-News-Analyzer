import os
import json
import sys
import webbrowser
from datetime import datetime

# 获取当前文件的绝对路径，然后获取其上一级目录（项目根目录）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入自定义模块
from news_analyzer import analyze_news
from stock_data import get_stock_data
from stock_analyzer import analyze_stock
from visualization import visualize_stock_data, generate_index_page

def process_news_data(news_data, output_dir='../output'):
    """处理新闻数据并生成分析报告"""
    # 创建结果列表
    results = []
    
    for i, news in enumerate(news_data):
        print(f"\n处理第 {i+1} 条新闻...")
        news_text = news['content']
        print(f"新闻内容: {news_text[:100]}...")  # 只打印前100个字符
        
        # 分析新闻并提取相关股票代码
        print("开始分析新闻并提取股票代码...")
        stock_codes = analyze_news(news_text)
        print(f"相关股票代码：{stock_codes}")
        
        # 处理无相关上市公司的情况
        if stock_codes == "无相关上市公司":
            print("该新闻没有相关的已上市公司，跳过分析")
            continue
        
        for stock_code in stock_codes.split(','):
            stock_code = stock_code.strip()
            if not stock_code:
                continue
            
            print(f"\n开始获取股票 {stock_code} 的数据...")
            # 获取股票数据
            stock_data = get_stock_data(stock_code)
            
            if not stock_data or not stock_data.get('basic', {}).get('name', ''):
                print(f"未能获取到股票 {stock_code} 的有效数据，跳过分析")
                continue
            
            print(f"开始分析股票 {stock_code}...")
            # 综合分析
            analysis_result = analyze_stock(news_text, stock_data)
            print(f"股票代码：{stock_code}\n分析结果：{analysis_result}")
            
            # 生成可视化报告
            report_file = visualize_stock_data(stock_data, news_text, analysis_result, output_dir)
            results.append({
                'news_index': i,
                'stock_code': stock_code,
                'stock_name': stock_data['basic']['name'],
                'report_file': report_file
            })
    
    # 生成索引页面
    if results:
        index_file = generate_index_page(results, output_dir)
        
        # 尝试自动打开索引页面
        try:
            webbrowser.open(f"file://{os.path.abspath(index_file)}")
            print("已自动打开报告索引页")
        except:
            print(f"请手动打开报告索引页: {index_file}")
    
    return results

def main():
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(__file__)
        # 构造 data 目录下的 JSON 文件路径
        json_path = os.path.join(current_dir, '..', 'data', 'news_data.json')
        # 构造输出目录
        output_dir = os.path.join(current_dir, '..', 'output')
        
        print(f"尝试读取新闻数据文件: {json_path}")
        
        # 假设你已经使用八爪鱼爬虫爬取了新闻数据，并保存为 news_data.json
        with open(json_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        print(f"成功读取新闻数据，共 {len(news_data)} 条")
        
        # 处理新闻数据
        process_news_data(news_data, output_dir)
        
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()