#!/bin/bash

# Redis 连接问题快速修复脚本
# 用于重新构建后端镜像并重启服务

set -e  # 遇到错误立即退出

echo "=================================="
echo "🔧 Redis 连接问题快速修复"
echo "=================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步骤 1: 检查当前位置
echo -e "${YELLOW}步骤 1/5: 检查环境...${NC}"
if [ ! -f "docker-compose-prod.yml" ]; then
    echo -e "${RED}❌ 错误: 未找到 docker-compose-prod.yml${NC}"
    echo "请在 deploy-https 目录下运行此脚本"
    exit 1
fi
echo -e "${GREEN}✅ 环境检查通过${NC}"
echo ""

# 步骤 2: 停止现有服务
echo -e "${YELLOW}步骤 2/5: 停止现有服务...${NC}"
docker compose -f docker-compose-prod.yml down
echo -e "${GREEN}✅ 服务已停止${NC}"
echo ""

# 步骤 3: 重新构建后端镜像
echo -e "${YELLOW}步骤 3/5: 重新构建后端镜像...${NC}"
cd ..
docker build -t deploy-https-backend:v1.0 -f backend/Dockerfile .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 后端镜像构建成功${NC}"
else
    echo -e "${RED}❌ 后端镜像构建失败${NC}"
    exit 1
fi
cd deploy-https
echo ""

# 步骤 4: 启动所有服务
echo -e "${YELLOW}步骤 4/5: 启动所有服务...${NC}"
docker compose -f docker-compose-prod.yml up -d
echo -e "${GREEN}✅ 服务已启动${NC}"
echo ""

# 步骤 5: 等待服务启动并查看日志
echo -e "${YELLOW}步骤 5/5: 检查服务状态...${NC}"
echo "等待 10 秒让服务完全启动..."
sleep 10

echo ""
echo "=================================="
echo "📊 服务状态"
echo "=================================="
docker compose -f docker-compose-prod.yml ps

echo ""
echo "=================================="
echo "📋 后端启动日志（最后 30 行）"
echo "=================================="
docker logs pm-backend --tail 30

echo ""
echo "=================================="
echo "✅ 修复完成！"
echo "=================================="
echo ""
echo "🔍 验证步骤："
echo "1. 检查上方日志是否显示: ✅ Redis 连接成功"
echo "2. 如果看到 '⚠️ Redis不可用'，请运行:"
echo "   docker logs -f pm-backend"
echo "   查看完整日志以诊断问题"
echo ""
echo "3. 测试 Redis 连接:"
echo "   docker exec pm-backend python -c 'import redis; r=redis.from_url(\"redis://redis:6379\"); print(r.ping())'"
echo ""
echo "4. 如果仍有问题，请查看详细文档:"
echo "   cat DOCKER_REDIS_CONNECTION_FIX.md"
echo ""

