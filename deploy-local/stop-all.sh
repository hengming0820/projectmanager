#!/bin/bash

# 星像精准研发部管理系统 - 停止所有服务

echo "🛑 停止星像精准研发部管理系统"
echo "================================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误：请在 deploy-local 目录下运行此脚本"
    exit 1
fi

# 询问是否删除数据卷
echo "⚠️  警告：即将停止所有 Docker 服务"
echo ""
read -p "是否同时删除数据卷（数据库数据将丢失）？(y/N): " remove_volumes

echo ""
if [[ "$remove_volumes" =~ ^[Yy]$ ]]; then
    echo "🗑️  停止服务并删除数据卷..."
    docker-compose down -v
    echo ""
    echo "✅ 服务已停止，数据卷已删除"
else
    echo "🛑 停止服务（保留数据）..."
    docker-compose down
    echo ""
    echo "✅ 服务已停止，数据已保留"
fi

echo ""
echo "💡 提示："
echo "   - 查看状态：docker-compose ps"
echo "   - 重新启动：./start-prod.sh 或 ./start-dev.sh"
echo ""

