#!/bin/bash

# 星像精准研发部管理系统 - 生产模式启动脚本

set -e

echo "🚀 启动星像精准研发部管理系统 - 生产模式"
echo "================================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误：请在 deploy-local 目录下运行此脚本"
    exit 1
fi

# 1. 检查 dist 目录
echo "📁 1. 检查前端构建产物..."
if [ ! -d "../dist" ]; then
    echo "⚠️  dist 目录不存在，开始构建前端..."
    cd ..
    npm run build
    if [ $? -ne 0 ]; then
        echo "❌ 前端构建失败！"
        exit 1
    fi
    cd deploy-local
    echo "✅ 前端构建完成"
else
    echo "✅ 发现 dist 目录"
    
    # 询问是否重新构建
    echo ""
    read -p "是否重新构建前端？(y/N): " rebuild
    if [[ "$rebuild" =~ ^[Yy]$ ]]; then
        echo "🔨 重新构建前端..."
        cd ..
        npm run build
        if [ $? -ne 0 ]; then
            echo "❌ 前端构建失败！"
            exit 1
        fi
        cd deploy-local
        echo "✅ 前端重新构建完成"
    fi
fi

# 2. 启动所有服务
echo ""
echo "📦 2. 启动所有服务（PostgreSQL, Redis, MinIO, Backend, Frontend）..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ 启动失败！请检查 Docker 是否运行"
    exit 1
fi

# 3. 等待服务启动
echo ""
echo "⏳ 3. 等待服务启动..."
sleep 8

# 4. 检查服务状态
echo ""
echo "📊 4. 检查服务状态..."
docker-compose ps

# 5. 获取本机 IP 地址
LOCAL_IP=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
else
    # WSL or other
    LOCAL_IP=$(ip addr show eth0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
fi

# 6. 显示访问信息
echo ""
echo "✅ 所有服务启动完成！"
echo "================================================"
echo ""
echo "📌 本机访问地址："
echo "   前端应用:       http://localhost:3006"
echo "   后端 API:       http://localhost:8000"
echo "   API 文档:       http://localhost:8000/docs"

if [ -n "$LOCAL_IP" ]; then
    echo ""
    echo "📱 局域网访问地址："
    echo "   前端应用:       http://${LOCAL_IP}:3006"
    echo "   后端 API:       http://${LOCAL_IP}:8000"
    echo "   MinIO 控制台:   http://${LOCAL_IP}:9001"
fi

echo ""
echo "🔧 服务端口："
echo "   PostgreSQL:     localhost:5432"
echo "   Redis:          localhost:6379"
echo "   MinIO API:      localhost:9000"
echo "   MinIO 控制台:   http://localhost:9001"
echo "     - 用户名: minioadmin"
echo "     - 密码: minioadmin123"
echo ""
echo "📝 默认登录账号："
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "💡 常用命令："
echo "   - 查看日志：docker-compose logs -f"
echo "   - 查看特定服务日志：docker-compose logs -f frontend"
echo "   - 停止服务：docker-compose down"
echo "   - 重启服务：docker-compose restart"
echo ""

# 6. 询问是否打开浏览器
read -p "是否在浏览器中打开前端页面？(Y/n): " open_browser
if [[ ! "$open_browser" =~ ^[Nn]$ ]]; then
    echo "🌐 正在打开浏览器..."
    
    # 跨平台打开浏览器
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open http://localhost:3006
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open > /dev/null; then
            xdg-open http://localhost:3006
        elif command -v gnome-open > /dev/null; then
            gnome-open http://localhost:3006
        else
            echo "ℹ️  请手动在浏览器中打开: http://localhost:3006"
        fi
    else
        # WSL or other
        if command -v wslview > /dev/null; then
            wslview http://localhost:3006
        else
            echo "ℹ️  请手动在浏览器中打开: http://localhost:3006"
        fi
    fi
fi

echo ""
echo "✅ 启动完成！"

