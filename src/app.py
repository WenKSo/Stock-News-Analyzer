import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import numpy as np

# 导入自定义模块
from news_analyzer import analyze_news
from stock_data import get_stock_data
from stock_analyzer import analyze_stock

# 设置页面标题
st.set_page_config(page_title="股票新闻分析系统", layout="wide")

# 页面标题
st.title("股票新闻分析与投资建议系统")

# 侧边栏
st.sidebar.header("操作面板")
option = st.sidebar.selectbox(
    "选择操作",
    ["分析新闻数据", "手动输入新闻"]
)

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
    st.header("分析已爬取的新闻数据")
    
    # 获取新闻数据文件路径
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, '..', 'data', 'news_data.json')
    
    # 加载新闻数据
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        # 显示新闻列表
        st.subheader(f"已加载 {len(news_data)} 条新闻")
        
        # 创建新闻选择器
        news_titles = [news.get('title', f"新闻 {i+1}") for i, news in enumerate(news_data)]
        selected_news_index = st.selectbox("选择要分析的新闻", range(len(news_titles)), format_func=lambda x: news_titles[x])
        
        # 显示选中的新闻内容
        selected_news = news_data[selected_news_index]
        st.subheader("新闻内容")
        st.write(selected_news.get('content', '无内容'))
        
        # 分析按钮
        if st.button("分析该新闻"):
            with st.spinner("正在分析新闻并提取相关股票..."):
                news_text = selected_news.get('content', '')
                stock_codes = analyze_news(news_text)
                
                if stock_codes == "无相关上市公司":
                    st.warning("该新闻没有相关的已上市公司")
                else:
                    st.success(f"找到相关股票代码: {stock_codes}")
                    
                    # 处理可能的多个股票代码
                    for stock_code in stock_codes.split(','):
                        stock_code = stock_code.strip()
                        if not stock_code:
                            continue
                        
                        with st.spinner(f"正在获取股票 {stock_code} 的数据..."):
                            stock_data = get_stock_data(stock_code)
                            
                            if not stock_data or not stock_data.get('basic', {}).get('name', ''):
                                st.error(f"未能获取到股票 {stock_code} 的有效数据")
                                continue
                            
                            # 显示股票基本信息
                            st.subheader(f"股票信息: {stock_data['basic']['name']} ({stock_code})")
                            
                            # 创建两列布局
                            col1, col2 = st.columns(2)
                            
                            # 基本信息表格
                            with col1:
                                st.write("**基本信息**")
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
                            
                            # 价格信息表格
                            with col2:
                                st.write("**价格信息**")
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
                            
                            # 财务指标可视化
                            st.write("**关键财务指标**")
                            
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
                                fig = px.bar(
                                    x=financial_data["指标"],
                                    y=financial_values,
                                    title="关键财务指标",
                                    labels={"x": "指标", "y": "数值"}
                                )
                                st.plotly_chart(fig)
                            except Exception as e:
                                st.error(f"创建财务指标图表时出错: {e}")
                                # 显示原始数据表格
                                st.write("财务指标原始数据:")
                                st.dataframe(pd.DataFrame(financial_data))
                            
                            # 分析结果
                            with st.spinner("正在分析股票投资价值..."):
                                analysis_result = analyze_stock(news_text, stock_data)
                                st.subheader("投资分析结果")
                                st.write(analysis_result)
                                
                                # 提取投资建议关键词
                                if "建议买入" in analysis_result:
                                    st.success("✅ 建议买入")
                                elif "不建议买入" in analysis_result:
                                    st.error("❌ 不建议买入")
                                elif "建议观望" in analysis_result:
                                    st.warning("⚠️ 建议观望")
    except Exception as e:
        st.error(f"加载新闻数据出错: {e}")
        import traceback
        st.error(traceback.format_exc())

else:  # 手动输入新闻
    st.header("手动输入新闻进行分析")
    
    # 文本输入区
    news_text = st.text_area("请输入新闻内容", height=200)
    
    # 分析按钮
    if st.button("分析新闻"):
        if not news_text:
            st.warning("请输入新闻内容")
        else:
            with st.spinner("正在分析新闻并提取相关股票..."):
                stock_codes = analyze_news(news_text)
                
                if stock_codes == "无相关上市公司":
                    st.warning("该新闻没有相关的已上市公司")
                else:
                    st.success(f"找到相关股票代码: {stock_codes}")
                    
                    # 处理可能的多个股票代码
                    for stock_code in stock_codes.split(','):
                        stock_code = stock_code.strip()
                        if not stock_code:
                            continue
                        
                        with st.spinner(f"正在获取股票 {stock_code} 的数据..."):
                            stock_data = get_stock_data(stock_code)
                            
                            if not stock_data or not stock_data.get('basic', {}).get('name', ''):
                                st.error(f"未能获取到股票 {stock_code} 的有效数据")
                                continue
                            
                            # 显示股票基本信息
                            st.subheader(f"股票信息: {stock_data['basic']['name']} ({stock_code})")
                            
                            # 创建两列布局
                            col1, col2 = st.columns(2)
                            
                            # 基本信息表格
                            with col1:
                                st.write("**基本信息**")
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
                            
                            # 价格信息表格
                            with col2:
                                st.write("**价格信息**")
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
                            
                            # 分析结果
                            with st.spinner("正在分析股票投资价值..."):
                                analysis_result = analyze_stock(news_text, stock_data)
                                st.subheader("投资分析结果")
                                st.write(analysis_result)
                                
                                # 提取投资建议关键词
                                if "建议买入" in analysis_result:
                                    st.success("✅ 建议买入")
                                elif "不建议买入" in analysis_result:
                                    st.error("❌ 不建议买入")
                                elif "建议观望" in analysis_result:
                                    st.warning("⚠️ 建议观望") 