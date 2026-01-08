# XNote 实时协作功能部署指南

## 📋 概述

XNote 编辑器已集成实时多人协作功能，使用 **Yjs** CRDT 算法实现无冲突的多人编辑。本指南将帮助您部署和配置协作服务器。

## 🎯 协作功能特性

### ✨ 核心功能

- ✅ **实时同步**：多人同时编辑，实时看到彼此的修改
- ✅ **无冲突合并**：使用 CRDT 算法自动解决编辑冲突
- ✅ **光标共享**：看到其他用户的光标位置和选区
- ✅ **用户标识**：彩色标记区分不同用户
- ✅ **离线支持**：网络断开后自动重连并同步

### 🔧 技术栈

- **前端**：XNote Editor + Yjs + YWebsocketConnector
- **后端**：y-websocket (Node.js) 或 y-py (Python)
- **协议**：WebSocket + Yjs CRDT

## 🏗️ 架构说明

```
┌─────────────────┐     WebSocket      ┌──────────────────┐
│  用户 A 浏览器   │ ←─────────────────→ │                  │
│  XNote Editor   │                     │  Yjs WebSocket   │
└─────────────────┘                     │     Server       │
                                        │                  │
┌─────────────────┐     WebSocket      │  (Node.js/Py)    │
│  用户 B 浏览器   │ ←─────────────────→ │                  │
│  XNote Editor   │                     │  文档状态存储     │
└─────────────────┘                     └──────────────────┘
```

## 🚀 部署方案

### 方案 A：使用 y-websocket (Node.js) - 推荐

#### 1. 安装依赖

```bash
# 创建新目录
mkdir yjs-collab-server
cd yjs-collab-server

# 初始化 npm 项目
npm init -y

# 安装依赖
npm install y-websocket yjs ws
```

#### 2. 创建服务器文件 `server.js`

```javascript
const http = require('http')
const WebSocket = require('ws')
const { setupWSConnection } = require('y-websocket/bin/utils')

// 创建 HTTP 服务器
const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' })
  res.end('Yjs WebSocket Server')
})

// 创建 WebSocket 服务器
const wss = new WebSocket.Server({
  server,
  path: '/api/collaboration/yjs' // 与前端配置的路径一致
})

wss.on('connection', (ws, req) => {
  // 从 URL 参数获取文档名称
  const docName = req.url.split('/').pop() || 'default-doc'
  console.log('New connection for document:', docName)

  setupWSConnection(ws, req, { docName })
})

const PORT = process.env.PORT || 1234
server.listen(PORT, () => {
  console.log(`✅ Yjs WebSocket Server running on http://localhost:${PORT}`)
  console.log(`   WebSocket path: /api/collaboration/yjs`)
})
```

#### 3. 启动服务器

```bash
node server.js
```

#### 4. 使用 PM2 守护进程（生产环境）

```bash
# 安装 PM2
npm install -g pm2

# 启动服务
pm2 start server.js --name yjs-collab

# 查看状态
pm2 status

# 查看日志
pm2 logs yjs-collab

# 设置开机自启
pm2 startup
pm2 save
```

### 方案 B：使用 y-py (Python FastAPI)

#### 1. 安装依赖

```bash
pip install fastapi uvicorn y-py ypy-websocket
```

#### 2. 创建服务器文件 `yjs_server.py`

```python
from fastapi import FastAPI, WebSocket
from ypy_websocket.websocket_server import WebsocketServer
import asyncio

app = FastAPI()

# 创建 Yjs WebSocket 服务器
yws = WebsocketServer()

@app.websocket("/api/collaboration/yjs/{document_id}")
async def websocket_endpoint(websocket: WebSocket, document_id: str):
    await websocket.accept()

    # 处理 Yjs 协议
    await yws.handle_websocket(websocket, document_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1234)
```

#### 3. 启动服务器

```bash
python yjs_server.py
```

### 方案 C：集成到现有 FastAPI 后端

如果您想将 Yjs 服务集成到现有的 FastAPI 后端（`backend/app/main.py`）：

#### 1. 安装 Python 依赖

```bash
cd backend
pip install y-py ypy-websocket
pip freeze > requirements.txt
```

#### 2. 在 `backend/app/main.py` 添加路由

```python
from fastapi import WebSocket, WebSocketDisconnect
from ypy_websocket.websocket_server import WebsocketServer
import asyncio

