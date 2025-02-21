# 新闻量化分析系统

本项目旨在构建一个量化选股系统，通过抓取财经新闻并利用豆包 Doubao-1.5-lite API 分析新闻内容，提取相关股票代码，再结合 Tushare 获取股票基本面数据，最终生成买入建议。

## 文件结构

- **config/**: 存放配置信息，如 API 密钥和 Tushare token
- **data/**: 存放抓取的原始新闻数据
- **src/**: 包含各个功能模块代码
  - fetch_news.py：新闻数据加载模块
  - analyze_news.py：调用豆包 API 分析新闻模块
  - fetch_stock.py：调用 Tushare 获取股票数据模块
  - decision.py：决策逻辑模块
  - main.py：主入口，串联所有模块
- **requirements.txt**: 项目依赖包列表
- **README.md**: 项目说明文档