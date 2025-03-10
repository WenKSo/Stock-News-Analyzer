import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import numpy as np
import random

# 导入自定义模块
from news_analyzer import analyze_news
from stock_data import get_stock_data
from stock_analyzer import analyze_stock

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
                stock_codes = analyze_news(news_text)
                
                if stock_codes == "无相关上市公司":
                    st.warning("⚠️ 该新闻没有相关的已上市公司")
                else:
                    st.success(f"✅ 找到相关股票代码: {stock_codes}")
                    
                    # 处理可能的多个股票代码
                    for stock_code in stock_codes.split(','):
                        stock_code = stock_code.strip()
                        if not stock_code:
                            continue
                        
                        with st.spinner(f"🔄 正在获取股票 {stock_code} 的数据..."):
                            stock_data = get_stock_data(stock_code)
                            
                            if not stock_data or not stock_data.get('basic', {}).get('name', ''):
                                st.error(f"❌ 未能获取到股票 {stock_code} 的有效数据")
                                continue
                            
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
                                st.table(basic_df)
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 价格信息表格
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
                                    "项目": ["最新收盘价", "涨跌幅", "市盈率(PE)", "市净率(PB)"],
                                    "数值": [
                                        format_value(stock_data['price']['close']),
                                        pct_chg_str,
                                        format_value(stock_data['price']['pe']),
                                        format_value(stock_data['price']['pb'])
                                    ]
                                })
                                st.table(price_df)
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 财务指标可视化
                            st.markdown("### 📊 关键财务指标")
                            
                            # 创建财务指标数据
                            financial_data = {
                                "指标": ["每股收益(EPS)", "净资产收益率(ROE)", "毛利率", "净利率", "资产负债率"],
                                "数值": [
                                    format_value(stock_data['financial_indicator']['eps']),
                                    format_value(stock_data['financial_indicator']['roe']),
                                    format_value(stock_data['financial_indicator']['grossprofit_margin']),
                                    format_value(stock_data['financial_indicator']['netprofit_margin']),
                                    format_value(stock_data['financial_indicator']['debt_to_assets'])
                                ]
                            }
                            
                            # 转换为数值类型进行绘图
                            try:
                                financial_values = []
                                for val in financial_data["数值"]:
                                    if isinstance(val, str) and val != '未知':
                                        # 移除百分号并转换为浮点数
                                        val = val.replace('%', '')
                                        try:
                                            financial_values.append(float(val))
                                        except ValueError:
                                            financial_values.append(0)
                                    elif val == '未知':
                                        financial_values.append(0)
                                    else:
                                        financial_values.append(float(val))
                                
                                # 创建条形图
                                colors = ['#1E88E5', '#43A047', '#FFB300', '#E53935', '#5E35B1']
                                fig = px.bar(
                                    x=financial_data["指标"],
                                    y=financial_values,
                                    title="关键财务指标",
                                    labels={"x": "指标", "y": "数值"},
                                    color=financial_data["指标"],
                                    color_discrete_sequence=colors
                                )
                                fig.update_layout(
                                    plot_bgcolor='rgba(240,240,240,0.2)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font=dict(size=14),
                                    title_font_size=20
                                )
                                st.plotly_chart(fig)
                            except Exception as e:
                                st.error(f"创建财务指标图表时出错: {e}")
                                # 显示原始数据表格
                                st.write("财务指标原始数据:")
                                st.dataframe(pd.DataFrame(financial_data))
                            
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
                stock_codes = analyze_news(news_text)
                
                if stock_codes == "无相关上市公司":
                    st.warning("⚠️ 该新闻没有相关的已上市公司")
                else:
                    st.success(f"✅ 找到相关股票代码: {stock_codes}")
                    
                    # 处理可能的多个股票代码
                    for stock_code in stock_codes.split(','):
                        stock_code = stock_code.strip()
                        if not stock_code:
                            continue
                        
                        with st.spinner(f"🔄 正在获取股票 {stock_code} 的数据..."):
                            stock_data = get_stock_data(stock_code)
                            
                            if not stock_data or not stock_data.get('basic', {}).get('name', ''):
                                st.error(f"❌ 未能获取到股票 {stock_code} 的有效数据")
                                continue
                            
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
                                st.table(basic_df)
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 价格信息表格
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
                                    "项目": ["最新收盘价", "涨跌幅", "市盈率(PE)", "市净率(PB)"],
                                    "数值": [
                                        format_value(stock_data['price']['close']),
                                        pct_chg_str,
                                        format_value(stock_data['price']['pe']),
                                        format_value(stock_data['price']['pb'])
                                    ]
                                })
                                st.table(price_df)
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

# 添加页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>© 2024 股票新闻分析与投资建议系统 | 基于AI的智能投资分析工具</p>
</div>
""", unsafe_allow_html=True) 