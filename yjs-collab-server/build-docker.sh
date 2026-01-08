#!/bin/bash

# Yjs 协作服务器 Docker 构建脚本

set -e

echo "🚀 开始构建 Yjs 协作服务器 Docker 镜像..."

# 镜像名称和版本
IMAGE_NAME="deploy-https-yjs"
VERSION="v1.0"
FULL_IMAGE_NAME="${IMAGE_NAME}:${VERSION}"

# 构建镜像
echo "📦 构建 Docker 镜像: ${FULL_IMAGE_NAME}"
docker build -t ${FULL_IMAGE_NAME} .

# 检查构建是否成功
if [ $? -eq 0 ]; then
  echo "✅ Docker 镜像构建成功: ${FULL_IMAGE_NAME}"
  
  # 显示镜像信息
  echo ""
  echo "📊 镜像信息:"
  docker images ${IMAGE_NAME}
  
  echo ""
  echo "📝 后续步骤:"
  echo "1. 导出镜像: docker save ${FULL_IMAGE_NAME} -o ${IMAGE_NAME}.tar"
  echo "2. 在目标服务器加载: docker load -i ${IMAGE_NAME}.tar"
  echo "3. 启动服务: cd ../deploy-htttps && docker-compose -f docker-compose-prod.yml up -d yjs-server"
else
  echo "❌ Docker 镜像构建失败"
  exit 1
fi

