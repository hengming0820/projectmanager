# 🔧 WebSocket 连接修复说明

## ✅ 好消息：堆栈溢出已修复！

从日志可以看到：

```
✅ [XNote] 编辑器初始化成功
✅ [XNote] 协作配置已添加到编辑器
✅ [XNote] 协作连接器创建成功
```

**编辑器成功初始化了，没有堆栈溢出错误！** 🎉

## ❌ 当前问题：WebSocket 连接失败

**错误日志**：

```
WebSocket connection to 'ws://localhost:3006/api/collaboration/yjs/doc-xxx' failed
```

**原因分析**：

1. ✅ Yjs 服务器正在运行（端口 1234 LISTENING）
2. ❌ Vite 的 WebSocket 代理配置有误

## 🛠️ 修复方案

### 修改的配置

**文件**: `vite.config.ts`

**问题**：

```typescript
target: 'ws://localhost:1234' // ❌ 错误：不应该用 ws 协议
```

**修复**：

```typescript
target: 'http://localhost:1234' // ✅ 正确：用 http 协议，Vite 会自动升级到 WebSocket
```

### 为什么要用 `http` 而不是 `ws`？

Vite 的 WebSocket 代理基于 `http-proxy`，它的工作原理是：

1. 接收来自浏览器的 WebSocket 升级请求（HTTP → WebSocket）
2. 转发到目标服务器
3. 目标服务器需要是 HTTP 服务器，然后自动升级到 WebSocket

所以配置中 `target` 应该是：

- ✅ `http://localhost:1234`
- ❌ `ws://localhost:1234`

## 🚀 现在需要做什么

### 步骤 1: 再次重启 Vite 服务器

**必须重启**，配置文件已修改！

```bash
# 按 Ctrl+C 停止当前的 Vite
# 然后重新运行
npm run dev
```

### 步骤 2: 刷新页面并观察日志

**浏览器控制台应该看到**：

```
📝 [XNote] 创建空白编辑器
🤝 [XNote] 启用协作模式
🔌 [XNote] 创建协作连接器
✅ [XNote] 协作连接器创建成功
✅ [XNote] 编辑器初始化成功
```

**Vite 终端应该看到**：

```
🔌 [Yjs WS] 代理 WebSocket 连接: /api/collaboration/yjs/doc-xxx
✅ [Yjs WS] WebSocket 连接已建立
```

**Yjs 服务器日志** （如果在单独终端运行）：

```
🔌 [2025-01-xx] New connection for document: doc-xxx
   Total connections: 1
```

### 步骤 3: 测试编辑功能

1. 点击编辑器
2. 输入文字
3. 确认：
   - ✅ 可以正常输入
   - ✅ 没有堆栈溢出错误
   - ✅ 没有 WebSocket 连接失败
   - ✅ 左侧显示"正在编辑 [1]"

## 📊 完整的连接流程

```
┌──────────────────────────────────────────────────────────┐
│ 浏览器                                                    │
│ ws://localhost:3006/api/collaboration/yjs/doc-xxx        │
└──────────────────────────────────────────────────────────┘
                          │
                          │ HTTP Upgrade Request
                          ↓
┌──────────────────────────────────────────────────────────┐
│ Vite Dev Server (localhost:3006)                         │
│ Proxy 配置:                                               │
│   '/api/collaboration/yjs' → http://localhost:1234       │
│   ws: true (允许 WebSocket 升级)                          │
└──────────────────────────────────────────────────────────┘
                          │
                          │ WebSocket 升级
                          ↓
┌──────────────────────────────────────────────────────────┐
│ Yjs WebSocket Server (localhost:1234)                    │
│ 路径: /api/collaboration/yjs                             │
│ 功能: Yjs CRDT 同步                                       │
└──────────────────────────────────────────────────────────┘
```

## 🐛 如果仍然失败

### 检查 1: Yjs 服务器是否运行

```powershell
netstat -ano | findstr :1234
```

应该看到 `LISTENING`

### 检查 2: 手动测试 Yjs 服务器

在浏览器中打开：

```
http://localhost:1234
```

应该返回 JSON：

```json
{
  "status": "ok",
  "message": "Yjs WebSocket Server",
  "version": "1.0.0",
  "activeConnections": 0
}
```

### 检查 3: 测试 WebSocket 连接

在浏览器控制台运行：

```javascript
const ws = new WebSocket('ws://localhost:1234/api/collaboration/yjs')
ws.onopen = () => console.log('✅ 直连成功')
ws.onerror = (err) => console.log('❌ 直连失败:', err)
```

- ✅ 如果成功：说明 Yjs 服务器正常
- ❌ 如果失败：检查 Yjs 服务器日志

### 检查 4: Vite 代理日志

重启 Vite 后，在终端查找：

```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:3006/
```

尝试连接时应该看到：

```
🔌 [Yjs WS] 代理 WebSocket 连接: /api/collaboration/yjs/doc-xxx
```

## 🎯 预期成功状态

**所有检查都通过**：

- [x] 编辑器初始化成功（无堆栈溢出）
- [x] Yjs 服务器运行中
- [ ] WebSocket 连接成功 ⬅️ 当前要修复的
- [ ] 可以正常编辑
- [ ] 多人协作正常同步

---

**请重启 Vite 服务器，然后告诉我 WebSocket 是否连接成功！** 🚀
