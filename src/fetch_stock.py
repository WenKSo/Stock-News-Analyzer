import tushare as ts
from config.config import TUSHARE_TOKEN

# 配置 tushare
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

def get_stock_data(ts_code, trade_date="20250220"):
    """
    调用 Tushare API 获取指定股票代码在特定日期的基本面数据。
    这里以 fina_indicator 接口为例，实际可根据需要调整接口和字段。
    """
    df = pro.query("fina_indicator", ts_code=ts_code, start_date=trade_date, end_date=trade_date)
    return df

if __name__ == "__main__":
    sample_code = "600519.SH"  # 示例股票代码，请根据实际情况调整
    data = get_stock_data(sample_code)
    print(data.head())
