import akshare as ak
import pandas as pd
from datetime import datetime

def get_stock_basic_info(stock_code):
    """
    获取股票的基本信息，包括名称、行业、上市日期等
    使用多种方法尝试获取，提高成功率
    """
    try:
        # 处理股票代码格式
        code_without_market = stock_code
        if '.' in stock_code:
            code_parts = stock_code.split('.')
            code_without_market = code_parts[0]
        
        # 尝试方法1: 使用 stock_individual_info_em
        try:
            info = ak.stock_individual_info_em(symbol=code_without_market)
            if not info.empty:
                print(f"使用stock_individual_info_em成功获取到股票信息: {info.head()}")
                
                # 正确映射字段名称
                # 检查数据中是否有我们需要的字段
                has_industry = False
                has_list_date = False
                industry_value = '未知'
                list_date_value = '未知'
                
                # 遍历获取到的数据寻找对应字段
                for _, row in info.iterrows():
                    item = row['item']
                    if item == '行业':
                        has_industry = True
                        industry_value = row['value']
                    elif item == '上市时间':
                        has_list_date = True
                        # 尝试格式化上市时间
                        try:
                            # 如果上市时间是类似"20111216"的数字格式，将其转换为"2011-12-16"格式
                            list_date_str = str(row['value'])
                            if len(list_date_str) == 8 and list_date_str.isdigit():
                                list_date_value = f"{list_date_str[:4]}-{list_date_str[4:6]}-{list_date_str[6:8]}"
                            else:
                                list_date_value = list_date_str
                        except:
                            list_date_value = str(row['value'])
                
                # 如果没有找到需要的字段，则保持原有结构
                if not (has_industry and has_list_date):
                    return ensure_compatible_types(info)
                
                # 创建一个新的DataFrame，确保包含我们需要的所有字段
                mapped_info = pd.DataFrame({
                    'item': ['名称', '所属行业', '上市日期'],
                    'value': [
                        info[info['item'] == '股票简称'].iloc[0]['value'] if '股票简称' in info['item'].values else 
                        (info[info['item'] == '名称'].iloc[0]['value'] if '名称' in info['item'].values else '未知'),
                        industry_value,
                        list_date_value
                    ]
                })
                print(f"映射后的股票信息: {mapped_info}")
                return ensure_compatible_types(mapped_info)
        except Exception as e:
            print(f"使用stock_individual_info_em获取股票信息失败: {e}")
        
        # 尝试方法2: 使用 stock_zh_a_spot_em
        try:
            spot_info = ak.stock_zh_a_spot_em()
            stock_spot = spot_info[spot_info['代码'] == code_without_market]
            if not stock_spot.empty:
                # 转换为预期的格式
                info = pd.DataFrame({
                    'item': ['名称', '所属行业', '上市日期'],
                    'value': [
                        stock_spot['名称'].values[0],
                        '未知',  # 行业信息需要从其他API获取
                        '未知'   # 上市日期需要从其他API获取
                    ]
                })
                print(f"使用stock_zh_a_spot_em成功获取到股票信息: {info}")
                return ensure_compatible_types(info)
        except Exception as e:
            print(f"使用stock_zh_a_spot_em获取股票信息失败: {e}")
        
        # 尝试方法3: 使用 stock_info_a_code_name
        try:
            stock_list = ak.stock_info_a_code_name()
            stock_basic = stock_list[stock_list['code'] == code_without_market]
            if not stock_basic.empty:
                info = pd.DataFrame({
                    'item': ['名称', '所属行业', '上市日期'],
                    'value': [
                        stock_basic['name'].values[0],
                        '未知',  # 行业信息需要从其他API获取
                        '未知'   # 上市日期需要从其他API获取
                    ]
                })
                print(f"使用stock_info_a_code_name成功获取到股票信息: {info}")
                return ensure_compatible_types(info)
        except Exception as e:
            print(f"使用stock_info_a_code_name获取股票信息失败: {e}")
        
        # 如果所有方法都失败，返回空的DataFrame
        print(f"所有方法都无法获取股票 {stock_code} 的基本信息")
        return ensure_compatible_types(pd.DataFrame({'item': ['名称', '所属行业', '上市日期'], 'value': ['未知', '未知', '未知']}))
    except Exception as e:
        print(f"获取股票基本信息时发生未知错误: {e}")
        return ensure_compatible_types(pd.DataFrame({'item': ['名称', '所属行业', '上市日期'], 'value': ['未知', '未知', '未知']}))

