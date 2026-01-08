# Yjs 协作服务器

XNote 编辑器的实时多人协作 WebSocket 服务器。

## 🚀 快速启动

### 1. 安装依赖

```bash
npm install
```

### 2. 启动服务器

```bash
npm start
```

服务器将在 `http://localhost:1234` 启动。

### 3. 测试连接

打开浏览器访问：

```
http://localhost:1234
```

应该看到：

```json
{
  "status": "ok",
  "service": "Yjs WebSocket Collaboration Server",
  "version": "1.0.0",
  "path": "/api/collaboration/yjs",
  "activeConnections": 0
}
```

## 📋 可用脚本

```bash
# 开发模式（自动重启）
npm run dev

# 生产模式（PM2）
npm run pm2:start    # 启动守护进程
npm run pm2:stop     # 停止服务
npm run pm2:restart  # 重启服务
npm run pm2:logs     # 查看日志
npm run pm2:delete   # 删除服务
```

## 🔧 配置

### 环境变量

- `PORT`: 服务器端口（默认: 1234）

```bash
PORT=8080 npm start
```

### 修改 WebSocket 路径

编辑 `server.js` 文件，修改 `WS_PATH` 变量：

```javascript
const WS_PATH = '/api/collaboration/yjs'
```

## 🧪 测试协作功能

### 方法 1：修改前端创建页面

编辑 `src/views/collaboration/create/index.vue`：

```vue
<ArtTextbusEditor
  v-model="form.content"
  :height="editorHeight"
  placeholder="开始编写你的文档..."
  :collaboration-enabled="true"
  :document-id="'test-doc-001'"
  :current-user="{
    id: '用户ID',
    username: '用户名',
    color: '#4ade80'
  }"
/>
```

### 方法 2：在浏览器控制台测试

```javascript
// 创建 WebSocket 连接
const ws = new WebSocket('ws://localhost:1234/api/collaboration/yjs/test-doc')

ws.onopen = () => console.log('✅ Connected')
ws.onmessage = (e) => console.log('📨 Message:', e.data)
ws.onerror = (e) => console.error('❌ Error:', e)
ws.onclose = () => console.log('🔌 Closed')
```

### 方法 3：打开多个浏览器窗口

1. 启动协作服务器
2. 打开两个浏览器窗口（可以是隐身模式）
3. 两个窗口都进入创建文档页面
4. 在一个窗口输入，另一个窗口应该实时看到更新

## 📊 日志说明

```
🔌 [时间戳] New connection for document: doc-123
   Total connections: 2
```

- 表示新用户连接到文档

```
📊 [时间戳] Status: 2 connections, 1 active documents
```

- 定期输出服务器状态（每分钟）

```
🗑️  Document doc-123 removed from memory
```

- 文档在无活动连接 30 秒后从内存清理

## 🐛 故障排查

### 问题：无法连接到服务器

**解决方案**：

1. 检查服务器是否运行：`curl http://localhost:1234`
2. 检查防火墙设置
3. 确认端口未被占用

### 问题：前端连接失败

**解决方案**：

1. 打开浏览器控制台，查看 WebSocket 错误
2. 确认前端配置的 URL 正确
3. 检查是否有反向代理拦截 WebSocket

### 问题：协作不生效

**解决方案**：

1. 确认两个用户使用相同的 `document-id`
2. 检查服务器日志，确认两个用户都已连接
3. 刷新页面重试

## 🔒 安全建议

生产环境部署时，建议：

1. **添加身份验证**：验证用户 token
2. **限制连接数**：防止 DDoS 攻击
3. **使用 HTTPS/WSS**：加密传输
4. **设置速率限制**：防止恶意用户
5. **日志记录**：记录所有连接和操作

详见：[../XNOTE_COLLABORATION_GUIDE.md](../XNOTE_COLLABORATION_GUIDE.md)

## 📚 技术栈

- **Yjs**: CRDT 算法库
- **y-websocket**: Yjs WebSocket 服务器
- **ws**: Node.js WebSocket 库

## 📖 更多文档

- [完整部署指南](../XNOTE_COLLABORATION_GUIDE.md)
- [Yjs 官方文档](https://docs.yjs.dev/)
- [y-websocket GitHub](https://github.com/yjs/y-websocket)
