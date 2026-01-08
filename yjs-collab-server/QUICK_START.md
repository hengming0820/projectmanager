# Yjs 协作服务器快速启动指南

## 🚀 5 分钟快速部署

### 方式 1: Docker 部署（推荐）

#### 步骤 1: 构建镜像

**Linux/Mac:**

```bash
cd yjs-collab-server
chmod +x build-docker.sh
./build-docker.sh
```

**Windows:**

```batch
cd yjs-collab-server
build-docker.bat
```

#### 步骤 2: 启动服务

**Linux/Mac:**

```bash
cd ../deploy-htttps
chmod +x deploy-yjs.sh
./deploy-yjs.sh
```

**Windows:**

```batch
cd ..\deploy-htttps
deploy-yjs.bat
```

#### 步骤 3: 验证部署

```bash
curl http://localhost:1234
```

**预期输出:**

```json
{
  "status": "ok",
  "service": "Yjs WebSocket Collaboration Server",
  "version": "1.0.0",
  "uptime": "5s",
  "documents": 0
}
```

### 方式 2: 本地开发运行

#### 步骤 1: 安装依赖

```bash
cd yjs-collab-server
npm install
```

#### 步骤 2: 启动服务

**Linux/Mac:**

```bash
npm start
```

**Windows:**

```batch
start.bat
```

#### 步骤 3: 验证运行

访问 http://localhost:1234 查看服务状态。

---

## 📊 服务状态检查

### 查看 Docker 容器

```bash
docker ps | grep yjs
```

**预期输出:**

```
pm-yjs-server   deploy-https-yjs:v1.0   Up 5 minutes   0.0.0.0:1234->1234/tcp
```

### 查看日志

```bash
docker logs -f pm-yjs-server
```

**预期日志:**

```
🚀 Yjs WebSocket server starting...
✅ WebSocket server is running on port 1234
📡 Ready for collaboration connections
```

### 健康检查

```bash
docker exec pm-yjs-server node -e "
const http = require('http');
http.get('http://localhost:1234', (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    console.log('Health Check:', JSON.parse(data));
  });
});
"
```

---

## 🔧 配置说明

### 环境变量

| 变量    | 默认值                 | 说明               |
| ------- | ---------------------- | ------------------ |
| PORT    | 1234                   | WebSocket 服务端口 |
| WS_PATH | /api/collaboration/yjs | WebSocket 路径     |

### 修改端口

**方式 1: 修改 docker-compose-prod.yml**

```yaml
yjs-server:
  environment:
    PORT: '8888' # 修改为你想要的端口
  ports:
    - '8888:8888' # 同步修改端口映射
```

**方式 2: 修改 server.js**

```javascript
const PORT = process.env.PORT || 8888 // 修改默认端口
```

---

## 🌐 前端配置

### 开发环境 (Vite)

编辑 `vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api/collaboration/yjs': {
        target: 'http://localhost:1234',
        ws: true,
        changeOrigin: true
      }
    }
  }
})
```

### 生产环境 (Nginx)

编辑 `nginx/default.conf`:

```nginx
location /api/collaboration/yjs {
    proxy_pass http://pm-yjs-server:1234;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400s;
}
```

---

## 🧪 测试连接

### 使用 wscat 测试

```bash
# 安装 wscat
npm install -g wscat

# 测试连接
wscat -c ws://localhost:1234/api/collaboration/yjs/test-doc-123
```

### 使用浏览器测试

```javascript
// 在浏览器控制台运行
const ws = new WebSocket('ws://localhost:1234/api/collaboration/yjs/test-doc-123')
ws.onopen = () => console.log('✅ WebSocket connected')
ws.onerror = (e) => console.error('❌ WebSocket error:', e)
ws.onmessage = (e) => console.log('📨 Message:', e.data)
```

---

## 🐛 常见问题

### 问题 1: 端口被占用

**症状:**

```
Error: listen EADDRINUSE: address already in use :::1234
```

**解决方案:**

```bash
# 查找占用端口的进程
lsof -i :1234  # Mac/Linux
netstat -ano | findstr :1234  # Windows

# 杀死进程
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# 或修改端口
export PORT=8888
npm start
```

### 问题 2: Docker 容器无法启动

**症状:**

```
pm-yjs-server   Restarting (1) 5 seconds ago
```

**解决方案:**

```bash
# 查看详细日志
docker logs pm-yjs-server

# 检查镜像
docker images | grep yjs

# 重新构建
cd yjs-collab-server
./build-docker.sh
```

### 问题 3: WebSocket 连接失败

**症状:** 前端无法连接到 Yjs 服务器

**解决方案:**

```bash
# 1. 检查服务是否运行
docker ps | grep yjs

# 2. 检查防火墙
sudo ufw allow 1234  # Linux
netsh advfirewall firewall add rule name="Yjs" dir=in action=allow protocol=TCP localport=1234  # Windows

# 3. 检查 Nginx 配置
docker logs pm-frontend | grep yjs

# 4. 检查浏览器控制台
# 查看 WebSocket 连接错误
```

---

## 📈 性能优化

### 调整内存限制

```yaml
yjs-server:
  deploy:
    resources:
      limits:
        memory: 512M
      reservations:
        memory: 256M
```

### 启用日志轮转

```yaml
yjs-server:
  logging:
    driver: 'json-file'
    options:
      max-size: '10m'
      max-file: '3'
```

---

## 🔄 服务管理命令速查表

| 操作     | 命令                                                           |
| -------- | -------------------------------------------------------------- |
| 启动服务 | `docker-compose -f docker-compose-prod.yml up -d yjs-server`   |
| 停止服务 | `docker-compose -f docker-compose-prod.yml stop yjs-server`    |
| 重启服务 | `docker-compose -f docker-compose-prod.yml restart yjs-server` |
| 查看状态 | `docker-compose -f docker-compose-prod.yml ps yjs-server`      |
| 查看日志 | `docker-compose -f docker-compose-prod.yml logs -f yjs-server` |
| 删除服务 | `docker-compose -f docker-compose-prod.yml down yjs-server`    |
| 进入容器 | `docker exec -it pm-yjs-server sh`                             |
| 查看资源 | `docker stats pm-yjs-server`                                   |

---

## 🎉 完成！

现在您可以：

1. ✅ 在前端编辑器中进行多人实时协作
2. ✅ 查看在线编辑用户列表
3. ✅ 实时同步编辑内容
4. ✅ 支持断线重连

**下一步:**

- 查看完整文档：`DOCKER_DEPLOY.md`
- 集成到前端：`../src/components/core/forms/art-textbus-editor/`
- 监控服务：设置 Prometheus/Grafana

---

**遇到问题？** 查看 `DOCKER_DEPLOY.md` 的故障排查部分或提交 issue。
