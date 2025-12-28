#!/bin/bash

# 电影数据仓库前端启动脚本

echo "🎬 电影数据仓库前端启动脚本"
echo "================================="

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 18+"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装 npm"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "❌ 请在 frontend/data-warehouse 目录下运行此脚本"
    exit 1
fi

echo "📦 安装依赖..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "🚀 启动开发服务器..."
echo "前端将在 http://localhost:3000 启动"
echo "后端API需要运行在 http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

npm run dev



