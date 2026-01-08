#!/usr/bin/env node
/**
 * Yjs WebSocket 协作服务器
 * 用于 XNote 编辑器的实时多人协作
 *
 * 快速启动：
 * 1. npm install
 * 2. node server.js
 *
 * 生产部署：
 * 1. npm install -g pm2
 * 2. pm2 start server.js --name yjs-collab
 */

const http = require('http')
const WebSocket = require('ws')
const { setupWSConnection } = require('y-websocket/bin/utils')

// 配置
const PORT = process.env.PORT || 1234
const WS_PATH = '/api/collaboration/yjs'

// 创建 HTTP 服务器
const server = http.createServer((req, res) => {
  res.writeHead(200, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
  })

  res.end(
    JSON.stringify({
      status: 'ok',
      service: 'Yjs WebSocket Collaboration Server',
      version: '1.0.0',
      path: WS_PATH,
      activeConnections: wss ? wss.clients.size : 0
    })
  )
})

// 创建 WebSocket 服务器（不指定 path，手动处理）
const wss = new WebSocket.Server({
  noServer: true // 使用 noServer 模式，手动处理 upgrade
})

// 手动处理 WebSocket 升级请求
server.on('upgrade', (request, socket, head) => {
  const pathname = new URL(request.url, `http://${request.headers.host}`).pathname

  // 只处理以 /api/collaboration/yjs 开头的路径
  if (pathname.startsWith(WS_PATH)) {
    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit('connection', ws, request)
    })
  } else {
    console.log(`❌ 拒绝连接: ${pathname} (不匹配 ${WS_PATH})`)
    socket.destroy()
  }
})

// 存储活动文档
const activeDocs = new Map()

wss.on('connection', (ws, req) => {
  // 从 URL 中提取文档 ID
  // URL 格式: /api/collaboration/yjs/doc-123
  const urlParts = req.url.split('?')[0].split('/')
  const docId = urlParts[urlParts.length - 1] || 'default-doc'

  console.log(`🔌 [${new Date().toISOString()}] New connection for document: ${docId}`)
  console.log(`   Total connections: ${wss.clients.size}`)

  // 记录活动文档
  if (!activeDocs.has(docId)) {
    activeDocs.set(docId, {
      createdAt: new Date(),
      connections: 0
    })
  }
  activeDocs.get(docId).connections++

  // 设置 Yjs WebSocket 连接
  setupWSConnection(ws, req, {
    docName: docId,
    gc: true // 启用垃圾回收
  })

  // 连接关闭时清理
  ws.on('close', () => {
    console.log(`🔌 [${new Date().toISOString()}] Connection closed for document: ${docId}`)

    if (activeDocs.has(docId)) {
      const doc = activeDocs.get(docId)
      doc.connections--

      // 如果文档没有活动连接了，延迟删除
      if (doc.connections <= 0) {
        setTimeout(() => {
          if (activeDocs.has(docId) && activeDocs.get(docId).connections <= 0) {
            activeDocs.delete(docId)
            console.log(`🗑️  Document ${docId} removed from memory`)
          }
        }, 30000) // 30秒后清理
      }
    }
  })
})

// 错误处理
wss.on('error', (error) => {
  console.error('❌ WebSocket Server Error:', error)
})

server.on('error', (error) => {
  console.error('❌ HTTP Server Error:', error)
})

// 启动服务器
server.listen(PORT, () => {
  console.log('╔════════════════════════════════════════════════════════╗')
  console.log('║                                                        ║')
  console.log('║    🚀 Yjs WebSocket Collaboration Server              ║')
  console.log('║                                                        ║')
  console.log('╠════════════════════════════════════════════════════════╣')
  console.log(`║  HTTP Server:    http://localhost:${PORT}                    ║`)
  console.log(`║  WebSocket Path: ${WS_PATH}                 ║`)
  console.log(`║  Status:         ✅ Running                            ║`)
  console.log('╚════════════════════════════════════════════════════════╝')
  console.log('')
  console.log('📝 使用说明:')
  console.log('  1. 前端配置 collaboration-enabled="true"')
  console.log('  2. 设置 document-id 为文档唯一标识')
  console.log('  3. 打开多个浏览器窗口测试协作')
  console.log('')
  console.log('🛑 停止服务: Ctrl+C')
  console.log('')
})

// 定期输出状态
setInterval(() => {
  const activeDocsCount = activeDocs.size
  const totalConnections = wss.clients.size

  if (totalConnections > 0 || activeDocsCount > 0) {
    console.log(
      `📊 [${new Date().toISOString()}] Status: ${totalConnections} connections, ${activeDocsCount} active documents`
    )
  }
}, 60000) // 每分钟

// 优雅退出
process.on('SIGTERM', () => {
  console.log('\n🛑 Received SIGTERM, shutting down gracefully...')
  wss.close(() => {
    server.close(() => {
      console.log('✅ Server closed')
      process.exit(0)
    })
  })
})

process.on('SIGINT', () => {
  console.log('\n🛑 Received SIGINT, shutting down gracefully...')
  wss.close(() => {
    server.close(() => {
      console.log('✅ Server closed')
      process.exit(0)
    })
  })
})
