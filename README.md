# 新闻数据处理流水线

这个项目用于处理从八爪鱼采集器获取的新闻数据，清理数据并将其导入到数据库中，以便进一步分析和使用。

## 功能特点

- 自动监控和处理八爪鱼采集器输出的新闻数据文件（JSON/CSV格式）
- 强大的文本清洗功能，去除HTML标签、CSS样式和多余的空白字符
- 数据清理和标准化
- 将处理后的数据导入到SQLite数据库
- 自动导出为JSON文件，用于现有系统
- 支持定时运行，与八爪鱼定时云采集功能配合使用
- 完整的日志记录和错误处理

## 目录结构

```
├── config.json              # 配置文件
├── data_processor.py        # 数据处理模块
├── data_integrator.py       # 数据库集成模块
├── news_data_pipeline.py    # 主流水线脚本
├── setup_environment.py     # 环境设置脚本
├── data/                    # 数据目录
│   ├── raw/                 # 原始数据（八爪鱼采集器输出）
│   ├── processed/           # 处理后的数据
│   ├── archive/             # 归档的原始数据
│   └── imported/            # 已导入数据库的处理后数据
└── news_database.db         # SQLite数据库文件
```

## 安装依赖

```bash
pip install pandas schedule beautifulsoup4
```

## 初始设置

在首次运行之前，请先运行环境设置脚本，创建必要的目录结构：

```bash
python setup_environment.py
```

这个脚本会：
1. 创建所有必要的数据目录
2. 可选地创建示例数据文件用于测试
3. 提供关于如何配置八爪鱼采集器的指导

## 使用方法

### 1. 配置

编辑 `config.json` 文件，根据需要调整配置：

```json
{
    "data_paths": {
        "input_dir": "data/raw",         # 八爪鱼采集器输出目录
        "output_dir": "data/processed",  # 处理后数据目录
        "archive_dir": "data/archive"    # 归档目录
    },
    "processing": {
        "interval_minutes": 10,          # 处理间隔（分钟）
        "run_continuously": false        # 是否持续运行
    },
    "data_cleaning": {
        "remove_duplicates": true,
        "drop_empty_content": true,
        "required_fields": ["title", "content", "publish_time", "source"]
    },
    "integration": {
        "target_db_file": "news_database.db",  # 数据库文件
        "table_name": "news_articles"          # 表名
    }
}
```

### 2. 设置八爪鱼采集器

1. 在八爪鱼采集器中，设置定时云采集任务，每10分钟运行一次
2. 将采集结果保存为JSON或CSV格式
3. 将输出目录设置为 `data/raw` 或在配置文件中指定的 `input_dir`

### 3. 运行流水线

单次运行：

```bash
python news_data_pipeline.py
```

如果要持续运行，将配置文件中的 `run_continuously` 设置为 `true`，然后运行：

```bash
python news_data_pipeline.py
```

### 4. 查看结果

处理后的数据将被导入到SQLite数据库中，可以使用任何SQLite客户端查看数据：

```bash
sqlite3 news_database.db
```

然后执行SQL查询：

```sql
SELECT * FROM news_articles LIMIT 10;
```

同时，处理后的数据也会被自动导出为JSON文件（默认为 `news_data.json`），您可以直接在现有系统中使用这个文件。

### 5. 导出JSON文件

如果您需要随时从数据库导出最新的数据为JSON文件，可以使用导出工具：

```bash
python export_json.py --output news_data.json --limit 1000
```

参数说明：
- `--output` 或 `-o`: 指定输出的JSON文件路径（默认为 `news_data.json`）
- `--limit` 或 `-l`: 限制导出的记录数（默认为全部导出）
- `--config` 或 `-c`: 指定配置文件路径（默认为 `config.json`）

## 与现有系统集成

如果您已经有一个使用 `news_data.json` 的系统，只需要：

1. 设置八爪鱼采集器将数据保存到 `data/raw` 目录
2. 运行数据处理流水线：`python news_data_pipeline.py`
3. 处理后的数据会自动导出为 `news_data.json`，您的现有系统可以直接使用这个文件

数据处理流程会自动清理八爪鱼采集的原始数据中的HTML标签、CSS样式和多余的空白字符，确保输出的JSON文件中包含干净的文本内容。

如果您想要自定义JSON文件的路径，可以在 `config.json` 中修改 `output_json_file` 配置项。

## 单独运行各模块

如果需要单独运行各个模块：

```bash
# 仅处理数据
python data_processor.py

# 仅导入数据到数据库
python data_integrator.py
```

## 日志

所有操作都会记录到日志文件中：

- `data_processor.log` - 数据处理日志
- `data_integrator.log` - 数据导入日志
- `news_pipeline.log` - 主流水线日志

## 常见问题解决

### 1. 找不到指定路径错误

如果遇到 `FileNotFoundError: [WinError 3] 系统找不到指定的路径` 错误，请确保：

1. 已运行 `setup_environment.py` 创建必要的目录
2. 配置文件中的路径正确
3. 数据库文件路径的目录部分存在

解决方法：
```bash
python setup_environment.py
```

### 2. 数据库错误

如果遇到数据库相关错误，可以尝试：

1. 删除现有的数据库文件，让程序重新创建
2. 检查数据库文件路径是否正确
3. 确保有足够的权限创建和写入数据库文件

### 3. 八爪鱼采集器输出格式不兼容

如果八爪鱼采集器的输出格式与程序不兼容，请检查：

1. 采集器输出的JSON或CSV文件格式
2. 确保输出文件包含必要的字段（title, content, publish_time, source等）
3. 根据需要调整 `data_processor.py` 中的数据清理逻辑

## 注意事项

- 确保八爪鱼采集器输出的数据格式与处理脚本兼容
- 根据实际数据结构，可能需要调整 `data_processor.py` 中的数据清理逻辑
- 首次运行时，会自动创建所需的目录和数据库
- 在Windows系统上，路径分隔符可能需要使用双反斜杠 `\\` 或正斜杠 `/`

## 文本清洗功能

系统内置了强大的文本清洗功能，可以处理以下问题：

1. 去除HTML标签（如 `<div>`, `<p>`, `<span>` 等）
2. 去除CSS样式定义（如 `ct_hqimg {margin: 10px 0;}`, `.hqimg_wrapper {text-align: center;}` 等）
3. 去除JavaScript代码
4. 去除多余的空白字符（空格、制表符、换行符等）
5. 去除URL链接
6. 去除常见的无意义文本（如"图片来源：网络"、"责任编辑：XXX"等）

您可以通过运行测试脚本来查看文本清洗的效果：

```bash
python test_text_cleaning.py
```

如果您需要自定义文本清洗规则，可以修改 `data_processor.py` 文件中的 `clean_text` 方法。