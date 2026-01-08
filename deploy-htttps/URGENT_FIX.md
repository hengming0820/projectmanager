# 🚨 紧急修复：WebSocket 连接失败

## ⚡ 快速修复步骤

### 问题原因

Nginx 配置中**缺少 Yjs WebSocket 代理**，导致协作功能无法使用。

### 已修复文件

✅ `nginx/default.conf` - 添加了 Yjs WebSocket 代理配置

---

## 📦 服务器部署步骤

### 方法 1: 自动部署（推荐）

#### Windows 服务器:

```bash
cd /path/to/deploy-htttps
redeploy.bat
```

#### Linux/Mac 服务器:

```bash
cd /path/to/deploy-htttps
chmod +x redeploy.sh
./redeploy.sh
```

### 方法 2: 手动部署

```bash
# 1. 进入部署目录
cd /path/to/deploy-htttps

# 2. 停止服务
docker-compose down

# 3. 确认 nginx/default.conf 已更新
# （将本地修改后的文件上传到服务器，或直接在服务器上修改）

# 4. 验证 Nginx 配置
docker run --rm -v $(pwd)/nginx/default.conf:/etc/nginx/conf.d/default.conf:ro nginx nginx -t

# 5. 启动服务
docker-compose up -d

# 6. 查看日志
docker-compose logs -f
```

---

## 🔍 配置验证

### 1. 检查 Nginx 配置是否正确

**关键配置片段**（应该在 `nginx/default.conf` 中）:

```nginx
# WebSocket proxy for Yjs collaboration (优先级高，必须在 /api/ 之前)
location ^~ /api/collaboration/yjs {
    proxy_pass http://yjs-server:1234;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # WebSocket 超时设置
    proxy_connect_timeout 7d;
    proxy_send_timeout 7d;
    proxy_read_timeout 7d;
}
```

**验证命令**:

```bash
# 检查配置文件
cat nginx/default.conf | grep -A 10 "yjs"

# 或在容器中验证
docker exec pm-frontend nginx -t
```

### 2. 测试 WebSocket 连接

#### 测试 1: 浏览器控制台

打开 `https://YOUR_SERVER_IP`，按 `F12` 打开控制台，输入：

```javascript
const ws = new WebSocket('wss://YOUR_SERVER_IP/api/collaboration/yjs/test-doc')
ws.onopen = () => console.log('✅ WebSocket 连接成功')
ws.onerror = (e) => console.error('❌ WebSocket 连接失败:', e)
ws.onmessage = (e) => console.log('📨 收到消息:', e.data)

// 30秒后关闭测试连接
setTimeout(() => ws.close(), 30000)
```

**期望结果**: 应该看到 `✅ WebSocket 连接成功`

#### 测试 2: curl 测试

```bash
# 测试 Yjs HTTP 端点（应该返回 JSON 状态）
curl -k https://YOUR_SERVER_IP/api/collaboration/yjs

# 期望返回类似：
# {"status":"ok","service":"Yjs WebSocket Collaboration Server","version":"1.0.0",...}
```

---

## 🐛 常见问题排查

### 问题 1: WebSocket 仍然连接失败

**原因**: Nginx 配置未生效或路由优先级错误

**解决方案**:

```bash
# 1. 确认配置文件已正确更新
docker exec pm-frontend cat /etc/nginx/conf.d/default.conf | grep "yjs"

# 2. 重新加载 Nginx
docker exec pm-frontend nginx -s reload

# 3. 查看 Nginx 错误日志
docker logs pm-frontend --tail 50
```

### 问题 2: 容器无法启动

**原因**: Nginx 配置语法错误

**解决方案**:

```bash
# 查看容器状态
docker-compose ps

# 查看具体错误
docker logs pm-frontend

# 验证 Nginx 配置语法
docker exec pm-frontend nginx -t

# 如果配置错误，修正后重启
docker-compose restart frontend
```

### 问题 3: Yjs 服务器未运行

**解决方案**:

```bash
# 检查 Yjs 容器状态
docker ps | grep yjs

# 查看 Yjs 日志
docker logs pm-yjs-server

# 如果容器不存在，检查 docker-compose.yml
docker-compose up -d yjs-server

# 手动测试 Yjs 连接
docker exec pm-yjs-server wget -O- http://localhost:1234
```

### 问题 4: 401 Unauthorized

这通常是前端 token 问题，不影响 WebSocket 配置：

**解决方案**:

1. 清除浏览器缓存和 localStorage
2. 重新登录系统
3. 检查后端日志：`docker logs pm-backend | grep -i auth`

---

## ✅ 验证清单

部署完成后，请依次检查：

- [ ] 所有容器都在运行: `docker-compose ps`
- [ ] Nginx 配置验证通过: `docker exec pm-frontend nginx -t`
- [ ] Yjs 服务器正常运行: `docker logs pm-yjs-server | grep Running`
- [ ] WebSocket 测试连接成功（使用浏览器控制台测试）
- [ ] 访问 `https://YOUR_SERVER_IP` 可以正常打开页面
- [ ] 可以成功登录系统
- [ ] 进入「团队协作」页面，打开文档，编辑器正常加载
- [ ] 打开第二个浏览器窗口，编辑同一文档，两个窗口能实时同步

---

## 📊 监控命令

```bash
# 实时查看所有服务日志
docker-compose logs -f

# 只看 Yjs 服务器日志
docker logs pm-yjs-server -f | grep -E "connection|document"

# 只看 Nginx 日志
docker logs pm-frontend -f | grep -E "yjs|websocket"

# 查看 WebSocket 连接统计
docker logs pm-yjs-server | grep "Total connections"
```

---

## 🆘 紧急联系

如果以上步骤都无法解决问题，请提供：

1. **错误截图**: 浏览器控制台的完整错误信息
2. **服务状态**: `docker-compose ps` 的输出
3. **Nginx 配置**: `docker exec pm-frontend cat /etc/nginx/conf.d/default.conf`
4. **Yjs 日志**: `docker logs pm-yjs-server --tail 100`
5. **Nginx 日志**: `docker logs pm-frontend --tail 100`

---

## 📝 补充说明

### Nginx 配置关键点

1. **路由优先级**: 使用 `^~` 确保 `/api/collaboration/yjs` 优先于 `/api/`
2. **WebSocket 升级**: 必须设置 `Upgrade` 和 `Connection` 头
3. **超时设置**: WebSocket 需要长连接，设置超时为 7 天
4. **代理目标**: `http://yjs-server:1234` (容器内部网络)

### Docker 网络说明

所有容器都在 `pm-network` 网络中，可以通过容器名互相访问：

- `backend` → `http://backend:8000`
- `yjs-server` → `http://yjs-server:1234`
- `postgres` → `postgresql://postgres:5432`
- `redis` → `redis://redis:6379`
- `minio` → `http://minio:9000`

---

## 🎉 预期效果

修复完成后：

✅ 进入团队协作页面，打开文档 ✅ 编辑器正常加载，可以输入内容 ✅ 打开第二个浏览器窗口（或无痕模式）✅ 两个窗口中的内容实时同步 ✅ 浏览器控制台没有 WebSocket 连接错误 ✅ 可以看到其他用户的光标位置（如果有协作者）

---

**最后更新**: 2025-01-19 **版本**: v1.0
