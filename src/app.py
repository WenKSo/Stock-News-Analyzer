import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import numpy as np
import random
import sys

# 获取当前文件的绝对路径，然后获取其上一级目录（项目根目录）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入自定义模块
from news_analyzer import analyze_news
from stock_data import get_stock_data
from stock_analyzer import analyze_stock
from dingtalk_bot import DingTalkBot
from config.config import DINGTALK_WEBHOOK, DINGTALK_SECRET

# 初始化钉钉机器人
dingtalk_bot = DingTalkBot(DINGTALK_WEBHOOK, DINGTALK_SECRET)

# 设置页面标题和配置
st.set_page_config(
    page_title="股票新闻分析系统", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': "https://www.example.com/bug",
        'About': "# 股票新闻分析与投资建议系统\n 基于AI的股票分析工具"
    }
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.8rem;
        color: #43A047;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #43A047;
        padding-bottom: 0.5rem;
    }
    .news-container {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .stock-info-card {
        background-color: #F1F8E9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #43A047;
        margin-bottom: 1rem;
    }
    .analysis-result {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FFB300;
        margin-top: 1rem;
    }
    .buy-recommendation {
        color: #2E7D32;
        font-weight: bold;
        font-size: 1.2rem;
        background-color: #C8E6C9;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    .sell-recommendation {
        color: #C62828;
        font-weight: bold;
        font-size: 1.2rem;
        background-color: #FFCDD2;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    .hold-recommendation {
        color: #F57C00;
        font-weight: bold;
        font-size: 1.2rem;
        background-color: #FFE0B2;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    .sidebar .sidebar-content {
        background-color: #ECEFF1;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0D47A1;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="main-header">📊 股票新闻分析与投资建议系统</h1>', unsafe_allow_html=True)

# 侧边栏
st.sidebar.image("https://img.freepik.com/free-vector/stock-market-concept_23-2148604937.jpg?w=826&t=st=1709574372~exp=1709574972~hmac=e254d49c8c5d7a6e9f86f5e3d7d5f5c6a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a", use_column_width=True)
st.sidebar.header("🛠️ 操作面板")
option = st.sidebar.selectbox(
    "选择操作",
    ["分析新闻数据", "手动输入新闻"]
)

# 添加一些装饰性元素
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 市场概览")
market_indices = {
    "上证指数": random.uniform(3000, 3500),
    "深证成指": random.uniform(10000, 12000),
    "创业板指": random.uniform(2000, 2500),
    "科创50": random.uniform(900, 1100)
}

# 显示市场指数
for index, value in market_indices.items():
    change = random.uniform(-2, 2)
    color = "green" if change > 0 else "red"
    st.sidebar.markdown(f"**{index}**: {value:.2f} <span style='color:{color};'>({change:+.2f}%)</span>", unsafe_allow_html=True)

# 辅助函数：处理可能包含百分号的值
def format_value(value):
    if isinstance(value, str) and '%' in value:
        return value  # 保持字符串格式，包含百分号
    elif isinstance(value, float) and np.isnan(value):
        return '未知'  # 处理 NaN 值
    elif isinstance(value, (int, float)):
        return value  # 保持数值格式
    else:
        return str(value)  # 其他情况转为字符串

# 根据选择显示不同的内容
if option == "分析新闻数据":
    st.markdown('<h2 class="sub-header">📰 分析已爬取的新闻数据</h2>', unsafe_allow_html=True)
    
    # 获取新闻数据文件路径
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, '..', 'data', 'news_data.json')
    
    # 加载新闻数据
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        # 显示新闻列表
        st.markdown(f"### 已加载 {len(news_data)} 条新闻")
        
        # 创建新闻选择器
        news_titles = [news.get('title', f"新闻 {i+1}") for i, news in enumerate(news_data)]
        selected_news_index = st.selectbox("选择要分析的新闻", range(len(news_titles)), format_func=lambda x: news_titles[x])
        
        # 显示选中的新闻内容
        selected_news = news_data[selected_news_index]
        st.markdown("### 新闻内容")
        st.markdown(f'<div class="news-container">{selected_news.get("content", "无内容")}</div>', unsafe_allow_html=True)
        
        # 分析按钮
        if st.button("🔍 分析该新闻"):
            with st.spinner("🔄 正在分析新闻并提取相关股票..."):
                news_text = selected_news.get('content', '')
                result = analyze_news(news_text)
                
                if not result["analyze"]:
                    st.warning(f"⚠️ 新闻重要性等级为{result['importance_level']}（{result['importance_category']}），不进行分析")
                elif result["stock_code"] == "无相关上市公司":
                    st.warning("⚠️ 该新闻没有相关的已上市公司")
                    # 显示行业信息
                    if result["industry_info"]:
                        st.info(f"📊 所属行业: {result['industry_info']['main_category']} - {result['industry_info']['sub_category']} (相关度: {result['industry_info']['relevance_score']})")
                else:
                    # 显示分析结果
                    importance_level = result["importance_level"]
                    importance_category = result["importance_category"]
                    industry_info = result["industry_info"]
                    stock_code = result["stock_code"]
                    
                    st.success(f"✅ 找到相关股票代码: {stock_code}")
                    st.info(f"📊 新闻重要性: {importance_level}级 ({importance_category})")
                    st.info(f"📊 所属行业: {industry_info['main_category']} - {industry_info['sub_category']} (相关度: {industry_info['relevance_score']})")
                    
                    with st.spinner(f"🔄 正在获取股票 {stock_code} 的数据..."):
                        stock_data = get_stock_data(stock_code)
                        
                        if not stock_data or not stock_data.get('basic', {}).get('name', ''):
                            st.error(f"❌ 未能获取到股票 {stock_code} 的有效数据")
                        else:
                            # 显示股票基本信息
                            st.markdown(f'<h3 class="sub-header">🏢 股票信息: {stock_data["basic"]["name"]} ({stock_code})</h3>', unsafe_allow_html=True)
                            
                            # 创建两列布局
                            col1, col2 = st.columns(2)
                            
                            # 基本信息表格
                            with col1:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**📋 基本信息**")
                                basic_df = pd.DataFrame({
                                    "项目": ["股票代码", "股票名称", "所属行业", "上市日期"],
                                    "数值": [
                                        stock_data['basic']['ts_code'],
                                        stock_data['basic']['name'],
                                        stock_data['basic']['industry'],
                                        stock_data['basic']['list_date']
                                    ]
                                })
                                st.table(basic_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 实时市场数据区域
                            st.markdown("### 📈 实时市场数据")
                            col2, col3, col4 = st.columns(3)
                            
                            # 价格信息合并到实时市场数据
                            with col2:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**💰 价格信息**")
                                # 处理百分号问题
                                pct_chg = stock_data['price']['pct_chg']
                                if isinstance(pct_chg, (int, float)):
                                    pct_chg_str = f"{pct_chg}%"
                                else:
                                    pct_chg_str = pct_chg
                                
                                price_df = pd.DataFrame({
                                    "项目": ["最新价", "涨跌额", "涨跌幅", "今日开盘", "最高价", "最低价"],
                                    "数值": [
                                        format_value(stock_data['price']['close']),
                                        format_value(stock_data['price']['change']),
                                        pct_chg_str,
                                        format_value(stock_data['price']['open']),
                                        format_value(stock_data['price']['high']),
                                        format_value(stock_data['price']['low'])
                                    ]
                                })
                                st.table(price_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col3:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**🔍 市场表现**")
                                market_df = pd.DataFrame({
                                    "项目": ["成交量", "成交额", "市盈率(TTM)", "市净率", "市值/资产净值", "流通值"],
                                    "数值": [
                                        format_value(stock_data['price'].get('成交量', '未知')),
                                        format_value(stock_data['price'].get('成交额', '未知')),
                                        format_value(stock_data['price']['pe']),
                                        format_value(stock_data['price']['pb']),
                                        format_value(stock_data['price']['total_mv']),
                                        format_value(stock_data['price']['circ_mv'])
                                    ]
                                })
                                st.table(market_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col4:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**📅 52周表现**")
                                performance_df = pd.DataFrame({
                                    "项目": ["52周最高", "52周最低", "今年以来涨幅", "振幅", "昨收", "周转率"],
                                    "数值": [
                                        format_value(stock_data['price'].get('52周最高', '未知')),
                                        format_value(stock_data['price'].get('52周最低', '未知')),
                                        format_value(stock_data['price'].get('今年以来涨幅', '未知')),
                                        format_value(stock_data['price'].get('振幅', '未知')),
                                        format_value(stock_data['price'].get('昨收', '未知')),
                                        format_value(stock_data['price'].get('周转率', '未知'))
                                    ]
                                })
                                st.table(performance_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 财务指标可视化
                            st.markdown("### 📊 关键财务指标")
                            
                            # 创建财务指标数据
                            financial_data = {
                                "指标": [
                                    "每股收益(EPS)", 
                                    "净资产收益率(ROE)", 
                                    "毛利率", 
                                    "净利率", 
                                    "资产负债率",
                                    "每股净资产",
                                    "营业收入增长率",
                                    "净利润增长率",
                                    "流动比率",
                                    "速动比率"
                                ],
                                "数值": [
                                    format_value(stock_data['financial_indicator'].get('eps', '未知')),
                                    format_value(stock_data['financial_indicator'].get('roe', '未知')),
                                    format_value(stock_data['financial_indicator'].get('gross_profit_margin', '未知')),
                                    format_value(stock_data['financial_indicator'].get('net_profit_margin', '未知')),
                                    format_value(stock_data['financial_indicator'].get('debt_to_assets', '未知')),
                                    format_value(stock_data['financial_indicator'].get('bps', '未知')),
                                    format_value(stock_data['financial_indicator'].get('revenue_growth', '未知')),
                                    format_value(stock_data['financial_indicator'].get('profit_growth', '未知')),
                                    format_value(stock_data['financial_indicator'].get('current_ratio', '未知')),
                                    format_value(stock_data['financial_indicator'].get('quick_ratio', '未知'))
                                ]
                            }
                            
                            # 检查是否为金融企业（存在金融特有指标）
                            if stock_data['financial_indicator'].get('capital_adequacy', '未知') != '未知' or \
                               stock_data['financial_indicator'].get('net_interest_margin', '未知') != '未知':
                                financial_data["指标"].extend(["资本充足率", "净息差"])
                                financial_data["数值"].extend([
                                    format_value(stock_data['financial_indicator'].get('capital_adequacy', '未知')),
                                    format_value(stock_data['financial_indicator'].get('net_interest_margin', '未知'))
                                ])
                            
                            # 使用表格直接显示财务指标
                            st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                            financial_df = pd.DataFrame(financial_data)
                            st.table(financial_df.set_index('指标'))
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 分析结果
                            with st.spinner("🧠 正在分析股票投资价值..."):
                                analysis_result = analyze_stock(news_text, stock_data)
                                st.markdown('<h3 class="sub-header">💡 投资分析结果</h3>', unsafe_allow_html=True)
                                st.markdown(f'<div class="analysis-result">{analysis_result.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                                
                                # 提取投资建议关键词
                                if "建议买入" in analysis_result:
                                    st.markdown('<div class="buy-recommendation">✅ 建议买入</div>', unsafe_allow_html=True)
                                elif "不建议买入" in analysis_result:
                                    st.markdown('<div class="sell-recommendation">❌ 不建议买入</div>', unsafe_allow_html=True)
                                elif "建议观望" in analysis_result:
                                    st.markdown('<div class="hold-recommendation">⚠️ 建议观望</div>', unsafe_allow_html=True)
                                
                                # 发送到钉钉机器人
                                title = f"股票分析报告 - {stock_data['basic']['name']}({stock_code})"
                                # 先处理换行符
                                formatted_analysis = analysis_result.replace('\n', '\n\n')
                                content = f'''### {title}
                                
#### 新闻内容
{news_text[:200]}...

#### 基本信息
- 股票代码：{stock_code}
- 股票名称：{stock_data['basic']['name']}
- 所属行业：{stock_data['basic'].get('industry', '未知')}
- 上市日期：{stock_data['basic'].get('list_date', '未知')}

#### 价格信息
- 最新价格：{stock_data['price'].get('close', '未知')}
- 涨跌额：{stock_data['price'].get('change', '未知')}
- 涨跌幅：{stock_data['price'].get('pct_chg', '未知')}%
- 今日开盘：{stock_data['price'].get('open', '未知')}
- 最高价：{stock_data['price'].get('high', '未知')}
- 最低价：{stock_data['price'].get('low', '未知')}
- 市盈率(TTM)：{stock_data['price'].get('pe', '未知')}
- 市净率：{stock_data['price'].get('pb', '未知')}

#### 市场表现
- 成交量：{stock_data['price'].get('成交量', '未知')}
- 成交额：{stock_data['price'].get('成交额', '未知')}
- 市值：{stock_data['price'].get('total_mv', '未知')}
- 52周最高：{stock_data['price'].get('52周最高', '未知')}
- 52周最低：{stock_data['price'].get('52周最低', '未知')}
- 今年以来涨幅：{stock_data['price'].get('今年以来涨幅', '未知')}

#### 投资分析结果
{formatted_analysis}
'''
                                # 发送消息
                                if dingtalk_bot.send_markdown(title, content):
                                    st.success("✅ 分析报告已发送到钉钉群")
                                else:
                                    st.error("❌ 发送到钉钉群失败，请检查配置")
    except Exception as e:
        st.error(f"加载新闻数据出错: {e}")
        import traceback
        st.error(traceback.format_exc())

else:  # 手动输入新闻
    st.markdown('<h2 class="sub-header">✍️ 手动输入新闻进行分析</h2>', unsafe_allow_html=True)
    
    # 文本输入区
    news_text = st.text_area("请输入新闻内容", height=200)
    
    # 分析按钮
    if st.button("🔍 分析新闻"):
        if not news_text:
            st.warning("⚠️ 请输入新闻内容")
        else:
            with st.spinner("🔄 正在分析新闻并提取相关股票..."):
                result = analyze_news(news_text)
                
                if not result["analyze"]:
                    st.warning(f"⚠️ 新闻重要性等级为{result['importance_level']}（{result['importance_category']}），不进行分析")
                elif result["stock_code"] == "无相关上市公司":
                    st.warning("⚠️ 该新闻没有相关的已上市公司")
                    # 显示行业信息
                    if result["industry_info"]:
                        st.info(f"📊 所属行业: {result['industry_info']['main_category']} - {result['industry_info']['sub_category']} (相关度: {result['industry_info']['relevance_score']})")
                else:
                    # 显示分析结果
                    importance_level = result["importance_level"]
                    importance_category = result["importance_category"]
                    industry_info = result["industry_info"]
                    stock_code = result["stock_code"]
                    
                    st.success(f"✅ 找到相关股票代码: {stock_code}")
                    st.info(f"📊 新闻重要性: {importance_level}级 ({importance_category})")
                    st.info(f"📊 所属行业: {industry_info['main_category']} - {industry_info['sub_category']} (相关度: {industry_info['relevance_score']})")
                    
                    with st.spinner(f"🔄 正在获取股票 {stock_code} 的数据..."):
                        stock_data = get_stock_data(stock_code)
                        
                        if not stock_data or not stock_data.get('basic', {}).get('name', ''):
                            st.error(f"❌ 未能获取到股票 {stock_code} 的有效数据")
                        else:
                            # 显示股票基本信息
                            st.markdown(f'<h3 class="sub-header">🏢 股票信息: {stock_data["basic"]["name"]} ({stock_code})</h3>', unsafe_allow_html=True)
                            
                            # 创建两列布局
                            col1, col2 = st.columns(2)
                            
                            # 基本信息表格
                            with col1:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**📋 基本信息**")
                                basic_df = pd.DataFrame({
                                    "项目": ["股票代码", "股票名称", "所属行业", "上市日期"],
                                    "数值": [
                                        stock_data['basic']['ts_code'],
                                        stock_data['basic']['name'],
                                        stock_data['basic']['industry'],
                                        stock_data['basic']['list_date']
                                    ]
                                })
                                st.table(basic_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 实时市场数据区域
                            st.markdown("### 📈 实时市场数据")
                            col2, col3, col4 = st.columns(3)
                            
                            # 价格信息合并到实时市场数据
                            with col2:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**💰 价格信息**")
                                # 处理百分号问题
                                pct_chg = stock_data['price']['pct_chg']
                                if isinstance(pct_chg, (int, float)):
                                    pct_chg_str = f"{pct_chg}%"
                                else:
                                    pct_chg_str = pct_chg
                                
                                price_df = pd.DataFrame({
                                    "项目": ["最新价", "涨跌额", "涨跌幅", "今日开盘", "最高价", "最低价"],
                                    "数值": [
                                        format_value(stock_data['price']['close']),
                                        format_value(stock_data['price']['change']),
                                        pct_chg_str,
                                        format_value(stock_data['price']['open']),
                                        format_value(stock_data['price']['high']),
                                        format_value(stock_data['price']['low'])
                                    ]
                                })
                                st.table(price_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col3:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**🔍 市场表现**")
                                market_df = pd.DataFrame({
                                    "项目": ["成交量", "成交额", "市盈率(TTM)", "市净率", "市值/资产净值", "流通值"],
                                    "数值": [
                                        format_value(stock_data['price'].get('成交量', '未知')),
                                        format_value(stock_data['price'].get('成交额', '未知')),
                                        format_value(stock_data['price']['pe']),
                                        format_value(stock_data['price']['pb']),
                                        format_value(stock_data['price']['total_mv']),
                                        format_value(stock_data['price']['circ_mv'])
                                    ]
                                })
                                st.table(market_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col4:
                                st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                                st.markdown("**📅 52周表现**")
                                performance_df = pd.DataFrame({
                                    "项目": ["52周最高", "52周最低", "今年以来涨幅", "振幅", "昨收", "周转率"],
                                    "数值": [
                                        format_value(stock_data['price'].get('52周最高', '未知')),
                                        format_value(stock_data['price'].get('52周最低', '未知')),
                                        format_value(stock_data['price'].get('今年以来涨幅', '未知')),
                                        format_value(stock_data['price'].get('振幅', '未知')),
                                        format_value(stock_data['price'].get('昨收', '未知')),
                                        format_value(stock_data['price'].get('周转率', '未知'))
                                    ]
                                })
                                st.table(performance_df.set_index('项目'))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 财务指标可视化
                            st.markdown("### 📊 关键财务指标")
                            
                            # 创建财务指标数据
                            financial_data = {
                                "指标": [
                                    "每股收益(EPS)", 
                                    "净资产收益率(ROE)", 
                                    "毛利率", 
                                    "净利率", 
                                    "资产负债率",
                                    "每股净资产",
                                    "营业收入增长率",
                                    "净利润增长率",
                                    "流动比率",
                                    "速动比率"
                                ],
                                "数值": [
                                    format_value(stock_data['financial_indicator'].get('eps', '未知')),
                                    format_value(stock_data['financial_indicator'].get('roe', '未知')),
                                    format_value(stock_data['financial_indicator'].get('gross_profit_margin', '未知')),
                                    format_value(stock_data['financial_indicator'].get('net_profit_margin', '未知')),
                                    format_value(stock_data['financial_indicator'].get('debt_to_assets', '未知')),
                                    format_value(stock_data['financial_indicator'].get('bps', '未知')),
                                    format_value(stock_data['financial_indicator'].get('revenue_growth', '未知')),
                                    format_value(stock_data['financial_indicator'].get('profit_growth', '未知')),
                                    format_value(stock_data['financial_indicator'].get('current_ratio', '未知')),
                                    format_value(stock_data['financial_indicator'].get('quick_ratio', '未知'))
                                ]
                            }
                            
                            # 检查是否为金融企业（存在金融特有指标）
                            if stock_data['financial_indicator'].get('capital_adequacy', '未知') != '未知' or \
                               stock_data['financial_indicator'].get('net_interest_margin', '未知') != '未知':
                                financial_data["指标"].extend(["资本充足率", "净息差"])
                                financial_data["数值"].extend([
                                    format_value(stock_data['financial_indicator'].get('capital_adequacy', '未知')),
                                    format_value(stock_data['financial_indicator'].get('net_interest_margin', '未知'))
                                ])
                            
                            # 使用表格直接显示财务指标
                            st.markdown('<div class="stock-info-card">', unsafe_allow_html=True)
                            financial_df = pd.DataFrame(financial_data)
                            st.table(financial_df.set_index('指标'))
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 分析结果
                            with st.spinner("🧠 正在分析股票投资价值..."):
                                analysis_result = analyze_stock(news_text, stock_data)
                                st.markdown('<h3 class="sub-header">💡 投资分析结果</h3>', unsafe_allow_html=True)
                                st.markdown(f'<div class="analysis-result">{analysis_result.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                                
                                # 提取投资建议关键词
                                if "建议买入" in analysis_result:
                                    st.markdown('<div class="buy-recommendation">✅ 建议买入</div>', unsafe_allow_html=True)
                                elif "不建议买入" in analysis_result:
                                    st.markdown('<div class="sell-recommendation">❌ 不建议买入</div>', unsafe_allow_html=True)
                                elif "建议观望" in analysis_result:
                                    st.markdown('<div class="hold-recommendation">⚠️ 建议观望</div>', unsafe_allow_html=True)
                                
                                # 发送到钉钉机器人
                                title = f"股票分析报告 - {stock_data['basic']['name']}({stock_code})"
                                # 先处理换行符
                                formatted_analysis = analysis_result.replace('\n', '\n\n')
                                content = f'''### {title}
                                
#### 新闻内容
{news_text[:200]}...

#### 基本信息
- 股票代码：{stock_code}
- 股票名称：{stock_data['basic']['name']}
- 所属行业：{stock_data['basic'].get('industry', '未知')}
- 上市日期：{stock_data['basic'].get('list_date', '未知')}

#### 价格信息
- 最新价格：{stock_data['price'].get('close', '未知')}
- 涨跌额：{stock_data['price'].get('change', '未知')}
- 涨跌幅：{stock_data['price'].get('pct_chg', '未知')}%
- 今日开盘：{stock_data['price'].get('open', '未知')}
- 最高价：{stock_data['price'].get('high', '未知')}
- 最低价：{stock_data['price'].get('low', '未知')}
- 市盈率(TTM)：{stock_data['price'].get('pe', '未知')}
- 市净率：{stock_data['price'].get('pb', '未知')}

#### 市场表现
- 成交量：{stock_data['price'].get('成交量', '未知')}
- 成交额：{stock_data['price'].get('成交额', '未知')}
- 市值：{stock_data['price'].get('total_mv', '未知')}
- 52周最高：{stock_data['price'].get('52周最高', '未知')}
- 52周最低：{stock_data['price'].get('52周最低', '未知')}
- 今年以来涨幅：{stock_data['price'].get('今年以来涨幅', '未知')}

#### 投资分析结果
{formatted_analysis}
'''
                                # 发送消息
                                if dingtalk_bot.send_markdown(title, content):
                                    st.success("✅ 分析报告已发送到钉钉群")
                                else:
                                    st.error("❌ 发送到钉钉群失败，请检查配置")

# 添加页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>© 2024 股票新闻分析与投资建议系统 | 基于AI的智能投资分析工具</p>
</div>
""", unsafe_allow_html=True) 