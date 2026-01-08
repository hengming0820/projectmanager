#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  重新构建后端服务 - 修复PDF中文字体问题                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ 错误：请在 deploy-htttps 目录下运行此脚本${NC}"
    exit 1
fi

# 第1步：停止服务
echo -e "${BLUE}📦 第1步：停止所有服务...${NC}"
docker-compose down
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 服务已停止${NC}"
else
    echo -e "${YELLOW}⚠️ 停止服务失败，可能服务未运行，继续...${NC}"
fi
echo ""

# 第2步：删除旧镜像
echo -e "${BLUE}🗑️ 第2步：删除旧的后端镜像...${NC}"
docker rmi deploy-https-backend:v1.0 -f 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 旧镜像已删除${NC}"
else
    echo -e "${YELLOW}⚠️ 删除镜像失败，可能镜像不存在，继续...${NC}"
fi
echo ""

# 第3步：可选清理缓存
echo -e "${BLUE}🧹 第3步：清理Docker缓存（可选）...${NC}"
read -p "是否清理Docker构建缓存？(y/N): " clean_cache
if [[ "$clean_cache" =~ ^[Yy]$ ]]; then
    docker builder prune -f
    echo -e "${GREEN}✅ 缓存已清理${NC}"
else
    echo -e "${YELLOW}⏭️ 跳过缓存清理${NC}"
fi
echo ""

# 第4步：重新构建
echo -e "${BLUE}🏗️ 第4步：重新构建后端镜像（这可能需要几分钟）...${NC}"
echo "正在下载并安装中文字体包..."
docker-compose build --no-cache backend
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 构建失败！请检查错误信息${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 后端镜像构建完成${NC}"
echo ""

# 第5步：启动服务
echo -e "${BLUE}🚀 第5步：启动所有服务...${NC}"
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 启动失败！请检查错误信息${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 所有服务已启动${NC}"
echo ""

# 等待服务初始化
echo -e "${BLUE}⏳ 等待服务初始化（10秒）...${NC}"
sleep 10

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🎉 重新构建完成！                                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 第6步：检查字体
echo -e "${BLUE}📋 第6步：检查后端日志中的字体加载情况...${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker-compose logs backend 2>&1 | grep -E "字体|font|Font" | tail -10
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo -e "${YELLOW}💡 验证建议：${NC}"
echo "   1. 上面应该看到 \"✅ 成功加载字体: WQYZenHei\" 的日志"
echo "   2. 如果看到 \"❌ 无法加载任何中文字体\"，请联系技术支持"
echo "   3. 访问前端测试PDF导出功能：http://localhost:3006"
echo ""

echo -e "${BLUE}📊 查看服务状态：${NC}"
docker-compose ps
echo ""

# 询问是否查看实时日志
read -p "是否查看后端实时日志？(y/N): " view_logs
if [[ "$view_logs" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}📋 后端实时日志（按 Ctrl+C 退出）：${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    docker-compose logs -f backend
else
    echo ""
    echo -e "${GREEN}✅ 完成！现在可以测试PDF导出功能了。${NC}"
    echo ""
fi

