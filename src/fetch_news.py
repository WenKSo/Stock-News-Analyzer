# src/fetch_news.py
import json

def load_news(file_path):
    """
    从 JSON 文件中加载新闻数据
    """
    with open(file_path, "r", encoding="utf8") as f:
        news = json.load(f)
    return news

if __name__ == "__main__":
    news = load_news("data/raw_news/news_data.json")
    print("新闻标题：", news.get("title"))
    print("新闻内容：", news.get("content"))
