import os
import matplotlib.pyplot as plt
from datetime import datetime

def visualize_stock_data(stock_data, news_text, analysis_result, output_dir='../output'):
    """
    将股票数据和分析结果可视化，并保存为HTML和图片文件
    """
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成唯一的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stock_code = stock_data['basic']['ts_code']
    stock_name = stock_data['basic']['name']
    base_filename = f"{output_dir}/{stock_code}_{timestamp}"
    
    # 创建HTML报告 - 使用三重引号和普通字符串，然后用format方法替换变量
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>股票分析报告 - {stock_name}({stock_code})</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .section {{ margin-bottom: 30px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .news {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
            .analysis {{ background-color: #f0f8ff; padding: 15px; border-radius: 5px; }}
            .buy {{ color: green; font-weight: bold; }}
            .sell {{ color: red; font-weight: bold; }}
            .hold {{ color: orange; font-weight: bold; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>股票分析报告</h1>
                <h2>{stock_name} ({stock_code})</h2>
                <p>生成时间: {timestamp}</p>
            </div>
            
            <div class="section">
                <h3>新闻内容</h3>
                <div class="news">
                    <p>{news_text}</p>
                </div>
            </div>
            
            <div class="section">
                <h3>基本信息</h3>
                <table>
                    <tr><th>股票代码</th><td>{ts_code}</td></tr>
                    <tr><th>股票名称</th><td>{name}</td></tr>
                    <tr><th>所属行业</th><td>{industry}</td></tr>
                    <tr><th>上市日期</th><td>{list_date}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h3>价格信息</h3>
                <table>
                    <tr><th>最新收盘价</th><td>{close}</td></tr>
                    <tr><th>涨跌幅</th><td>{pct_chg}%</td></tr>
                    <tr><th>市盈率(PE)</th><td>{pe}</td></tr>
                    <tr><th>市净率(PB)</th><td>{pb}</td></tr>
                    <tr><th>总市值</th><td>{total_mv}</td></tr>
                    <tr><th>流通市值</th><td>{circ_mv}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h3>财务指标</h3>
                <table>
                    <tr><th>每股收益(EPS)</th><td>{eps}</td></tr>
                    <tr><th>净资产收益率(ROE)</th><td>{roe}</td></tr>
                    <tr><th>每股净资产</th><td>{bps}</td></tr>
                    <tr><th>毛利率</th><td>{grossprofit_margin}</td></tr>
                    <tr><th>净利率</th><td>{netprofit_margin}</td></tr>
                    <tr><th>资产负债率</th><td>{debt_to_assets}</td></tr>
                </table>
                <img src="financial_indicators_{img_timestamp}.png" alt="财务指标图表">
            </div>
            
            <div class="section">
                <h3>投资分析结果</h3>
                <div class="analysis">
                    <p>{analysis_html}</p>
                    <p class="{recommendation_class}">
                        {recommendation_text}
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # 准备替换变量
    formatted_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    analysis_html = analysis_result.replace('\n', '<br>')
    
    # 确定推荐类别和文本
    if '建议买入' in analysis_result:
        recommendation_class = "buy"
        recommendation_text = "✅ 建议买入"
    elif '不建议买入' in analysis_result:
        recommendation_class = "sell"
        recommendation_text = "❌ 不建议买入"
    else:
        recommendation_class = "hold"
        recommendation_text = "⚠️ 建议观望"
    
    # 使用format方法替换变量
    html_content = html_content.format(
        stock_name=stock_name,
        stock_code=stock_code,
        timestamp=formatted_timestamp,
        news_text=news_text,
        ts_code=stock_data['basic']['ts_code'],
        name=stock_data['basic']['name'],
        industry=stock_data['basic']['industry'],
        list_date=stock_data['basic']['list_date'],
        close=stock_data['price']['close'],
        pct_chg=stock_data['price']['pct_chg'],
        pe=stock_data['price']['pe'],
        pb=stock_data['price']['pb'],
        total_mv=stock_data['price']['total_mv'],
        circ_mv=stock_data['price']['circ_mv'],
        eps=stock_data['financial_indicator'].get('eps', '未知'),
        roe=stock_data['financial_indicator'].get('roe', '未知'),
        bps=stock_data['financial_indicator'].get('bps', '未知'),
        grossprofit_margin=stock_data['financial_indicator'].get('gross_profit_margin', '未知'),
        netprofit_margin=stock_data['financial_indicator'].get('net_profit_margin', '未知'),
        debt_to_assets=stock_data['financial_indicator'].get('debt_to_assets', '未知'),
        img_timestamp=timestamp,
        analysis_html=analysis_html,
        recommendation_class=recommendation_class,
        recommendation_text=recommendation_text
    )
    
    # 保存HTML报告
    html_file = f"{base_filename}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 创建财务指标图表
    try:
        # 准备数据
        indicators = ["EPS", "ROE", "毛利率", "净利率", "资产负债率"]
        values = [
            float(str(stock_data['financial_indicator'].get('eps', '未知')).replace('%', '')) if stock_data['financial_indicator'].get('eps', '未知') != '未知' else 0,
            float(str(stock_data['financial_indicator'].get('roe', '未知')).replace('%', '')) if stock_data['financial_indicator'].get('roe', '未知') != '未知' else 0,
            float(str(stock_data['financial_indicator'].get('gross_profit_margin', '未知')).replace('%', '')) if stock_data['financial_indicator'].get('gross_profit_margin', '未知') != '未知' else 0,
            float(str(stock_data['financial_indicator'].get('net_profit_margin', '未知')).replace('%', '')) if stock_data['financial_indicator'].get('net_profit_margin', '未知') != '未知' else 0,
            float(str(stock_data['financial_indicator'].get('debt_to_assets', '未知')).replace('%', '')) if stock_data['financial_indicator'].get('debt_to_assets', '未知') != '未知' else 0
        ]
        
        # 创建图表
        plt.figure(figsize=(10, 6))
        bars = plt.bar(indicators, values, color=['blue', 'green', 'orange', 'red', 'purple'])
        
        # 添加数据标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{height:.2f}', 
                    ha='center', va='bottom', fontsize=9)
        
        plt.title(f"{stock_name}({stock_code}) - 关键财务指标")
        plt.xlabel("指标")
        plt.ylabel("数值")
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(f"{output_dir}/financial_indicators_{timestamp}.png")
        plt.close()
        
        print(f"已生成分析报告: {html_file}")
        return html_file
    except Exception as e:
        print(f"创建图表时出错: {e}")
        return html_file

def generate_index_page(results, output_dir='../output'):
    """
    生成索引页面，列出所有分析报告
    """
    if not results:
        return None
    
    index_file = f"{output_dir}/index.html"
    existing_records = []
    
    # 获取当前output目录中所有HTML报告文件
    all_html_files = []
    try:
        for filename in os.listdir(output_dir):
            if filename.endswith('.html') and filename != 'index.html':
                # 分析文件名，提取股票代码和时间戳
                parts = filename.split('_')
                if len(parts) >= 3:
                    stock_code = parts[0]
                    # 提取时间戳信息
                    date_part = parts[-2] if len(parts) >= 2 else ""
                    time_part = parts[-1].replace('.html', '') if len(parts) >= 1 else ""
                    
                    if len(date_part) == 8 and len(time_part) == 6:  # 确保格式为YYYYMMDD_HHMMSS
                        timestamp = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
                    else:
                        timestamp = ""
                    
                    # 尝试从文件中提取股票名称
                    stock_name = ""
                    try:
                        with open(os.path.join(output_dir, filename), 'r', encoding='utf-8') as f:
                            content = f.read()
                            # 简单从HTML标题中提取股票名称
                            import re
                            name_match = re.search(r'<h2>([^(]+)', content)
                            if name_match:
                                stock_name = name_match.group(1).strip()
                    except:
                        stock_name = f"{stock_code}股票"
                    
                    # 如果当前处理的文件不在新结果中，则添加到existing_records
                    if not any(os.path.basename(result['report_file']) == filename for result in results):
                        existing_records.append({
                            'news_index': 999,  # 给旧记录一个大索引号
                            'stock_code': stock_code,
                            'stock_name': stock_name,
                            'report_filename': filename,
                            'timestamp': timestamp
                        })
        
        print(f"在output目录中找到 {len(existing_records)} 个现有报告文件")
    except Exception as e:
        print(f"读取output目录出错: {e}")
    
    # 使用普通字符串和format方法
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>股票分析报告索引</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:hover {{background-color: #f5f5f5;}}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>股票分析报告索引</h1>
            <p>最近更新时间: {timestamp}</p>
            <p>共 {total_reports} 条分析报告</p>
            <table>
                <tr>
                    <th>序号</th>
                    <th>股票代码</th>
                    <th>股票名称</th>
                    <th>报告链接</th>
                    <th>生成时间</th>
                </tr>
    """
    
    # 格式化时间戳
    formatted_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 合并现有记录和新记录
    combined_records = []
    
    # 添加现有记录
    for record in existing_records:
        combined_records.append({
            'news_index': record.get('news_index', 999),
            'stock_code': record.get('stock_code', ''),
            'stock_name': record.get('stock_name', ''),
            'report_filename': record.get('report_filename', ''),
            'timestamp': record.get('timestamp', '')
        })
    
    # 添加新记录
    for result in results:
        report_filename = os.path.basename(result['report_file'])
        # 从文件名中提取时间戳 (格式: stock_code_YYYYMMDD_HHMMSS.html)
        timestamp_parts = report_filename.split('_')
        if len(timestamp_parts) >= 3:
            date_part = timestamp_parts[-2]
            time_part = timestamp_parts[-1].replace('.html', '')
            report_timestamp = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
        else:
            report_timestamp = formatted_timestamp
            
        combined_records.append({
            'news_index': result.get('news_index', 0) + 1,
            'stock_code': result.get('stock_code', ''),
            'stock_name': result.get('stock_name', ''),
            'report_filename': report_filename,
            'timestamp': report_timestamp
        })
    
    # 去除重复记录（以股票代码和报告文件名为依据）
    unique_records = []
    seen = set()
    for record in combined_records:
        key = f"{record['stock_code']}_{record['report_filename']}"
        if key not in seen and record['report_filename']:
            seen.add(key)
            unique_records.append(record)
    
    # 按时间戳排序，最新的在前面
    unique_records.sort(key=lambda x: (x.get('timestamp', '')), reverse=True)
    
    index_html = index_html.format(
        timestamp=formatted_timestamp,
        total_reports=len(unique_records)
    )
    
    # 添加每个结果的行
    for i, record in enumerate(unique_records):
        row_html = """
                <tr>
                    <td>{index}</td>
                    <td>{stock_code}</td>
                    <td>{stock_name}</td>
                    <td><a href="{report_filename}" target="_blank">查看报告</a></td>
                    <td>{timestamp}</td>
                </tr>
        """
        index_html += row_html.format(
            index=i + 1,
            stock_code=record.get('stock_code', ''),
            stock_name=record.get('stock_name', ''),
            report_filename=record.get('report_filename', ''),
            timestamp=record.get('timestamp', '')
        )
    
    # 添加HTML结束标签
    index_html += """
            </table>
        </div>
    </body>
    </html>
    """
    
    # 保存索引页面
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"已生成报告索引页: {index_file}，包含 {len(unique_records)} 条记录")
    return index_file 