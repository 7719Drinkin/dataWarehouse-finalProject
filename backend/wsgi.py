#!/usr/bin/env python3
"""
WSGI入口文件，用于生产环境部署
"""
from app import create_app

# 创建生产环境应用实例
app = create_app('development')

if __name__ == '__main__':
    app.run()

