# 🔧 生产环境部署修复指南

## 📋 问题汇总

1. **WebSocket 连接失败** - Yjs 协作服务器无法连接
2. **401 Unauthorized** - 认证失败
3. **404 Not Found** - 通知接口不存在

## ✅ 解决方案

### 1. 更新 Nginx 配置

**已修复内容**：

- ✅ 添加了 Yjs WebSocket 代理配置
- ✅ 设置了正确的路由优先级（`^~`）
- ✅ 配置了 WebSocket 超时设置

**关键改动**：

```nginx
# WebSocket proxy for Yjs collaboration (优先级高，必须在 /api/ 之前)
location ^~ /api/collaboration/yjs {
    proxy_pass http://yjs-server:1234;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    # ... 其他配置
}
```

### 2. 服务器部署步骤

#### 步骤 1: 备份当前配置

```bash
cd /path/to/deploy-htttps
cp nginx/default.conf nginx/default.conf.backup
```

#### 步骤 2: 更新 Nginx 配置

```bash
# 将新的 default.conf 上传到服务器
# 或者直接在服务器上修改 nginx/default.conf
```

#### 步骤 3: 重启服务

```bash
# 停止所有服务
docker-compose down

# 重新启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 步骤 4: 验证服务状态

```bash
# 检查所有容器是否运行
docker-compose ps

# 检查 Yjs 服务器日志
docker logs pm-yjs-server

# 检查 Nginx 日志
docker logs pm-frontend

# 检查后端日志
docker logs pm-backend
```

### 3. 验证 WebSocket 连接

#### 方法 1: 使用浏览器控制台

```javascript
// 打开浏览器控制台，输入：
const ws = new WebSocket('wss://192.168.80.100/api/collaboration/yjs/test-doc')
ws.onopen = () => console.log('✅ WebSocket 连接成功')
ws.onerror = (e) => console.error('❌ WebSocket 连接失败:', e)
ws.onmessage = (e) => console.log('📨 收到消息:', e.data)
```

#### 方法 2: 使用 curl 测试 Yjs HTTP 端点

```bash
# 测试 Yjs 服务器是否正常
curl -k https://192.168.80.100/api/collaboration/yjs

# 应该返回类似：
# {"status":"ok","service":"Yjs WebSocket Collaboration Server","version":"1.0.0",...}
```

### 4. 常见问题排查

#### 问题 1: WebSocket 连接仍然失败

```bash
# 检查 Nginx 配置是否生效
docker exec pm-frontend nginx -t

# 重新加载 Nginx 配置
docker exec pm-frontend nginx -s reload

# 检查 Yjs 服务器是否运行
docker ps | grep yjs
docker logs pm-yjs-server --tail 50
```

#### 问题 2: 401 Unauthorized

这通常是 token 过期或未传递。解决方案：

1. 清除浏览器 localStorage
2. 重新登录
3. 检查后端日志是否有 token 验证错误

```bash
# 查看后端日志
docker logs pm-backend --tail 100 | grep -i "token\|auth"
```

#### 问题 3: 404 Not Found (/api/notifications/)

这个接口可能在当前后端版本中不存在或路径错误。可以暂时忽略，或者检查前端是否有调用这个接口的代码。

```bash
# 查找前端中调用 notifications 的代码
grep -r "notifications" dist/ --include="*.js"
```

### 5. 健康检查

运行以下命令检查所有服务状态：

```bash
# 检查所有容器健康状态
docker-compose ps

# 应该看到类似输出：
# NAME            STATUS                 PORTS
# pm-backend      Up (healthy)          0.0.0.0:8000->8000/tcp
# pm-frontend     Up                    0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
# pm-yjs-server   Up (healthy)          0.0.0.0:1234->1234/tcp
# pm-postgres     Up                    0.0.0.0:5432->5432/tcp
# pm-redis        Up                    0.0.0.0:6379->6379/tcp
# pm-minio        Up                    0.0.0.0:9000-9001->9000-9001/tcp
```

### 6. 测试协作功能

1. 打开浏览器访问：`https://192.168.80.100`
2. 登录系统
3. 进入「团队协作」页面
4. 创建或打开一个文档
5. 打开第二个浏览器窗口，登录同一文档
6. 在一个窗口中编辑，应该能在另一个窗口中实时看到变化

### 7. 性能优化建议

#### 生产环境配置调整

**docker-compose.yml**:

```yaml
yjs-server:
  # ... 其他配置
  restart: always # 确保自动重启
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 512M
```

#### Nginx 缓存优化

对于生产环境，可以启用缓存：

```nginx
# 在 server 块中添加
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m;

# 在 location /api/ 中添加
proxy_cache api_cache;
proxy_cache_valid 200 1m;
proxy_cache_bypass $http_cache_control;
add_header X-Cache-Status $upstream_cache_status;
```

### 8. 监控和日志

#### 实时监控日志

```bash
# 监控所有服务日志
docker-compose logs -f

# 只监控 Yjs 服务器
docker logs pm-yjs-server -f

# 只监控 Nginx
docker logs pm-frontend -f

# 只监控后端
docker logs pm-backend -f
```

#### 检查连接数

```bash
# 查看 Yjs 服务器的连接数
docker logs pm-yjs-server | grep "Total connections"

# 查看 Nginx 连接数
docker exec pm-frontend nginx -s reload
docker exec pm-frontend cat /var/log/nginx/access.log | grep "collaboration/yjs" | wc -l
```

## 📞 技术支持

如果遇到问题，请提供以下信息：

1. 完整的错误日志
2. 浏览器控制台截图
3. Docker 容器状态：`docker-compose ps`
4. Nginx 配置验证：`docker exec pm-frontend nginx -t`
5. Yjs 服务器日志：`docker logs pm-yjs-server --tail 100`

## 🎉 完成

按照以上步骤操作后，协作功能应该可以正常工作了！
