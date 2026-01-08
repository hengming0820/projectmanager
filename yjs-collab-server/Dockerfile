# Yjs WebSocket 协作服务器 Dockerfile
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖（生产环境）
RUN npm ci --only=production

# 复制服务器文件
COPY server.js ./

# 暴露端口（Yjs WebSocket 服务）
EXPOSE 1234

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:1234', (res) => { process.exit(res.statusCode === 200 ? 0 : 1); }).on('error', () => process.exit(1));"

# 启动服务
CMD ["npm", "start"]

