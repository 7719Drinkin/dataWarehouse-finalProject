#!/usr/bin/env python3
"""
电影数据仓库后端应用启动脚本
"""
import os
from dotenv import load_dotenv
from app import create_app
from waitress import serve

# 加载环境变量
load_dotenv()

app = create_app()

if __name__ == '__main__':
    # 从环境变量获取配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'

    print(f"Starting Movie Data Warehouse Backend...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")

    serve(app, host=host, port=port)
