import os
import json
import pandas as pd
from data_processor import NewsDataProcessor

def test_text_cleaning():
    """测试文本清洗功能"""
    print("开始测试文本清洗功能...")
    
    # 创建测试数据
    test_data = [
        {
            "title": "测试标题 <b>加粗</b>",
            "content": "ct_hqimg {margin: 10px 0;} .hqimg_wrapper {text-align: center;} 这是一个<div class='test'>测试</div>内容，\t\n包含HTML标签和CSS样式。"
        },
        {
            "title": "另一个测试标题",
            "content": "<p style='color:red;'>这是红色文本</p>\n\n<script>alert('测试');</script>这是正常内容。"
        }
    ]
    
    # 保存测试数据
    os.makedirs("test_data", exist_ok=True)
    with open("test_data/test_news.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=4)
    
    # 创建处理器
    processor = NewsDataProcessor("test_data", "test_data/output", "test_data/archive")
    
    # 加载测试数据
    df = pd.DataFrame(test_data)
    
    # 清理数据
    cleaned_df = processor.clean_news_data(df)
    
    # 显示清理前后的对比
    print("\n=== 清理前 ===")
    for i, row in df.iterrows():
        print(f"标题 {i+1}: {row['title']}")
        print(f"内容 {i+1}: {row['content'][:100]}...\n")
    
    print("\n=== 清理后 ===")
    for i, row in cleaned_df.iterrows():
        print(f"标题 {i+1}: {row['title']}")
        print(f"内容 {i+1}: {row['content'][:100]}...\n")
    
    # 测试单独的文本清理函数
    print("\n=== 测试更多样例 ===")
    test_cases = [
        "ct_hqimg {margin: 10px 0;} .hqimg_wrapper {text-align: center;} 实际内容",
        "<div class='news-content'>这是新闻内容</div>",
        "这是正常文本\t\n但包含制表符和换行符",
        "图片来源：网络 这是一篇文章",
        "这是一篇文章 责任编辑：张三",
        "https://example.com 这是包含URL的文本"
    ]
    
    for i, test_case in enumerate(test_cases):
        cleaned = processor.clean_text(test_case)
        print(f"样例 {i+1}:")
        print(f"原文: {test_case}")
        print(f"清理后: {cleaned}\n")
    
    print("文本清洗测试完成！")

if __name__ == "__main__":
    test_text_cleaning() 