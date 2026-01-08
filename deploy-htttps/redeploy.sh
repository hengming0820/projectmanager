#!/bin/bash
# 🔄 快速重新部署脚本
# 用于更新 Nginx 配置后重启服务

set -e

echo "================================================"
echo "🔄 开始重新部署服务"
echo "================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查 Nginx 配置
echo "📋 [1/5] 检查 Nginx 配置..."
if docker exec pm-frontend nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✅ Nginx 配置验证通过${NC}"
else
    echo -e "${RED}❌ Nginx 配置验证失败，请检查配置文件${NC}"
    docker exec pm-frontend nginx -t
    exit 1
fi
echo ""

# 2. 停止服务
echo "🛑 [2/5] 停止所有服务..."
docker-compose down
echo -e "${GREEN}✅ 服务已停止${NC}"
echo ""

# 3. 启动服务
echo "🚀 [3/5] 启动所有服务..."
docker-compose up -d
echo -e "${GREEN}✅ 服务已启动${NC}"
echo ""

# 4. 等待服务就绪
echo "⏳ [4/5] 等待服务就绪..."
sleep 5
echo ""

# 5. 验证服务状态
echo "✅ [5/5] 验证服务状态..."
echo ""
docker-compose ps
echo ""

# 检查关键服务
echo "================================================"
echo "🔍 检查关键服务健康状态"
echo "================================================"
echo ""

# 检查后端
echo -n "🔹 后端服务: "
if curl -s -k https://localhost/api/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${YELLOW}⚠️  可能未就绪，请稍后检查${NC}"
fi

# 检查 Yjs 服务器
echo -n "🔹 Yjs 服务器: "
YJS_STATUS=$(docker logs pm-yjs-server 2>&1 | grep -c "Running" || echo "0")
if [ "$YJS_STATUS" -gt 0 ]; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${YELLOW}⚠️  可能未就绪，请稍后检查${NC}"
fi

# 检查 Postgres
echo -n "🔹 数据库: "
if docker exec pm-postgres pg_isready -U admin > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${RED}❌ 异常${NC}"
fi

# 检查 Redis
echo -n "🔹 缓存服务: "
if docker exec pm-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${RED}❌ 异常${NC}"
fi

# 检查 MinIO
echo -n "🔹 对象存储: "
if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${YELLOW}⚠️  可能未就绪，请稍后检查${NC}"
fi

echo ""
echo "================================================"
echo "🎉 重新部署完成！"
echo "================================================"
echo ""
echo "📝 后续操作："
echo "  1. 访问: https://YOUR_SERVER_IP"
echo "  2. 清除浏览器缓存（Ctrl+Shift+Delete）"
echo "  3. 重新登录测试"
echo "  4. 测试协作文档功能"
echo ""
echo "📊 查看日志："
echo "  docker-compose logs -f              # 所有服务"
echo "  docker logs pm-yjs-server -f        # Yjs 服务器"
echo "  docker logs pm-frontend -f          # Nginx"
echo "  docker logs pm-backend -f           # 后端"
echo ""