def ensure_compatible_types(df):
    """
    确保DataFrame中的数据类型兼容，特别是处理可能导致PyArrow错误的混合类型
    """
    if df is None or df.empty:
        return df
    
    # 检查每一列
    for col in df.columns:
        # 如果列中有'未知'值，将整列转换为字符串类型
        if df[col].astype(str).str.contains('未知').any():
            df[col] = df[col].astype(str)
    
    return df

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
        stock_info = get_stock_basic_info(stock_code)
        
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
            # 使用stock_individual_spot_xq获取实时行情
            # 格式化股票代码为雪球接口所需格式 (SH或SZ + 代码)
            if formatted_code.startswith('sh'):
                xq_symbol = f"SH{code_without_market}"
            elif formatted_code.startswith('sz'):
                xq_symbol = f"SZ{code_without_market}"
            else:
                xq_symbol = code_without_market
                
            print(f"查询的股票代码: {code_without_market}, 雪球格式: {xq_symbol}")
            real_time_quote = ak.stock_individual_spot_xq(symbol=xq_symbol)
            
            if not real_time_quote.empty:
                # 将DataFrame转换为字典格式
                real_time_quote_dict = {}
                for _, row in real_time_quote.iterrows():
                    real_time_quote_dict[row['item']] = row['value']
                
                real_time_quote = real_time_quote_dict
                print(f"获取到的实时行情: {real_time_quote}")
            else:
                print(f"未找到股票代码 {xq_symbol} 的实时行情")
                real_time_quote = {}
        except Exception as e:
            print(f"获取实时行情出错: {e}")
            real_time_quote = {}
        
        # 获取财务指标数据
        financial_indicator = {}
        try:
            # 获取主要财务指标 - 使用正确的API参数
            current_year = str(datetime.now().year)
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
                # 尝试使用财务报表API获取 - 先尝试获取利润表
                fin_indicator = ak.stock_financial_report_sina(stock=formatted_code, symbol="利润表")
                if not fin_indicator.empty:
                    financial_indicator = fin_indicator.iloc[0].to_dict()
                    print(f"使用利润表API获取到的财务指标数据: {list(financial_indicator.keys())[:10]}...")
                else:
                    # 如果利润表为空，尝试获取资产负债表
                    fin_indicator = ak.stock_financial_report_sina(stock=formatted_code, symbol="资产负债表")
                    if not fin_indicator.empty:
                        financial_indicator = fin_indicator.iloc[0].to_dict()
                        print(f"使用资产负债表API获取到的财务指标数据: {list(financial_indicator.keys())[:10]}...")
            except Exception as e2:
                print(f"使用备选API获取财务指标数据也出错: {e2}")
                print(f"错误详情: {str(e2)}")
                
        # 创建一个函数来获取财务指标值，使用多个可能的字段名称
        def get_financial_value(data_dict, possible_keys, default='未知'):
            for key in possible_keys:
                if key in data_dict:
                    return data_dict[key]
            return default
        
        # 整理财务指标 - 使用字典映射更系统化地处理
        financial_metrics = {}
        if financial_indicator:
            # 基本财务指标映射表
            financial_metrics_mapping = {
                # 收益能力指标
                'eps': ['加权每股收益(元)', '摊薄每股收益(元)', '每股收益_调整后(元)', '基本每股收益', '每股收益', 'EPS', '稀释每股收益'],
                'diluted_eps': ['稀释每股收益', '稀释每股收益(元)'],
                'adjusted_eps': ['扣除非经常性损益后的每股收益(元)', '扣非每股收益'],
                'roe': ['净资产收益率(%)', '加权净资产收益率(%)', '净资产报酬率(%)', 'ROE', '净资产收益率'],
                'weighted_roe': ['加权净资产收益率(%)', '加权平均净资产收益率'],
                'gross_profit_margin': ['销售毛利率(%)', '主营业务利润率(%)', '毛利率', '综合毛利率'],
                'net_profit_margin': ['销售净利率(%)', '净利率(%)', '净利润率', '营业利润率'],
                
                # 每股指标
                'bps': ['每股净资产_调整后(元)', '每股净资产_调整前(元)', '每股净资产', 'BPS'],
                'ocf_per_share': ['每股经营性现金流(元)', '每股经营活动产生的现金流量净额', '每股现金流量净额'],
                'capital_reserve_per_share': ['每股资本公积金(元)', '每股资本公积'],
                'undistributed_profit_per_share': ['每股未分配利润(元)', '每股未分配利润'],
                
                # 盈利能力
                'rop': ['总资产报酬率(%)', '总资产利润率(%)', '资产报酬率(%)'],
                'operating_profit_ratio': ['营业利润率(%)', '经营利润率'],
                'cost_profit_ratio': ['成本费用利润率(%)', '成本费用利润率'],
                
                # 成长能力
                'revenue_growth': ['主营业务收入增长率(%)', '营业收入增长率', '营收增长率'],
                'profit_growth': ['净利润增长率(%)', '净利润增长率'],
                'asset_growth': ['总资产增长率(%)', '资产增长率'],
                'equity_growth': ['净资产增长率(%)', '股东权益增长率'],
                
                # 营运能力
                'ar_turnover': ['应收账款周转率(次)', '应收账款周转率'],
                'ar_turnover_days': ['应收账款周转天数(天)', '应收账款周转天数'],
                'inventory_turnover': ['存货周转率(次)', '存货周转率'],
                'inventory_turnover_days': ['存货周转天数(天)', '存货周转天数'],
                'fixed_asset_turnover': ['固定资产周转率(次)', '固定资产周转率'],
                'total_asset_turnover': ['总资产周转率(次)', '总资产周转率'],
                
                # 偿债能力
                'current_ratio': ['流动比率', '流动比率(倍)'],
                'quick_ratio': ['速动比率', '速动比率(倍)'],
                'cash_ratio': ['现金比率(%)', '现金比率'],
                'debt_to_assets': ['资产负债率(%)', '资产负债率', '负债资产比率', '总资产负债率'],
                'equity_ratio': ['股东权益比率(%)', '净资产负债率', '所有者权益比率'],
                'debt_to_equity': ['负债与所有者权益比率(%)', '产权比率(%)', '资产负债率'],
                
                # 现金流指标
                'ocf_to_sales': ['经营现金净流量对销售收入比率(%)', '销售现金比率'],
                'ocf_to_profit': ['经营现金净流量与净利润的比率(%)', '现金净流量与净利润比率'],
                'ocf_to_debt': ['经营现金净流量对负债比率(%)', '现金流量债务比'],
                
                # 特殊金融企业指标
                'capital_adequacy': ['资本充足率', '核心资本充足率', '资本充足率(%)'],
                'net_interest_margin': ['净息差', '净利息收入/平均生息资产', '净利息收入比率']
            }
            
            # 遍历映射表并提取数据
            for metric_key, possible_field_names in financial_metrics_mapping.items():
                value = get_financial_value(financial_indicator, possible_field_names)
                financial_metrics[metric_key] = value
                print(f"{metric_key}: {value}")
                
            print("\n提取后的关键财务指标:")
            for k, v in financial_metrics.items():
                print(f"{k}: {v}")
        else:
            print("未能获取到任何财务指标数据")
            # 初始化所有指标为"未知"
            for metric_key in ['eps', 'diluted_eps', 'adjusted_eps', 'roe', 'weighted_roe', 
                            'gross_profit_margin', 'net_profit_margin', 'bps', 'ocf_per_share',
                            'capital_reserve_per_share', 'undistributed_profit_per_share',
                            'rop', 'operating_profit_ratio', 'cost_profit_ratio',
                            'revenue_growth', 'profit_growth', 'asset_growth', 'equity_growth',
                            'ar_turnover', 'ar_turnover_days', 'inventory_turnover', 
                            'inventory_turnover_days', 'fixed_asset_turnover', 'total_asset_turnover',
                            'current_ratio', 'quick_ratio', 'cash_ratio', 'debt_to_assets',
                            'equity_ratio', 'debt_to_equity', 'ocf_to_sales', 'ocf_to_profit',
                            'ocf_to_debt', 'capital_adequacy', 'net_interest_margin']:
                financial_metrics[metric_key] = '未知'
        
        # 获取资产负债表数据
        balance_sheet = {}
        try:
            # 使用正确的API获取资产负债表
            bs_data = ak.stock_financial_report_sina(stock=formatted_code, symbol="资产负债表")
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
            income_data = ak.stock_financial_report_sina(stock=formatted_code, symbol="利润表")
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
            cf_data = ak.stock_financial_report_sina(stock=formatted_code, symbol="现金流量表")
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
                'pe': real_time_quote.get('市盈率(TTM)', real_time_quote.get('市盈率(静)', '未知')),
                'pb': real_time_quote.get('市净率', '未知'),
                'total_mv': real_time_quote.get('资产净值/总市值', real_time_quote.get('市值', '未知')),
                'circ_mv': real_time_quote.get('流通值', '未知')
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
        # 如果从基本信息中获取不到行业，尝试从实时行情中获取
        if industry == '未知' and real_time_quote.get('行业'):
            industry = real_time_quote.get('行业')
        
        # 获取上市日期
        list_date = '未知'
        list_date_row = stock_info[stock_info['item'] == '上市日期']
        if not list_date_row.empty:
            list_date = list_date_row['value'].values[0]
        # 如果从基本信息中获取不到上市日期，尝试从实时行情中获取
        if list_date == '未知' and real_time_quote.get('发行日期'):
            # 尝试格式化发行日期
            try:
                issue_date = real_time_quote.get('发行日期')
                if issue_date and str(issue_date).isdigit():
                    # 假设发行日期是毫秒时间戳
                    list_date = datetime.fromtimestamp(int(issue_date)/1000).strftime('%Y-%m-%d')
            except:
                pass
        
        # 检查是否为已上市股票
        is_listed = True
        if list_date == '未知' or not real_time_quote:
            # 尝试进一步确认是否已上市
            try:
                # 使用 stock_info_a_code_name 获取A股列表
                stock_list = ak.stock_info_a_code_name()
                is_listed = code_without_market in stock_list['code'].values
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
                'close': daily_data.get('close', real_time_quote.get('现价', '未知')),
                'pct_chg': real_time_quote.get('涨幅', '未知'),
                'change': real_time_quote.get('涨跌', '未知'),
                'open': real_time_quote.get('今开', '未知'),
                'high': real_time_quote.get('最高', '未知'),
                'low': real_time_quote.get('最低', '未知'),
                'pe': valuation.get('pe', '未知'),
                'pb': valuation.get('pb', '未知'),
                'total_mv': valuation.get('total_mv', '未知'),
                'circ_mv': valuation.get('circ_mv', '未知'),
                # 添加从雪球获取的额外实时数据 
                '成交量': real_time_quote.get('成交量', '未知'),
                '成交额': real_time_quote.get('成交额', '未知'),
                '52周最高': real_time_quote.get('52周最高', '未知'),
                '52周最低': real_time_quote.get('52周最低', '未知'),
                '今年以来涨幅': real_time_quote.get('今年以来涨幅', '未知'),
                '振幅': real_time_quote.get('振幅', '未知'),
                '均价': real_time_quote.get('均价', '未知'),
                '昨收': real_time_quote.get('昨收', '未知'),
                '交易所': real_time_quote.get('交易所', '未知'),
                '货币': real_time_quote.get('货币', '未知'),
                '时间': real_time_quote.get('时间', '未知'),
                '股息率(TTM)': real_time_quote.get('股息率(TTM)', '未知'),
                '股息(TTM)': real_time_quote.get('股息(TTM)', '未知'),
                '周转率': real_time_quote.get('周转率', '未知'),
                '基金份额/总股本': real_time_quote.get('基金份额/总股本', '未知'),
            },
            'financial_indicator': financial_metrics,
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
        
        # 将所有数据转换为字符串，确保兼容性
        for section in stock_data:
            if isinstance(stock_data[section], dict):
                for key in stock_data[section]:
                    if stock_data[section][key] == '未知' or stock_data[section][key] is None:
                        stock_data[section][key] = '未知'
                    else:
                        stock_data[section][key] = str(stock_data[section][key])
        
        return stock_data
    except Exception as e:
        print(f"获取股票 {stock_code} 数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return {} 