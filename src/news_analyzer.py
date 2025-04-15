import os
import sys
from volcenginesdkarkruntime import Ark
import akshare as ak

# 获取当前文件的绝对路径，然后获取其上一级目录（项目根目录）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从config导入常量
from config.config import ARK_API_KEY

# 配置 DeepSeek
client = Ark(
    api_key=ARK_API_KEY,
    timeout=1800,
)

def filter_news_by_importance(news_text):
    """
    对新闻进行重要性分级筛选，只有达到一定等级的新闻才会被分析
    
    重要性等级：
    1级 - 国家政策（最高级别）：政府重大政策、监管措施、规划等
    2级 - 行业重大事件：行业政策调整、重大技术突破、行业格局变化等
    3级 - 公司重大事件：业绩预告、重大合同、重组并购、管理层变动等
    4级 - 普通公司新闻：一般性发展、日常运营、小额合同等
    5级 - 市场传闻（最低级别）：未经证实的消息、小道消息等
    
    返回值：
    - (int, str): 包含重要性等级(1-5)和分类描述的元组
    - 只有等级1-3的新闻会被推荐进一步分析
    """
    prompt = f"""
    请对以下新闻按照重要性和影响力进行分级，分类请严格按照以下标准：
    
    1级 - 国家政策（最高级别）：中央政府、国务院、财政部、央行等发布的重大政策、监管措施、规划、法规等，可能对整个市场或多个行业产生重大影响的政策变动
    
    2级 - 行业重大事件：行业政策调整、重大技术突破、行业格局变化、区域性政策对特定行业的影响等，可能对一个行业或板块产生实质性影响的事件
    
    3级 - 公司重大事件：上市公司业绩预告（尤其是大幅增长或下滑）、重大合同签订、重组并购、管理层重大变动、产品重大创新等，可能对个股价格产生明显影响的公司消息
    
    4级 - 普通公司新闻：一般性公司发展动态、日常运营信息、小额合同、常规产品更新等，对股价影响较小的日常信息
    
    5级 - 市场传闻（最低级别）：未经官方证实的消息、小道消息、模糊信息等，可靠性较低的市场传言
    
    请先对新闻内容进行深入理解，然后给出一个明确的分级（1-5之间的整数），并提供一句话解释。
    你的回答必须以以下格式返回（且只返回这两行）：
    分级：[1-5之间的数字]
    分类：[对应上述分类的文字描述，如"国家政策"、"行业重大事件"等]
    
    新闻内容：
    {news_text}
    """
    
    response = client.chat.completions.create(
        model="deepseek-r1-distill-qwen-32b-250120",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    result = response.choices[0].message.content.strip()
    
    # 解析返回结果
    lines = result.split('\n')
    if len(lines) >= 2:
        try:
            level_line = lines[0]
            category_line = lines[1]
            
            # 提取数字和分类
            level = int(level_line.split('：')[1].strip())
            category = category_line.split('：')[1].strip()
            
            return (level, category)
        except (IndexError, ValueError) as e:
            print(f"解析新闻重要性分级时出错: {e}")
            return (5, "解析错误")  # 默认为最低级别
    else:
        print("AI返回的格式不符合预期")
        return (5, "格式错误")  # 默认为最低级别

def should_analyze_news(news_text):
    """
    判断新闻是否应该被进一步分析
    
    返回值：
    - (bool, tuple): 包含是否应分析的布尔值和重要性信息元组(级别,分类)
    """
    importance = filter_news_by_importance(news_text)
    level = importance[0]
    
    # 只有1-3级的新闻才会被继续分析
    should_analyze = level <= 3
    
    return (should_analyze, importance)

def analyze_news(news_text):
    """
    分析新闻内容，提取相关的股票代码
    确保只返回已上市的A股股票代码
    首先会对新闻进行重要性筛选，只分析重要级别较高的新闻
    即使新闻没有直接提到公司名称，也会根据行业关联性推荐相关股票
    """
    # 首先对新闻进行重要性筛选
    should_analyze, importance = should_analyze_news(news_text)
    importance_level, importance_category = importance
    
    # 如果新闻重要性不足（4级或5级），则不进行分析
    if not should_analyze:
        print(f"新闻重要性等级为{importance_level}（{importance_category}），不进行分析")
        return {
            "analyze": False,
            "importance_level": importance_level,
            "importance_category": importance_category,
            "industry_info": None,
            "stock_code": None
        }
    
    print(f"新闻重要性等级为{importance_level}（{importance_category}），进行分析")
    
    # 对重要新闻进行行业分类
    industry_info = categorize_news_by_industry(news_text)
    print(f"所属行业: {industry_info['main_category']} - {industry_info['sub_category']} (相关度: {industry_info['relevance_score']})")
    
    prompt = f"""
    分析以下新闻内容，提取或推荐与该新闻最相关的A股上市公司股票代码。
    新闻归类于"{industry_info['main_category']}"行业大类中的"{industry_info['sub_category']}"细分领域。
    
    分析步骤：
    1. 首先检查新闻中是否明确提到了A股上市公司名称，如有，优先返回该公司的股票代码
    2. 如果新闻没有直接提到上市公司名称，请根据新闻内容和行业分类，推荐该行业中最相关的龙头或代表性A股上市公司
    3. 推荐时优先考虑与新闻内容主题高度相关的公司，尤其是在该细分领域有竞争优势的企业
    4. 切记不要返回未上市公司（如华为、字节跳动等）的名称
    
    重要说明：
    - 即使新闻中没有直接提到上市公司名称，也必须找出与新闻主题最相关的A股上市公司
    - 优先选择行业龙头、市场份额领先或技术领先的公司
    - 如果是行业政策新闻，请选择最受该政策影响（正面或负面）的公司
    - 如果是国家政策新闻，请选择最受该政策影响的行业龙头公司
    
    你的回答必须只包含一个6位数字的股票代码（如"600519"或"000001"），不要有任何其他文字说明。
    如果经过充分分析确实找不到任何相关上市公司，请回复"无相关上市公司"。
    
    新闻内容：
    {news_text}
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
        # 如果第一次尝试未找到相关股票，再次尝试，但更明确要求返回行业龙头
        print("第一次未找到相关上市公司，尝试获取行业龙头企业...")
        
        fallback_prompt = f"""
        请根据以下新闻的行业分类，推荐一家在这个行业中最具代表性的A股上市公司。
        
        新闻行业归类：
        - 行业大类：{industry_info['main_category']}
        - 细分领域：{industry_info['sub_category']}
        
        即使新闻内容没有明确提到任何公司，你也必须从该行业中选择一家A股上市的龙头企业或最具代表性的公司。
        你应该考虑：市值规模、营收规模、市场占有率、技术领先程度等因素来选择最合适的公司。
        
        请直接返回股票代码（6位数字），不要有任何其他文字。
        你的回答将直接用于投资决策，请确保选择的公司确实是A股上市公司。
        
        新闻简述：{news_text[:100]}...
        """
        
        fallback_response = client.chat.completions.create(
            model="deepseek-r1-distill-qwen-32b-250120",
            messages=[
                {"role": "user", "content": fallback_prompt}
            ]
        )
        
        stock_code = fallback_response.choices[0].message.content.strip()
        print(f"找到行业相关股票: {stock_code}")
    
    # 验证返回的是否为有效的股票代码
    if stock_code == "无相关上市公司":
        return {
            "analyze": True,
            "importance_level": importance_level,
            "importance_category": importance_category,
            "industry_info": industry_info,
            "stock_code": "无相关上市公司"
        }
    
    # 尝试验证股票代码是否为已上市股票
    try:
        # 获取所有A股股票列表
        stock_list = ak.stock_info_a_code_name()
        # 检查返回的股票代码是否在列表中
        if stock_code in stock_list['code'].values:
            company_name = stock_list.loc[stock_list['code'] == stock_code, 'name'].values[0]
            print(f"验证通过：{stock_code} ({company_name}) 是已上市的A股股票")
            formatted_code = stock_code
        else:
            # 如果不在列表中，尝试添加市场后缀
            if stock_code.startswith(('0', '3')):
                formatted_code = f"{stock_code}.SZ"
            elif stock_code.startswith(('6', '9')):
                formatted_code = f"{stock_code}.SH"
            else:
                formatted_code = stock_code
            print(f"股票代码 {stock_code} 不在A股列表中，转换为 {formatted_code}")
    except Exception as e:
        print(f"验证股票代码时出错: {e}")
        # 如果验证过程出错，仍然返回原始代码，但在后续处理中会再次验证
        formatted_code = stock_code
    
    return {
        "analyze": True,
        "importance_level": importance_level,
        "importance_category": importance_category,
        "industry_info": industry_info,
        "stock_code": formatted_code
    }

def categorize_news_by_industry(news_text):
    """
    对新闻进行行业领域分类，确定新闻属于哪个行业大类和细分领域
    
    返回行业分类信息字典，包含：
    - main_category: 主要行业大类
    - sub_category: 细分行业
    - relevance_score: 相关度评分(1-10)
    - explanation: 分类解释
    """
    from industry_database import get_all_categories, get_subcategories
    
    # 获取所有行业大类
    main_categories = get_all_categories()
    
    prompt = f"""
    请分析以下新闻，确定其所属的行业领域类别。请从以下分类体系中，选择最匹配的行业大类和细分领域：

    行业大类列表：
    {', '.join(main_categories)}

    请根据新闻内容，给出如下格式的回答（只返回以下4行内容）：
    主要行业类别：[选择最匹配的行业大类]
    细分领域：[选择最匹配的细分领域]
    相关度评分：[1-10的整数，表示新闻与该行业的相关度]
    分类解释：[一句话解释为什么将新闻分类到该行业]

    新闻内容：
    {news_text}
    """
    
    response = client.chat.completions.create(
        model="deepseek-r1-distill-qwen-32b-250120",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    result = response.choices[0].message.content.strip()
    
    # 解析返回结果
    lines = result.split('\n')
    if len(lines) >= 4:
        try:
            main_category_line = lines[0]
            sub_category_line = lines[1]
            relevance_line = lines[2]
            explanation_line = lines[3]
            
            # 提取各项信息
            main_category = main_category_line.split('：')[1].strip()
            sub_category = sub_category_line.split('：')[1].strip()
            relevance_score = int(relevance_line.split('：')[1].strip())
            explanation = explanation_line.split('：')[1].strip()
            
            # 验证分类是否有效
            if main_category not in main_categories:
                print(f"警告：返回的行业大类 '{main_category}' 不在有效列表中")
                return {
                    "main_category": "未知",
                    "sub_category": "未知",
                    "relevance_score": 0,
                    "explanation": "无效的行业大类"
                }
            
            sub_categories = get_subcategories(main_category)
            if sub_category not in sub_categories:
                print(f"警告：返回的细分领域 '{sub_category}' 不在有效列表中")
                return {
                    "main_category": main_category,
                    "sub_category": "未知",
                    "relevance_score": relevance_score,
                    "explanation": "无效的细分领域"
                }
            
            return {
                "main_category": main_category,
                "sub_category": sub_category,
                "relevance_score": relevance_score,
                "explanation": explanation
            }
        except (IndexError, ValueError) as e:
            print(f"解析行业分类时出错: {e}")
            return {
                "main_category": "未知",
                "sub_category": "未知",
                "relevance_score": 0,
                "explanation": "解析错误"
            }
    else:
        print("AI返回的格式不符合预期")
        return {
            "main_category": "未知",
            "sub_category": "未知",
            "relevance_score": 0,
            "explanation": "格式错误"
        } 