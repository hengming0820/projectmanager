#!/bin/bash

# 生产环境镜像加载和启动脚本
# Usage: ./load-and-start.sh [backend-image.tar]

set -e

echo "============================================"
echo "医学影像标注管理系统 - 生产环境部署"
echo "============================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装，请先安装 Docker Compose${NC}"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${GREEN}📂 当前目录: $SCRIPT_DIR${NC}"
echo ""

# 步骤1: 加载 Backend 镜像
echo "================================"
echo "步骤 1/4: 加载 Backend 镜像"
echo "================================"

BACKEND_TAR="${1:-deploy-https-backend-v1.0.tar}"

# 支持加载多个镜像文件
IMAGE_FILES=(
    "$BACKEND_TAR"
    "deploy-https-postgres-v1.0.tar"
    "deploy-https-redis-v1.0.tar"
    "deploy-https-minio-v1.0.tar"
)

for img_file in "${IMAGE_FILES[@]}"; do
    if [ -f "$img_file" ]; then
        echo -e "${YELLOW}正在加载镜像: $img_file${NC}"
        docker load -i "$img_file"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 镜像加载成功: $img_file${NC}"
        else
            echo -e "${RED}❌ 镜像加载失败: $img_file${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  未找到镜像文件: $img_file (跳过)${NC}"
    fi
done

echo ""

# 步骤2: 验证镜像
echo "================================"
echo "步骤 2/4: 验证镜像"
echo "================================"

if docker images | grep -q "deploy-https-backend"; then
    echo -e "${GREEN}✅ Backend 镜像已存在${NC}"
    docker images | grep "deploy-https-backend" | head -1
else
    echo -e "${RED}❌ Backend 镜像不存在，请检查${NC}"
    echo -e "${YELLOW}提示: 请确保已加载 deploy-https-backend:v1.0 镜像${NC}"
    exit 1
fi

echo ""

# 步骤3: 检查配置文件
echo "================================"
echo "步骤 3/4: 检查配置文件"
echo "================================"

if [ ! -f "docker-compose-prod.yml" ]; then
    echo -e "${RED}❌ 未找到 docker-compose-prod.yml${NC}"
    exit 1
fi

if [ ! -d "../dist" ]; then
    echo -e "${YELLOW}⚠️  未找到前端 dist 目录${NC}"
    echo "请确保已解压前端文件到上级目录"
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✅ 配置文件检查完成${NC}"
echo ""

# 步骤4: 启动服务
echo "================================"
echo "步骤 4/4: 启动服务"
echo "================================"

echo "正在停止旧服务（如果存在）..."
docker-compose -f docker-compose-prod.yml down 2>/dev/null || true

echo ""
echo "正在启动新服务..."
docker-compose -f docker-compose-prod.yml up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 服务启动成功${NC}"
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    exit 1
fi

echo ""

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 显示服务状态
echo ""
echo "================================"
echo "服务状态"
echo "================================"
docker-compose -f docker-compose-prod.yml ps

echo ""
echo "================================"
echo "健康检查"
echo "================================"

# 检查 Backend
echo -n "Backend API: "
if curl -f -s http://localhost:8000/docs > /dev/null; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${RED}❌ 无法访问${NC}"
fi

# 检查 Frontend
echo -n "Frontend:    "
if curl -f -s http://localhost/ > /dev/null; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${RED}❌ 无法访问${NC}"
fi

# 检查 PostgreSQL
echo -n "PostgreSQL:  "
if docker exec pm-postgres2 pg_isready -U admin > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${RED}❌ 无法连接${NC}"
fi

# 检查 Redis
echo -n "Redis:       "
if docker exec pm-redis2 redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${RED}❌ 无法连接${NC}"
fi

# 检查 MinIO
echo -n "MinIO:       "
if curl -f -s http://localhost:9000/minio/health/live > /dev/null; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${RED}❌ 无法连接${NC}"
fi

echo ""
echo "================================"
echo "部署完成！"
echo "================================"
echo ""
echo "访问地址："
echo "  - 前端: http://localhost"
echo "  - API 文档: http://localhost:8000/docs"
echo "  - MinIO 控制台: http://localhost:9001"
echo ""
echo "查看日志："
echo "  docker-compose -f docker-compose-prod.yml logs -f"
echo ""
echo "停止服务："
echo "  docker-compose -f docker-compose-prod.yml down"
echo ""
echo -e "${GREEN}🎉 部署成功！${NC}"

