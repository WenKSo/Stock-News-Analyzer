import requests
from config.config import DOUBAO_API_URL, DOUBAO_API_KEY

def extract_stock_codes(news_text):
    """
    调用 Doubao-1.5-lite API 分析新闻内容，提取相关股票代码
    返回股票代码列表，代码间以逗号分隔。
    """
    headers = {
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "doubao-1.5-lite",
        "messages": [
            {
                "role": "system",
                "content": "你是一个财经分析助手，请根据下面的新闻内容提取相关股票代码，仅返回股票代码，逗号分隔。"
            },
            {
                "role": "user",
                "content": news_text
            }
        ],
        "stream": False
    }
    response = requests.post(DOUBAO_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        # 假设返回的内容在 choices[0].message.content 中为逗号分隔的股票代码
        stock_codes_str = result["choices"][0]["message"]["content"]
        stock_codes = [code.strip() for code in stock_codes_str.split(",") if code.strip()]
        return stock_codes
    else:
        print("Doubao API 请求失败：", response.text)
        return []

if __name__ == "__main__":
    test_text = "示例新闻内容，涉及股票代码：600519, 000858。"
    codes = extract_stock_codes(test_text)
    print("提取到的股票代码：", codes)
