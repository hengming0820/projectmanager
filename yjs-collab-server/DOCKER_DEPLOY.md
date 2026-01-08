# Yjs 协作服务器 Docker 部署指南

## 📋 概述

Yjs 协作服务器是一个基于 WebSocket 的实时协作服务，用于支持 XNote 编辑器的多人实时编辑功能。

## 🏗️ 架构

```
┌─────────────────────────────────────────────┐
│                  Frontend                    │
│           (Vue.js + XNote Editor)           │
└─────────────┬───────────────────────────────┘
              │
              ├─ HTTP/HTTPS → Backend (FastAPI)
              │                 Port: 8000
              │
              └─ WebSocket → Yjs Server (Node.js)
                              Port: 1234
                              Path: /api/collaboration/yjs
```

## 🚀 快速开始

### 1. 构建 Docker 镜像

#### Linux/Mac:

```bash
cd yjs-collab-server
chmod +x build-docker.sh
./build-docker.sh
```

#### Windows:

```batch
cd yjs-collab-server
build-docker.bat
```

### 2. 导出镜像（用于生产部署）

```bash
docker save deploy-https-yjs:v1.0 -o deploy-https-yjs.tar
```

### 3. 在生产服务器加载镜像

```bash
docker load -i deploy-https-yjs.tar
```

### 4. 启动服务

```bash
cd ../deploy-htttps
docker-compose -f docker-compose-prod.yml up -d yjs-server
```

## 📦 Docker 配置详解

### Dockerfile

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY server.js ./
EXPOSE 1234
CMD ["npm", "start"]
```

**关键配置：**

- 基础镜像：`node:18-alpine` (轻量级)
- 工作目录：`/app`
- 端口：`1234`
- 启动命令：`npm start`

### Docker Compose 配置

```yaml
yjs-server:
  image: deploy-https-yjs:v1.0
  container_name: pm-yjs-server
  environment:
    PORT: '1234'
    WS_PATH: '/api/collaboration/yjs'
  ports:
    - '0.0.0.0:1234:1234'
  restart: unless-stopped
  networks:
    - pm-network
  healthcheck:
    test: ['CMD', 'node', '-e', "require('http').get('http://localhost:1234', ...)"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 5s
```

## 🔧 环境变量

| 变量    | 默认值                 | 说明               |
| ------- | ---------------------- | ------------------ |
| PORT    | 1234                   | WebSocket 服务端口 |
| WS_PATH | /api/collaboration/yjs | WebSocket 路径     |

## 🌐 网络配置

### Nginx 代理配置

如果使用 Nginx 反向代理，需要添加以下配置：

```nginx
# WebSocket 代理配置（用于 Yjs 协作）
location /api/collaboration/yjs {
    proxy_pass http://pm-yjs-server:1234;

    # WebSocket 必需的头信息
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # 基础代理头
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # 超时配置（长连接）
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
}
```

### 前端配置

前端通过 Vite 代理或直接连接：

```typescript
// 开发环境 (vite.config.ts)
proxy: {
  '/api/collaboration/yjs': {
    target: 'http://localhost:1234',
    ws: true,
    changeOrigin: true
  }
}

// 生产环境 (直接连接)
const wsUrl = `ws://${window.location.host}/api/collaboration/yjs`
```

## 🔍 服务监控

### 查看服务状态

```bash
docker-compose -f docker-compose-prod.yml ps yjs-server
```

### 查看日志

```bash
# 实时日志
docker-compose -f docker-compose-prod.yml logs -f yjs-server

# 最近 100 行
docker logs --tail 100 pm-yjs-server

# 实时跟踪
docker logs -f pm-yjs-server
```

### 健康检查

```bash
# 手动测试
curl http://localhost:1234

# 应该返回 JSON:
# {"status":"ok","service":"Yjs WebSocket Collaboration Server",...}
```

## 🔄 服务管理

### 启动服务

```bash
docker-compose -f docker-compose-prod.yml up -d yjs-server
```

### 停止服务

```bash
docker-compose -f docker-compose-prod.yml stop yjs-server
```

### 重启服务

```bash
docker-compose -f docker-compose-prod.yml restart yjs-server
```

### 删除服务

```bash
docker-compose -f docker-compose-prod.yml down yjs-server
```

## 📊 性能监控

### 查看资源使用

```bash
docker stats pm-yjs-server
```

### 查看连接数

```bash
docker exec pm-yjs-server node -e "
const http = require('http');
http.get('http://localhost:1234', (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(JSON.parse(data)));
});
"
```

## 🐛 故障排查

### 问题 1: WebSocket 连接失败

**症状：** 前端无法连接到 Yjs 服务器

**解决方案：**

1. 检查服务是否运行：`docker ps | grep yjs`
2. 检查端口是否开放：`netstat -an | grep 1234`
3. 检查防火墙规则
4. 查看日志：`docker logs pm-yjs-server`

### 问题 2: 容器无法启动

**症状：** 容器状态为 Restarting 或 Exited

**解决方案：**

```bash
# 查看详细错误
docker logs pm-yjs-server

