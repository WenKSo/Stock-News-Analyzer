import os
import sys
import subprocess
import time
import json

def check_dependencies():
    """检查必要的依赖是否已安装"""
    try:
        import watchdog
        import pandas
        import schedule
        return True
    except ImportError as e:
        print(f"缺少必要的依赖: {e}")
        print("正在尝试安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            return True
        except Exception as e:
            print(f"安装依赖失败: {e}")
            return False

def check_directories():
    """确保必要的目录结构存在"""
    # 加载配置
    config = {}
    try:
        if os.path.exists("config.json"):
            with open("config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
    except Exception as e:
        print(f"加载配置文件时出错: {e}")
        return False
    
    # 确保必要的目录存在
    directories = [
        config.get("data_paths", {}).get("input_dir", "data/raw"),
        config.get("data_paths", {}).get("output_dir", "data/processed"),
        config.get("data_paths", {}).get("archive_dir", "data/archive"),
        "output",  # 用于存储分析报告
        "data"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"已确保目录存在: {directory}")
    
    return True

def start_watcher():
    """启动新闻监控服务"""
    print("正在启动新闻监控服务...\n")
    print("='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='")
    print(" 新闻数据自动处理监控服务")
    print(" - 监控data/raw目录的新文件和变化")
    print(" - 监控news_data.json文件的变化")
    print(" - 自动处理新数据并更新到news_data.json")
    print(" - 对新闻数据自动进行分析并生成报告")
    print(" - 使用MD5哈希算法确保不会重复处理同一条新闻")
    print(" - 按Ctrl+C可以停止服务")
    print("='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='")
    print("\n服务启动中...")
    
    try:
        # 使用Python解释器启动监控脚本
        subprocess.call([sys.executable, "news_watcher.py"])
    except KeyboardInterrupt:
        print("\n服务已停止")

def main():
    """主函数"""
    print("='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='")
    print(" 新闻数据自动处理系统")
    print("='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='='")
    
    # 检查依赖
    print("\n正在检查依赖...")
    if not check_dependencies():
        print("请手动安装所需依赖: pip install -r requirements.txt")
        input("按回车键退出...")
        return
    
    # 检查目录结构
    print("\n正在检查目录结构...")
    if not check_directories():
        print("创建目录结构失败")
        input("按回车键退出...")
        return
    
    # 启动监控服务
    start_watcher()

if __name__ == "__main__":
    main() 