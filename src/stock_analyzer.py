import os
import sys

# 获取当前文件的绝对路径，然后获取其上一级目录（项目根目录）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从config导入常量
from config.config import ARK_API_KEY
from volcenginesdkarkruntime import Ark

# 配置 DeepSeek
client = Ark(
    api_key=ARK_API_KEY,
    timeout=1800,
)

def analyze_stock(news_text, stock_data):
    """
    使用DeepSeek分析股票数据和新闻，给出投资建议
    提供具体的买入建议和仓位控制
    """
    prompt = f"""
    请基于以下信息分析是否应该投资该股票，给出详细的分析理由和具体的投资建议：
    
    1. 新闻内容：
    {news_text}
    
    2. 股票基本信息：
    代码：{stock_data.get('basic', {}).get('ts_code', '未知')}
    名称：{stock_data.get('basic', {}).get('name', '未知')}
    行业：{stock_data.get('basic', {}).get('industry', '未知')}
    上市日期：{stock_data.get('basic', {}).get('list_date', '未知')}
    
    3. 当前价格信息：
    最新收盘价：{stock_data.get('price', {}).get('close', '未知')}
    最新交易日涨跌幅：{stock_data.get('price', {}).get('pct_chg', '未知')}%
    市盈率(PE)：{stock_data.get('price', {}).get('pe', '未知')}
    市净率(PB)：{stock_data.get('price', {}).get('pb', '未知')}
    
    4. 关键财务指标：
    每股收益(EPS)：{stock_data.get('financial_indicator', {}).get('eps', '未知')}
    净资产收益率(ROE)：{stock_data.get('financial_indicator', {}).get('roe', '未知')}
    每股净资产：{stock_data.get('financial_indicator', {}).get('bps', '未知')}
    毛利率：{stock_data.get('financial_indicator', {}).get('grossprofit_margin', '未知')}%
    净利率：{stock_data.get('financial_indicator', {}).get('netprofit_margin', '未知')}%
    资产负债率：{stock_data.get('financial_indicator', {}).get('debt_to_assets', '未知')}%
    
    5. 资产负债情况：
    总资产：{stock_data.get('balance_sheet', {}).get('total_assets', '未知')}
    总负债：{stock_data.get('balance_sheet', {}).get('total_liab', '未知')}
    所有者权益：{stock_data.get('balance_sheet', {}).get('total_equity', '未知')}
    货币资金：{stock_data.get('balance_sheet', {}).get('cash_equivalents', '未知')}
    
    6. 盈利能力：
    营业收入：{stock_data.get('income', {}).get('total_revenue', '未知')}
    营业利润：{stock_data.get('income', {}).get('operating_profit', '未知')}
    利润总额：{stock_data.get('income', {}).get('total_profit', '未知')}
    净利润：{stock_data.get('income', {}).get('n_income', '未知')}
    
    7. 现金流情况：
    经营活动现金流：{stock_data.get('cash_flow', {}).get('c_fr_oper_a', '未知')}
    投资活动现金流：{stock_data.get('cash_flow', {}).get('n_cashflow_inv_a', '未知')}
    筹资活动现金流：{stock_data.get('cash_flow', {}).get('n_cash_flows_fin_a', '未知')}
    自由现金流：{stock_data.get('cash_flow', {}).get('free_cash_flow', '未知')}
    
    请给出详细的分析和明确的投资建议，必须包括以下内容：
    1. 基于财务数据的分析（财务健康状况、盈利能力、估值水平等）
    2. 基于新闻内容的分析（可能对公司未来发展的影响）
    3. 明确的投资决策建议：
       - 是否应该买入该股票（必须明确回答"建议买入"、"不建议买入"或"建议观望"）
       - 如果建议买入，建议配置的仓位比例（占总投资的百分比，如5%、10%等）
       - 买入理由和风险提示
       - 预期持有时间（短期、中期或长期）
    
    注意：请确保你的建议是具体的、明确的，避免模糊不清的表述。
    """
    
    response = client.chat.completions.create(
        model="deepseek-r1-distill-qwen-32b-250120",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    if hasattr(response.choices[0].message, 'reasoning_content'):
        print(response.choices[0].message.reasoning_content)
    return response.choices[0].message.content 