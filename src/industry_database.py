import json
import os
from typing import Dict, List, Optional

# 行业分类数据库
INDUSTRY_DATABASE = {
    "科技与创新类": {
        "人工智能（AI）": {
            "细分方向": ["机器学习", "计算机视觉", "自然语言处理（NLP）"],
            "代表公司": ["科大讯飞", "云从科技", "寒武纪"]
        },
        "半导体/芯片": {
            "细分方向": ["集成电路设计", "晶圆制造", "封测", "EDA工具"],
            "代表公司": ["中芯国际", "韦尔股份", "北方华创"]
        },
        "5G通信": {
            "细分方向": ["基站设备", "光模块", "射频器件"],
            "代表公司": ["中兴通讯", "烽火通信", "新易盛"]
        },
        "云计算/大数据": {
            "细分方向": ["IDC（数据中心）", "SaaS", "边缘计算"],
            "代表公司": ["浪潮信息", "用友网络", "宝信软件"]
        },
        "元宇宙/虚拟现实（VR/AR）": {
            "细分方向": ["VR设备", "数字孪生", "NFT"],
            "代表公司": ["歌尔股份", "中青宝", "风语筑"]
        },
        "区块链/数字货币": {
            "细分方向": ["数字人民币", "加密技术", "金融科技"],
            "代表公司": ["恒生电子", "广电运通", "四方精创"]
        },
        "量子科技": {
            "细分方向": ["量子计算", "量子通信"],
            "代表公司": ["国盾量子", "科大国创"]
        }
    },
    "新能源与绿色经济类": {
        "新能源汽车": {
            "细分方向": ["锂电池", "氢能源", "充电桩"],
            "代表公司": ["宁德时代", "比亚迪", "亿纬锂能"]
        },
        "光伏（太阳能）": {
            "细分方向": ["HJT电池", "钙钛矿", "逆变器"],
            "代表公司": ["隆基绿能", "通威股份", "阳光电源"]
        },
        "风电": {
            "细分方向": ["陆上风电", "海上风电", "叶片材料"],
            "代表公司": ["金风科技", "明阳智能", "大金重工"]
        },
        "储能": {
            "细分方向": ["电化学储能", "抽水蓄能", "钠离子电池"],
            "代表公司": ["阳光电源", "南都电源", "鹏辉能源"]
        },
        "氢能源": {
            "细分方向": ["制氢", "储氢", "燃料电池"],
            "代表公司": ["亿华通", "美锦能源", "潍柴动力"]
        },
        "环保/碳中和": {
            "细分方向": ["碳交易", "固废处理", "污水处理"],
            "代表公司": ["清新环境", "伟明环保", "碧水源"]
        }
    },
    "消费与医疗健康类": {
        "医药/生物科技": {
            "细分方向": ["创新药", "CXO（医药外包）", "医疗器械"],
            "代表公司": ["药明康德", "迈瑞医疗", "恒瑞医药"]
        },
        "医美/化妆品": {
            "细分方向": ["玻尿酸", "胶原蛋白", "功能性护肤品"],
            "代表公司": ["爱美客", "华熙生物", "珀莱雅"]
        },
        "白酒/食品饮料": {
            "细分方向": ["高端白酒", "调味品", "预制菜"],
            "代表公司": ["贵州茅台", "海天味业", "安井食品"]
        },
        "免税/零售": {
            "细分方向": ["离岛免税", "跨境电商"],
            "代表公司": ["中国中免", "王府井"]
        },
        "宠物经济": {
            "细分方向": ["宠物食品", "宠物医疗"],
            "代表公司": ["中宠股份", "佩蒂股份"]
        }
    },
    "政策驱动与周期类": {
        "国企改革（中特估）": {
            "细分方向": ["央企重组", "地方国资改革"],
            "代表公司": ["中国联通", "中国交建"]
        },
        "一带一路": {
            "细分方向": ["基建", "港口", "国际工程"],
            "代表公司": ["中国建筑", "中远海控"]
        },
        "军工/航天": {
            "细分方向": ["航空发动机", "卫星导航", "船舶制造"],
            "代表公司": ["中航沈飞", "中国卫星", "中国船舶"]
        },
        "农业/乡村振兴": {
            "细分方向": ["种子", "农机", "土地流转"],
            "代表公司": ["隆平高科", "北大荒"]
        },
        "房地产/REITs": {
            "细分方向": ["物业管理", "保障房"],
            "代表公司": ["万科A", "保利发展"]
        }
    },
    "其他热点概念": {
        "机器人/智能制造": {
            "细分方向": ["工业机器人", "人形机器人"],
            "代表公司": ["埃斯顿", "汇川技术"]
        },
        "低空经济（无人机/eVTOL）": {
            "细分方向": ["飞行汽车", "无人机物流"],
            "代表公司": ["亿航智能", "纵横股份"]
        },
        "可控核聚变（未来能源）": {
            "细分方向": ["超导材料", "等离子体技术"],
            "代表公司": ["联创光电", "西部超导"]
        },
        "ST/壳资源（重组预期）": {
            "细分方向": [],
            "代表公司": ["部分ST股（高风险投机标的）"]
        },
        "黄金/避险资产": {
            "细分方向": [],
            "代表公司": ["山东黄金", "紫金矿业"]
        }
    }
}

def get_industry_info(main_category: str, sub_category: str) -> Optional[Dict]:
    """获取指定行业大类和细分领域的信息"""
    try:
        return INDUSTRY_DATABASE[main_category][sub_category]
    except KeyError:
        return None

def get_all_categories() -> List[str]:
    """获取所有行业大类"""
    return list(INDUSTRY_DATABASE.keys())

def get_subcategories(main_category: str) -> List[str]:
    """获取指定行业大类的所有细分领域"""
    try:
        return list(INDUSTRY_DATABASE[main_category].keys())
    except KeyError:
        return []

def get_representative_companies(main_category: str, sub_category: str) -> List[str]:
    """获取指定行业大类和细分领域的代表公司"""
    try:
        return INDUSTRY_DATABASE[main_category][sub_category]["代表公司"]
    except KeyError:
        return []

def get_sub_directions(main_category: str, sub_category: str) -> List[str]:
    """获取指定行业大类和细分领域的细分方向"""
    try:
        return INDUSTRY_DATABASE[main_category][sub_category]["细分方向"]
    except KeyError:
        return []

def save_database_to_file(file_path: str = "data/industry_database.json"):
    """将行业数据库保存到文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(INDUSTRY_DATABASE, f, ensure_ascii=False, indent=2)

def load_database_from_file(file_path: str = "data/industry_database.json") -> Dict:
    """从文件加载行业数据库"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return INDUSTRY_DATABASE 