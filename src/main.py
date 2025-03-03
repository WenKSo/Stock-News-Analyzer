import os
import json
import sys
import akshare as ak
from volcenginesdkarkruntime import Ark

# 获取当前文件的绝对路径，然后获取其上一级目录（项目根目录）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从config导入常量
from config.config import ARK_API_KEY

# 配置 DeepSeek
client = Ark(
    api_key=ARK_API_KEY,
    timeout=1800,
)

def analyze_news(news_text):
    """
    分析新闻内容，提取相关的股票代码
    确保只返回已上市的A股股票代码
    """
    prompt = f"""
    分析以下新闻内容，并提取与之最相关的股票代码。
    
    要求：
    1. 只提取已经在A股上市的公司股票代码
    2. 不要提取未上市公司（如华为、字节跳动等）
    3. 如果新闻中没有明确提到已上市公司，请回复"无相关上市公司"
    4. 你的回答只需要输出1个股票代码，不要参杂其他内容
    5. 股票代码格式为6位数字，如"600519"或"000001"
    
    新闻内容：{news_text}
    """
    
    response = client.chat.completions.create(
        model="deepseek-r1-distill-qwen-32b-250120",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    if hasattr(response.choices[0].message, 'reasoning_content'):
        print(response.choices[0].message.reasoning_content)
    
    # 获取AI返回的股票代码
    stock_code = response.choices[0].message.content.strip()
    
    # 验证返回的是否为有效的股票代码
    if stock_code == "无相关上市公司":
        return stock_code
    
    # 尝试验证股票代码是否为已上市股票
    try:
        # 获取所有A股股票列表
        stock_list = ak.stock_zh_a_spot_em()
        # 检查返回的股票代码是否在列表中
        if stock_code in stock_list['代码'].values:
            print(f"验证通过：{stock_code} 是已上市的A股股票")
            return stock_code
        else:
            # 如果不在列表中，尝试添加市场后缀
            if stock_code.startswith(('0', '3')):
                formatted_code = f"{stock_code}.SZ"
            elif stock_code.startswith(('6', '9')):
                formatted_code = f"{stock_code}.SH"
            else:
                formatted_code = stock_code
            print(f"股票代码 {stock_code} 不在A股列表中，转换为 {formatted_code}")
            return formatted_code
    except Exception as e:
        print(f"验证股票代码时出错: {e}")
        # 如果验证过程出错，仍然返回原始代码，但在后续处理中会再次验证
        return stock_code

def get_stock_data(stock_code):
    """
    使用Akshare获取股票的全面数据，包括：
    1. 基本信息
    2. 当前价格和交易数据
    3. 资产负债表关键数据
    4. 利润表关键数据
    5. 现金流量表关键数据
    6. 关键财务指标（如PE、PB、ROE等）
    """
    try:
        # 处理股票代码格式（如果需要）
        code_without_market = stock_code
        if '.' in stock_code:
            # 如果是类似 "600519.SH" 的格式，转换为 "sh600519" 格式
            code_parts = stock_code.split('.')
            code_without_market = code_parts[0]  # 600519
            market = code_parts[1].lower()  # sh
            
            if market == 'sh':
                formatted_code = f"sh{code_without_market}"
            elif market == 'sz':
                formatted_code = f"sz{code_without_market}"
            else:
                formatted_code = code_without_market
        else:
            # 如果只有数字，根据第一位判断市场
            if len(stock_code) == 6:
                if stock_code.startswith(('0', '3')):
                    formatted_code = f"sz{stock_code}"
                elif stock_code.startswith(('6', '9')):
                    formatted_code = f"sh{stock_code}"
                else:
                    formatted_code = stock_code
            else:
                formatted_code = stock_code
        
        print(f"原始股票代码: {stock_code}, 处理后的股票代码: {formatted_code}, 纯代码: {code_without_market}")
        
        # 获取股票基本信息
        try:
            stock_info = ak.stock_individual_info_em(symbol=formatted_code)
            print(f"获取到的股票基本信息: {stock_info.head()}")
        except Exception as e:
            print(f"获取股票基本信息出错: {e}")
            # 尝试使用另一种方式获取基本信息
            try:
                stock_info = ak.stock_individual_info_em(symbol=code_without_market)
                print(f"使用纯代码获取到的股票基本信息: {stock_info.head()}")
            except Exception as e2:
                print(f"使用纯代码获取股票基本信息也出错: {e2}")
                # 创建一个空的DataFrame作为备用
                import pandas as pd
                stock_info = pd.DataFrame({'item': ['名称', '所属行业', '上市日期'], 'value': ['未知', '未知', '未知']})
        
        # 获取最新交易日数据（价格等）
        try:
            daily_data = ak.stock_zh_a_daily(symbol=formatted_code, adjust="qfq").iloc[-1].to_dict()
            print(f"获取到的最新交易日数据: {daily_data}")
        except Exception as e:
            print(f"获取最新交易日数据出错: {e}")
            # 尝试使用另一种方式获取
            try:
                daily_data = ak.stock_zh_a_daily(symbol=code_without_market, adjust="qfq").iloc[-1].to_dict()
                print(f"使用纯代码获取到的最新交易日数据: {daily_data}")
            except Exception as e2:
                print(f"使用纯代码获取最新交易日数据也出错: {e2}")
                daily_data = {}
        
        # 获取实时行情
        try:
            real_time_quote = ak.stock_zh_a_spot_em()
            print(f"查询的股票代码: {code_without_market}")
            real_time_quote = real_time_quote[real_time_quote['代码'] == code_without_market]
            
            if not real_time_quote.empty:
                real_time_quote = real_time_quote.to_dict('records')[0]
                print(f"获取到的实时行情: {real_time_quote}")
            else:
                print(f"未找到股票代码 {code_without_market} 的实时行情")
                real_time_quote = {}
        except Exception as e:
            print(f"获取实时行情出错: {e}")
            real_time_quote = {}
        
        # 获取财务指标数据
        financial_indicator = {}
        try:
            # 获取主要财务指标 - 使用正确的API参数
            import datetime
            current_year = str(datetime.datetime.now().year)
            fin_indicator = ak.stock_financial_analysis_indicator(symbol=code_without_market, start_year=str(int(current_year)-3))
            if not fin_indicator.empty:
                # 获取最新的一期数据
                financial_indicator = fin_indicator.iloc[0].to_dict()
                print("\n获取到的财务指标原始数据：")
                print("所有字段名称：", list(financial_indicator.keys()))
                print("\n前几个字段的值：")
                for i, (key, value) in enumerate(financial_indicator.items()):
                    if i < 10:  # 只打印前10个字段
                        print(f"{key}: {value}")
            else:
                print("获取到的财务指标数据为空")
        except Exception as e:
            print(f"获取财务指标数据出错: {e}")
            # 尝试使用其他API获取财务指标
            try:
                # 尝试使用财务报表API获取
                fin_indicator = ak.stock_financial_report_em(stock=code_without_market, report_type="资产负债表")
                if not fin_indicator.empty:
                    financial_indicator = fin_indicator.iloc[0].to_dict()
                    print(f"使用备选API获取到的财务指标数据: {list(financial_indicator.keys())[:10]}...")
            except Exception as e2:
                print(f"使用备选API获取财务指标数据也出错: {e2}")
                print(f"错误详情: {str(e2)}")
                
        # 打印更多的调试信息
        if financial_indicator:
            print("\n尝试不同的字段名称获取财务指标：")
            # 每股收益的可能字段名
            eps_value = financial_indicator.get('加权每股收益(元)',
                       financial_indicator.get('摊薄每股收益(元)',
                       financial_indicator.get('每股收益_调整后(元)',
                       financial_indicator.get('基本每股收益', '未知'))))
            
            # 净资产收益率的可能字段名
            roe_value = financial_indicator.get('净资产收益率(%)',
                       financial_indicator.get('加权净资产收益率(%)',
                       financial_indicator.get('净资产报酬率(%)', '未知')))
            
            # 毛利率的可能字段名
            gpm_value = financial_indicator.get('销售毛利率(%)',
                       financial_indicator.get('主营业务利润率(%)', '未知'))
            
            # 其他关键指标
            bps_value = financial_indicator.get('每股净资产_调整后(元)',
                       financial_indicator.get('每股净资产_调整前(元)', '未知'))
            
            npm_value = financial_indicator.get('销售净利率(%)', '未知')
            
            dar_value = financial_indicator.get('资产负债率(%)', '未知')
            
            print(f"基本每股收益: {eps_value}")
            print(f"净资产收益率: {roe_value}")
            print(f"毛利率: {gpm_value}")
            print(f"每股净资产: {bps_value}")
            print(f"销售净利率: {npm_value}")
            print(f"资产负债率: {dar_value}")
            
            # 更新financial_indicator字典中的值
            financial_indicator.update({
                '基本每股收益': eps_value,
                '净资产收益率': roe_value,
                '毛利率': gpm_value,
                '每股净资产': bps_value,
                '净利率': npm_value,
                '资产负债率': dar_value
            })
        else:
            print("未能获取到任何财务指标数据")
        
        # 获取资产负债表数据
        balance_sheet = {}
        try:
            # 使用正确的API获取资产负债表
            bs_data = ak.stock_financial_report_em(stock=code_without_market, report_type="资产负债表")
            if not bs_data.empty:
                balance_sheet = bs_data.iloc[0].to_dict()
                print(f"获取到的资产负债表数据: {list(balance_sheet.keys())[:10]}...")  # 只打印前10个键
            else:
                print("获取到的资产负债表数据为空")
        except Exception as e:
            print(f"获取资产负债表数据出错: {e}")
        
        # 获取利润表数据
        income = {}
        try:
            # 使用正确的API获取利润表
            income_data = ak.stock_financial_report_em(stock=code_without_market, report_type="利润表")
            if not income_data.empty:
                income = income_data.iloc[0].to_dict()
                print(f"获取到的利润表数据: {list(income.keys())[:10]}...")  # 只打印前10个键
            else:
                print("获取到的利润表数据为空")
        except Exception as e:
            print(f"获取利润表数据出错: {e}")
        
        # 获取现金流量表数据
        cash_flow = {}
        try:
            # 使用正确的API获取现金流量表
            cf_data = ak.stock_financial_report_em(stock=code_without_market, report_type="现金流量表")
            if not cf_data.empty:
                cash_flow = cf_data.iloc[0].to_dict()
                print(f"获取到的现金流量表数据: {list(cash_flow.keys())[:10]}...")  # 只打印前10个键
            else:
                print("获取到的现金流量表数据为空")
        except Exception as e:
            print(f"获取现金流量表数据出错: {e}")
        
        # 获取市盈率、市净率等估值指标
        valuation = {}
        try:
            # 使用实时行情中的估值指标
            valuation = {
                'pe': real_time_quote.get('市盈率-动态', '未知'),
                'pb': real_time_quote.get('市净率', '未知'),
                'total_mv': real_time_quote.get('总市值', '未知'),
                'circ_mv': real_time_quote.get('流通市值', '未知')
            }
            print(f"从实时行情获取的估值指标数据: {valuation}")
        except Exception as e:
            print(f"获取估值指标数据出错: {e}")
        
        # 获取股票名称
        stock_name = '未知'
        if not real_time_quote.get('名称', ''):
            # 尝试从stock_info获取名称
            name_row = stock_info[stock_info['item'] == '名称']
            if not name_row.empty:
                stock_name = name_row['value'].values[0]
        else:
            stock_name = real_time_quote.get('名称', '未知')
        
        # 获取行业信息
        industry = '未知'
        industry_row = stock_info[stock_info['item'] == '所属行业']
        if not industry_row.empty:
            industry = industry_row['value'].values[0]
        
        # 获取上市日期
        list_date = '未知'
        list_date_row = stock_info[stock_info['item'] == '上市日期']
        if not list_date_row.empty:
            list_date = list_date_row['value'].values[0]
        
        # 检查是否为已上市股票
        is_listed = True
        if list_date == '未知' or not real_time_quote:
            # 尝试进一步确认是否已上市
            try:
                stock_list = ak.stock_zh_a_spot_em()
                is_listed = code_without_market in stock_list['代码'].values
                print(f"股票 {code_without_market} 是否在A股上市: {is_listed}")
            except Exception as e:
                print(f"检查股票是否上市出错: {e}")
                is_listed = False
        
        # 如果不是已上市股票，返回空数据
        if not is_listed:
            print(f"股票 {stock_code} 不是已上市股票，跳过数据获取")
            return {}
        
        # 整合所有数据
        stock_data = {
            'basic': {
                'ts_code': stock_code,
                'name': stock_name,
                'industry': industry,
                'list_date': list_date,
            },
            'price': {
                'close': daily_data.get('close', real_time_quote.get('最新价', '未知')),
                'pct_chg': real_time_quote.get('涨跌幅', '未知'),
                'pe': valuation.get('pe', '未知'),
                'pb': valuation.get('pb', '未知'),
                'total_mv': valuation.get('total_mv', '未知'),
                'circ_mv': valuation.get('circ_mv', '未知'),
            },
            'financial_indicator': {
                'eps': eps_value if financial_indicator else '未知',
                'roe': roe_value if financial_indicator else '未知',
                'bps': bps_value if financial_indicator else '未知',
                'grossprofit_margin': gpm_value if financial_indicator else '未知',
                'netprofit_margin': npm_value if financial_indicator else '未知',
                'debt_to_assets': dar_value if financial_indicator else '未知',
            },
            'balance_sheet': {
                'total_assets': balance_sheet.get('资产总计' if '资产总计' in balance_sheet else '资产总额', balance_sheet.get('总资产', '未知')),
                'total_liab': balance_sheet.get('负债合计' if '负债合计' in balance_sheet else '负债总额', balance_sheet.get('总负债', '未知')),
                'total_equity': balance_sheet.get('所有者权益(或股东权益)合计', balance_sheet.get('股东权益合计', balance_sheet.get('所有者权益', '未知'))),
                'cash_equivalents': balance_sheet.get('货币资金', balance_sheet.get('现金及现金等价物', '未知')),
            },
            'income': {
                'total_revenue': income.get('营业总收入' if '营业总收入' in income else '营业收入', income.get('营业收入', '未知')),
                'operating_profit': income.get('营业利润', '未知'),
                'n_income': income.get('净利润', '未知'),
                'total_profit': income.get('利润总额', '未知'),
            },
            'cash_flow': {
                'c_fr_oper_a': cash_flow.get('经营活动产生的现金流量净额', cash_flow.get('经营活动现金流量净额', '未知')),
                'n_cashflow_inv_a': cash_flow.get('投资活动产生的现金流量净额', cash_flow.get('投资活动现金流量净额', '未知')),
                'n_cash_flows_fin_a': cash_flow.get('筹资活动产生的现金流量净额', cash_flow.get('筹资活动现金流量净额', '未知')),
                'free_cash_flow': cash_flow.get('企业自由现金流量', cash_flow.get('自由现金流量', '未知')),
            }
        }
        
        print(f"整合后的股票数据: {stock_data}")
        return stock_data
    except Exception as e:
        print(f"获取股票 {stock_code} 数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return {}

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

def main():
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(__file__)
        # 构造 data 目录下的 JSON 文件路径
        json_path = os.path.join(current_dir, '..', 'data', 'news_data.json')
        
        print(f"尝试读取新闻数据文件: {json_path}")
        
        # 假设你已经使用八爪鱼爬虫爬取了新闻数据，并保存为 news_data.json
        with open(json_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        print(f"成功读取新闻数据，共 {len(news_data)} 条")
        
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
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()