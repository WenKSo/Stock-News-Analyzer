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
    主要关注新闻对股票的影响
    """
    prompt = f"""
    请基于以下信息分析这条新闻对该股票的影响，重点是判断该新闻是否会对股票产生积极、消极或中性影响，并给出具体的投资建议：
    
    1. 【新闻内容】(这是分析的核心和重点)：
    {news_text}
    
    请首先深入分析这条新闻：
    - 这条新闻对公司有何具体影响？
    - 这是利好、利空还是中性消息？
    - 新闻传递的信息会如何影响公司的短期表现和长期发展？
    - 市场可能会如何反应？是否已经反应在股价上？
    - 这条新闻是否改变了公司的基本面或未来发展前景？
    
    2. 股票基本信息（作为参考）：
    代码：{stock_data.get('basic', {}).get('ts_code', '未知')}
    名称：{stock_data.get('basic', {}).get('name', '未知')}
    行业：{stock_data.get('basic', {}).get('industry', '未知')}
    上市日期：{stock_data.get('basic', {}).get('list_date', '未知')}
    
    3. 当前价格信息（作为参考）：
    最新收盘价：{stock_data.get('price', {}).get('close', '未知')}
    最新交易日涨跌幅：{stock_data.get('price', {}).get('pct_chg', '未知')}%
    市盈率(PE)：{stock_data.get('price', {}).get('pe', '未知')}
    市净率(PB)：{stock_data.get('price', {}).get('pb', '未知')}
    
    4. 关键财务指标（作为参考）：
    每股收益(EPS)：{stock_data.get('financial_indicator', {}).get('eps', '未知')}
    净资产收益率(ROE)：{stock_data.get('financial_indicator', {}).get('roe', '未知')}
    每股净资产：{stock_data.get('financial_indicator', {}).get('bps', '未知')}
    毛利率：{stock_data.get('financial_indicator', {}).get('grossprofit_margin', '未知')}%
    净利率：{stock_data.get('financial_indicator', {}).get('netprofit_margin', '未知')}%
    资产负债率：{stock_data.get('financial_indicator', {}).get('debt_to_assets', '未知')}%
    
    5. 资产负债情况（简要参考）：
    总资产：{stock_data.get('balance_sheet', {}).get('total_assets', '未知')}
    总负债：{stock_data.get('balance_sheet', {}).get('total_liab', '未知')}
    
    请给出详细分析和明确的投资建议，必须按照以下结构呈现：
    
    ### 一、新闻分析（占分析内容的60%以上）
    [深入分析这条新闻对公司的具体影响，这是最核心的部分]
    - 新闻传递的核心信息是什么？
    - 对公司业务、收入和利润的可能影响
    - 对行业竞争格局的影响
    - 对公司市场地位的影响
    - 新闻可能导致的市场反应
    
    ### 二、基本面简要分析（占分析内容的20%左右）
    [简要分析公司当前基本面状况，仅作为辅助参考]
    - 公司当前估值是否合理
    - 财务状况是否健康
    - 盈利能力如何
    
    ### 三、综合判断与投资建议（占分析内容的20%左右）
    [结合新闻和基本面，给出明确的投资建议]
    1. 整体判断：这条新闻是否足以影响投资决策
    2. 投资决策：必须明确给出以下三种结论之一
       - "建议买入"：如果新闻带来明显的积极信号且基本面可接受
       - "不建议买入"：如果新闻带来明显的负面信号或风险
       - "建议观望"：如果新闻影响不明确或需要进一步观察
    3. 如果建议买入：
       - 建议配置的仓位比例（占总投资的百分比，如5%、10%等）
       - 预期持有时间（短期、中期或长期）
    4. 投资理由（优势）和风险提示
    
    注意：重点分析新闻内容对该股票的直接影响，这是决策的核心依据。基本面数据仅作为辅助参考，不应该成为分析的主体。
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