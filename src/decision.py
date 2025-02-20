import pandas as pd

def decide_trade(sentiment, stock_data_df):
    """
    根据新闻情绪和股票基本面数据给出交易决策。
    示例规则：如果情绪为“积极”，且股票的市盈率（pe_ttm）低于20且净利润同比增长（netprofit_yoy）为正，
    则建议“买入”；否则建议“观望”。
    """
    decision = {}
    for ts_code in stock_data_df["ts_code"].unique():
        stock_info = stock_data_df[stock_data_df["ts_code"] == ts_code]
        pe = stock_info["pe_ttm"].iloc[0] if "pe_ttm" in stock_info.columns else None
        growth = stock_info["netprofit_yoy"].iloc[0] if "netprofit_yoy" in stock_info.columns else None
        if sentiment == "积极" and pe is not None and growth is not None:
            decision[ts_code] = "买入" if pe < 20 and growth > 0 else "观望"
        else:
            decision[ts_code] = "观望"
    return decision

if __name__ == "__main__":
    # 使用示例数据测试决策模块
    data = pd.DataFrame({
        "ts_code": ["600519.SH", "000858.SZ"],
        "pe_ttm": [15, 25],
        "netprofit_yoy": [5, -2]
    })
    result = decide_trade("积极", data)
    print("交易建议：", result)
