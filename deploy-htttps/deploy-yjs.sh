#!/bin/bash

# Yjs 协作服务器部署脚本

set -e

echo "🚀 Yjs 协作服务器部署脚本"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装，请先安装 Docker Compose${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 环境检查通过${NC}"

# 检查镜像是否存在
IMAGE_NAME="deploy-https-yjs:v1.0"
if ! docker images | grep -q "deploy-https-yjs"; then
    echo -e "${YELLOW}⚠️  未找到 Yjs 镜像，开始构建...${NC}"
    
    # 检查 tar 文件
    if [ -f "deploy-https-yjs.tar" ]; then
        echo "📦 从 tar 文件加载镜像..."
        docker load -i deploy-https-yjs.tar
        echo -e "${GREEN}✅ 镜像加载成功${NC}"
    else
        echo "🔨 从源码构建镜像..."
        cd ../yjs-collab-server
        
        if [ ! -f "Dockerfile" ]; then
            echo -e "${RED}❌ 未找到 Dockerfile，请检查 yjs-collab-server 目录${NC}"
            exit 1
        fi
        
        docker build -t ${IMAGE_NAME} .
        echo -e "${GREEN}✅ 镜像构建成功${NC}"
        cd ../deploy-htttps
    fi
else
    echo -e "${GREEN}✅ 找到现有 Yjs 镜像${NC}"
fi

# 显示当前运行的服务
echo ""
echo "📊 当前运行的服务:"
docker-compose -f docker-compose-prod.yml ps

# 询问是否继续
echo ""
read -p "是否启动 Yjs 服务？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消部署"
    exit 0
fi

# 启动 Yjs 服务
echo ""
echo "🚀 启动 Yjs 协作服务器..."
docker-compose -f docker-compose-prod.yml up -d yjs-server

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📊 Yjs 服务状态:"
docker-compose -f docker-compose-prod.yml ps yjs-server

# 健康检查
echo ""
echo "🔍 健康检查:"
if curl -s http://localhost:1234 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Yjs 服务运行正常${NC}"
    echo "📡 WebSocket 地址: ws://localhost:1234/api/collaboration/yjs"
else
    echo -e "${YELLOW}⚠️  服务可能还在启动中，请稍后检查${NC}"
    echo "查看日志: docker logs pm-yjs-server"
fi

# 显示日志
echo ""
read -p "是否查看实时日志？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose-prod.yml logs -f yjs-server
fi

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo ""
echo "📝 常用命令:"
echo "  查看状态: docker-compose -f docker-compose-prod.yml ps yjs-server"
echo "  查看日志: docker-compose -f docker-compose-prod.yml logs -f yjs-server"
echo "  重启服务: docker-compose -f docker-compose-prod.yml restart yjs-server"
echo "  停止服务: docker-compose -f docker-compose-prod.yml stop yjs-server"
echo "  删除服务: docker-compose -f docker-compose-prod.yml down yjs-server"

