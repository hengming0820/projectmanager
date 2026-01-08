#!/bin/bash

# 星像精准研发部管理系统 - 开发环境启动脚本

set -e

echo "🚀 启动星像精准研发部管理系统 - 开发环境"
echo "================================================"

# 检查是否在正确的目录
if [ ! -f "docker-compose.dev.yml" ]; then
    echo "❌ 错误：请在 deploy-local 目录下运行此脚本"
    exit 1
fi

# 1. 启动后端服务
echo ""
echo "📦 1. 启动后端服务（PostgreSQL, Redis, MinIO, Backend）..."
docker-compose -f docker-compose.dev.yml up -d

# 2. 等待服务启动
echo ""
echo "⏳ 2. 等待服务启动..."
sleep 5

# 3. 检查服务状态
echo ""
echo "📊 3. 检查服务状态..."
docker-compose -f docker-compose.dev.yml ps

# 4. 获取本机 IP 地址
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

# 5. 显示访问信息
echo ""
echo "✅ 后端服务启动完成！"
echo "================================================"
echo ""
echo "📌 本机访问地址："
echo "   后端 API:       http://localhost:8000"
echo "   API 文档:       http://localhost:8000/docs"

if [ -n "$LOCAL_IP" ]; then
    echo ""
    echo "📱 局域网访问地址："
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
echo "🎯 下一步："
echo "   1. 打开新终端，进入项目根目录"
echo "   2. 运行：npm run dev"
echo "   3. 本机访问：http://localhost:3008"

if [ -n "$LOCAL_IP" ]; then
    echo "   4. 局域网访问：http://${LOCAL_IP}:3008"
fi

echo ""
echo "💡 提示："
echo "   - 查看日志：docker-compose -f docker-compose.dev.yml logs -f"
echo "   - 停止服务：docker-compose -f docker-compose.dev.yml down"
echo ""

