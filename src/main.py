import os
import json
import tushare as ts
import sys
from volcenginesdkarkruntime import Ark

# 获取当前文件的绝对路径，然后获取其上一级目录（项目根目录）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从config导入常量
from config.config import ARK_API_KEY, TUSHARE_TOKEN

# 配置 Tushare API
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

# 配置 DeepSeek
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

def get_stock_data(stock_code):
    """
    获取股票的全面数据，包括：
    1. 基本信息
    2. 当前价格和交易数据
    3. 资产负债表关键数据
    4. 利润表关键数据
    5. 现金流量表关键数据
    6. 关键财务指标（如PE、PB、ROE等）
    """
    try:
        # 获取股票基本信息
        stock_basic = pro.stock_basic(ts_code=stock_code, fields='ts_code,symbol,name,area,industry,market,list_date')
        
        # 获取最新交易日数据（价格等）
        daily_data = pro.daily(ts_code=stock_code, limit=1)
        
        # 获取最新财务指标数据
        financial_indicator = pro.fina_indicator(ts_code=stock_code, period='20231231', fields='ts_code,ann_date,eps,dt_eps,total_revenue_ps,revenue_ps,capital_rese_ps,surplus_rese_ps,undist_profit_ps,extra_item,profit_dedt,gross_margin,current_ratio,quick_ratio,cash_ratio,ar_turn,inv_turn,assets_turn,bps,netasset_ps,cf_ps,ebit_ps,fcff_ps,fcfe_ps,netprofit_margin,grossprofit_margin,profit_to_gr,op_of_gr,roe,roe_waa,roe_dt,roa,npta,roic,roe_yearly,roa2_yearly')
        
        # 获取资产负债表数据
        balance_sheet = pro.balancesheet(ts_code=stock_code, period='20231231', fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,total_assets,total_cur_assets,total_non_cur_assets,total_liab,total_cur_liab,total_non_cur_liab,total_hldr_eqy_exc_min_int,total_hldr_eqy_inc_min_int,total_liab_hldr_eqy,lt_borr,st_borr,cb_borr')
        
        # 获取利润表数据
        income = pro.income(ts_code=stock_code, period='20231231', fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,total_revenue,revenue,int_income,n_income_attr_p,n_income_attr_p_cut,oper_cost,operate_profit,ebit,ebitda,oper_profit,val_chg_profit,n_income')
        
        # 获取现金流量表数据
        cash_flow = pro.cashflow(ts_code=stock_code, period='20231231', fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,net_profit,finan_exp,c_fr_oper_a,n_cashflow_act,c_paid_invest,n_cashflow_inv_a,c_fr_fin_a,n_cash_flows_fin_a,n_incr_cash_cash_equ')
        
        # 整合所有数据
        stock_data = {
            'basic': stock_basic.to_dict('records')[0] if not stock_basic.empty else {},
            'price': daily_data.to_dict('records')[0] if not daily_data.empty else {},
            'financial_indicator': financial_indicator.to_dict('records')[0] if not financial_indicator.empty else {},
            'balance_sheet': balance_sheet.to_dict('records')[0] if not balance_sheet.empty else {},
            'income': income.to_dict('records')[0] if not income.empty else {},
            'cash_flow': cash_flow.to_dict('records')[0] if not cash_flow.empty else {}
        }
        
        return stock_data
    except Exception as e:
        print(f"获取股票 {stock_code} 数据时出错: {e}")
        return {}

def analyze_stock(news_text, stock_data):
    """
    使用DeepSeek分析股票数据和新闻，给出投资建议
    """
    prompt = f"""
    请基于以下信息分析是否应该投资该股票，给出详细的分析理由和建议：
    
    1. 新闻内容：
    {news_text}
    
    2. 股票基本信息：
    代码：{stock_data.get('basic', {}).get('ts_code', '未知')}
    名称：{stock_data.get('basic', {}).get('name', '未知')}
    行业：{stock_data.get('basic', {}).get('industry', '未知')}
    
    3. 当前价格信息：
    最新收盘价：{stock_data.get('price', {}).get('close', '未知')}
    最新交易日涨跌幅：{stock_data.get('price', {}).get('pct_chg', '未知')}%
    
    4. 关键财务指标：
    每股收益(EPS)：{stock_data.get('financial_indicator', {}).get('eps', '未知')}
    市盈率(PE)：{stock_data.get('price', {}).get('close', 0) / stock_data.get('financial_indicator', {}).get('eps', 1) if stock_data.get('financial_indicator', {}).get('eps', 0) != 0 else '未知'}
    净资产收益率(ROE)：{stock_data.get('financial_indicator', {}).get('roe', '未知')}
    每股净资产：{stock_data.get('financial_indicator', {}).get('bps', '未知')}
    
    5. 资产负债情况：
    总资产：{stock_data.get('balance_sheet', {}).get('total_assets', '未知')}
    总负债：{stock_data.get('balance_sheet', {}).get('total_liab', '未知')}
    资产负债率：{stock_data.get('balance_sheet', {}).get('total_liab', 0) / stock_data.get('balance_sheet', {}).get('total_assets', 1) * 100 if stock_data.get('balance_sheet', {}).get('total_assets', 0) != 0 else '未知'}%
    
    6. 盈利能力：
    营业收入：{stock_data.get('income', {}).get('total_revenue', '未知')}
    净利润：{stock_data.get('income', {}).get('n_income', '未知')}
    毛利率：{stock_data.get('financial_indicator', {}).get('grossprofit_margin', '未知')}%
    
    7. 现金流情况：
    经营活动现金流：{stock_data.get('cash_flow', {}).get('c_fr_oper_a', '未知')}
    投资活动现金流：{stock_data.get('cash_flow', {}).get('n_cashflow_inv_a', '未知')}
    筹资活动现金流：{stock_data.get('cash_flow', {}).get('n_cash_flows_fin_a', '未知')}
    
    请给出详细的分析和投资建议，包括：
    1. 基于财务数据的分析（财务健康状况、盈利能力、估值水平等）
    2. 基于新闻内容的分析（可能对公司未来发展的影响）
    3. 综合分析和投资建议（是否值得投资、投资理由、风险提示等）
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
        
        for stock_code in stock_codes.split(','):
            # 获取股票数据
            stock_data = get_stock_data(stock_code.strip())
            # 综合分析
            analysis_result = analyze_stock(news_text, stock_data)
            print(f"股票代码：{stock_code}\n分析结果：{analysis_result}")

if __name__ == "__main__":
    main()