# 创建 Yjs WebSocket 服务器实例
yjs_server = WebsocketServer()

@app.websocket("/api/collaboration/yjs/{document_id}")
async def yjs_collaboration(websocket: WebSocket, document_id: str):
    """
    Yjs 实时协作 WebSocket 端点
    使用 Yjs CRDT 协议实现多人编辑
    """
    await websocket.accept()

    try:
        # 将 WebSocket 交给 Yjs 服务器处理
        await yjs_server.serve(websocket, document_id)
    except WebSocketDisconnect:
        print(f"Client disconnected from document: {document_id}")
    except Exception as e:
        print(f"Error in Yjs WebSocket: {e}")
```

#### 3. 重启后端服务

```bash
docker-compose restart backend
# 或
uvicorn app.main:app --reload
```

## 🔧 前端配置

### 在创建/编辑页面启用协作

编辑器组件已支持协作，只需传入参数即可：

```vue
<ArtTextbusEditor
  v-model="form.content"
  :height="editorHeight"
  placeholder="开始编写你的文档..."
  :collaboration-enabled="true"
  :document-id="documentId"
  :current-user="{
    id: currentUser.id,
    username: currentUser.username,
    color: '#4ade80'
  }"
/>
```

### 参数说明

| 参数                    | 类型    | 必填 | 说明                     |
| ----------------------- | ------- | ---- | ------------------------ |
| `collaboration-enabled` | boolean | 是   | 是否启用协作模式         |
| `document-id`           | string  | 是   | 文档唯一标识符           |
| `current-user`          | object  | 是   | 当前用户信息             |
| `current-user.id`       | string  | 是   | 用户ID                   |
| `current-user.username` | string  | 是   | 用户名                   |
| `current-user.color`    | string  | 否   | 用户光标颜色（十六进制） |

## 🌐 反向代理配置

### Nginx 配置

如果您使用 Nginx 作为反向代理，需要添加 WebSocket 支持：

```nginx
# 协作服务器 upstream
upstream yjs_collab {
    server localhost:1234;
}