# 检查镜像是否正确加载
docker images | grep yjs

# 重新构建镜像
cd yjs-collab-server
./build-docker.sh
```

### 问题 3: 内存占用过高

**症状：** Yjs 服务器内存使用不断增长

**解决方案：**

1. 检查活动文档数量
2. 配置文档清理策略（修改 server.js）
3. 设置内存限制：

```yaml
yjs-server:
  ...
  deploy:
    resources:
      limits:
        memory: 512M
```

## 🔒 安全配置

### 1. 限制访问来源

在 Nginx 中配置 CORS：

```nginx
location /api/collaboration/yjs {
    # 只允许特定域名访问
    if ($http_origin ~* "^https?://(localhost|your-domain\.com)") {
        set $cors "true";
    }

    if ($cors = "true") {
        add_header Access-Control-Allow-Origin $http_origin;
    }

    # ... 其他配置
}
```

### 2. 配置 SSL/TLS

使用 wss:// (WebSocket Secure) 连接：

```javascript
const wsUrl = `wss://${window.location.host}/api/collaboration/yjs`
```

## 📈 扩展部署

### 多实例部署（负载均衡）

```yaml
yjs-server-1:
  image: deploy-https-yjs:v1.0
  container_name: pm-yjs-server-1
  ports:
    - "1234:1234"

yjs-server-2:
  image: deploy-https-yjs:v1.0
  container_name: pm-yjs-server-2
  ports:
    - "1235:1234"

nginx:
  # 在 Nginx 配置负载均衡
  upstream yjs_backend {
    ip_hash;  # 重要：保持会话粘性
    server yjs-server-1:1234;
    server yjs-server-2:1234;
  }
```

**注意：** WebSocket 需要会话粘性（sticky session），使用 `ip_hash` 或其他粘性策略。

## 📝 完整部署流程

### 步骤 1: 准备环境

```bash
# 确保 Docker 已安装
docker --version
docker-compose --version
```

### 步骤 2: 构建镜像

```bash
cd yjs-collab-server
./build-docker.sh
```

### 步骤 3: 导出镜像（可选，用于离线部署）

```bash
docker save deploy-https-yjs:v1.0 -o deploy-https-yjs-v1.0.tar
```

### 步骤 4: 部署到生产服务器

```bash
# 如果使用 tar 文件
docker load -i deploy-https-yjs-v1.0.tar

# 启动服务
cd deploy-htttps
docker-compose -f docker-compose-prod.yml up -d yjs-server
```

### 步骤 5: 验证部署

```bash
# 检查服务状态
docker-compose -f docker-compose-prod.yml ps

# 测试连接
curl http://localhost:1234

# 查看日志
docker logs -f pm-yjs-server
```

## 🎯 最佳实践

1. **日志管理**: 使用 Docker 日志驱动或外部日志服务
2. **监控告警**: 配置 Prometheus + Grafana 监控
3. **自动重启**: `restart: unless-stopped` 确保服务可用性
4. **资源限制**: 设置内存和 CPU 限制防止资源耗尽
5. **定期备份**: 虽然 Yjs 是无状态的，但记录连接日志有助于排查问题

## 📚 相关文档

- [Yjs 官方文档](https://docs.yjs.dev/)
- [y-websocket 文档](https://github.com/yjs/y-websocket)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [XNote 编辑器文档](../xnote/README.md)

## 🆘 获取帮助

如遇问题，请检查：

1. Docker 日志：`docker logs pm-yjs-server`
2. 网络连接：`docker network inspect pm-network`
3. 服务状态：`docker-compose -f docker-compose-prod.yml ps`