server {
    listen 80;
    server_name your-domain.com;

    # 主应用代理
    location / {
        proxy_pass http://localhost:3006;
        # ... 其他配置
    }

    # Yjs WebSocket 代理
    location /api/collaboration/yjs {
        proxy_pass http://yjs_collab;

        # WebSocket 必需配置
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # 超时设置
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
```

### Docker Compose 配置

如果使用 Docker 部署，添加 Yjs 服务：

```yaml
services:
  # 现有服务...

  yjs-collab:
    image: node:18-alpine
    working_dir: /app
    volumes:
      - ./yjs-collab-server:/app
    ports:
      - '1234:1234'
    command: node server.js
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

## 🧪 测试协作功能

### 1. 启动协作服务器

```bash
# 方案 A (Node.js)
cd yjs-collab-server
node server.js

# 方案 B (Python)
python yjs_server.py
```

### 2. 修改前端配置

在 `src/views/collaboration/create/index.vue` 中，临时启用协作模式：

```vue
<ArtTextbusEditor
  v-model="form.content"
  :height="editorHeight"
  placeholder="开始编写你的文档..."
  :collaboration-enabled="true"
  :document-id="'test-doc-001'"
  :current-user="{
    id: userStore.currentUser.id,
    username: userStore.currentUser.username,
    color: '#4ade80'
  }"
/>
```

### 3. 打开多个浏览器窗口

1. 打开第一个浏览器窗口，进入创建文档页面
2. 打开第二个浏览器窗口（可以是隐身模式），用另一个账号登录
3. 两个窗口都进入同一个文档（使用相同的 `document-id`）
4. 在一个窗口输入，另一个窗口应该实时看到更新

### 4. 查看协作效果

- ✅ **实时同步**：一个用户的输入立即在其他用户的编辑器中显示
- ✅ **光标显示**：看到其他用户的彩色光标和用户名标签
- ✅ **选区高亮**：看到其他用户选中的文字区域
- ✅ **自动重连**：断网后重新连接，内容自动同步

## 🔍 故障排查

### 问题 1：WebSocket 连接失败

**症状**：控制台显示 `WebSocket connection failed`

**排查步骤**：

1. 检查 Yjs 服务器是否正在运行
   ```bash
   curl http://localhost:1234
   ```
2. 检查防火墙设置
3. 查看服务器日志
4. 确认前端 WebSocket URL 配置正确

### 问题 2：协作不生效

**症状**：编辑器初始化成功，但无法看到其他用户的修改

**排查步骤**：

1. 打开浏览器控制台，查看是否有 `🤝 [XNote] 启用协作模式` 日志
2. 检查 `document-id` 是否一致
3. 确认 `collaboration-enabled` 设置为 `true`
4. 查看 WebSocket 连接状态（开发者工具 → Network → WS）

### 问题 3：用户光标不显示

**症状**：内容同步正常，但看不到其他用户的光标

**解决方案**：

- 确认每个用户的 `current-user.color` 不同
- 检查 CSS 是否有 `z-index` 冲突
- 升级 `@textbus/xnote` 到最新版本

## 📊 性能优化

### 1. 内存持久化

默认情况下，Yjs 服务器将文档存储在内存中。生产环境建议使用持久化：

#### LevelDB 持久化 (Node.js)

```bash
npm install y-leveldb
```

```javascript
const { LeveldbPersistence } = require('y-leveldb')

const persistence = new LeveldbPersistence('./yjs-data')

wss.on('connection', (ws, req) => {
  const docName = req.url.split('/').pop() || 'default-doc'
  setupWSConnection(ws, req, {
    docName,
    persistence
  })
})
```

#### Redis 持久化 (Python)

```python
from ypy_websocket.stores import RedisYStore

redis_store = RedisYStore(
    host="localhost",
    port=6379,
    db=0
)

yjs_server = WebsocketServer(rooms_ready=False, auto_clean_rooms=False, ystore=redis_store)
```

### 2. 限制连接数

```javascript
const MAX_CONNECTIONS = 100

wss.on('connection', (ws, req) => {
  if (wss.clients.size > MAX_CONNECTIONS) {
    ws.close(1008, 'Server is full')
    return
  }

  setupWSConnection(ws, req, { docName })
})
```

### 3. 清理过期文档

```javascript
const DOCUMENT_TIMEOUT = 24 * 60 * 60 * 1000 // 24 hours

setInterval(
  () => {
    // 清理超过 24 小时没有活动的文档
    // 具体实现取决于持久化方案
  },
  60 * 60 * 1000
) // 每小时检查一次
```

## 🔐 安全建议

### 1. 身份验证

在 WebSocket 连接时验证用户身份：

```javascript
wss.on('connection', (ws, req) => {
  // 从 URL 或 Header 获取 token
  const token = req.url.split('token=')[1] || req.headers.authorization

  // 验证 token
  if (!verifyToken(token)) {
    ws.close(1008, 'Unauthorized')
    return
  }

  setupWSConnection(ws, req, { docName })
})
```

### 2. 权限控制

确保只有授权用户可以编辑文档：

```javascript
wss.on('connection', (ws, req) => {
  const docName = req.url.split('/').pop()
  const userId = getUserIdFromToken(req)

  // 检查用户是否有权限编辑此文档
  if (!hasPermission(userId, docName, 'edit')) {
    ws.close(1008, 'Forbidden')
    return
  }

  setupWSConnection(ws, req, { docName })
})
```

### 3. 速率限制

防止恶意用户发送大量消息：

```javascript
const rateLimiter = new Map()

wss.on('connection', (ws, req) => {
  const userId = getUserIdFromToken(req)
  const limit = rateLimiter.get(userId) || 0

  if (limit > 100) {
    // 每秒最多 100 条消息
    ws.close(1008, 'Rate limit exceeded')
    return
  }

  // 更新限制
  rateLimiter.set(userId, limit + 1)
  setTimeout(() => rateLimiter.delete(userId), 1000)

  setupWSConnection(ws, req, { docName })
})
```

## 📚 参考资源

- [Yjs 官方文档](https://docs.yjs.dev/)
- [y-websocket GitHub](https://github.com/yjs/y-websocket)
- [XNote 协作配置](xnote/README_COLLABORATION.md)
- [TextBus 协作指南](https://textbus.io/guide/collab/)

## 🆘 获取帮助

如遇到问题，请：

1. 查看服务器日志
2. 检查浏览器控制台
3. 参考本指南的故障排查部分
4. 提交 Issue 到项目仓库

---

**部署完成后，即可享受强大的实时协作功能！** 🎉
