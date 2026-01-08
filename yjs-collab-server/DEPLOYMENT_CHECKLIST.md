# Yjs 协作服务器部署检查清单

## 📋 部署前检查

### 环境准备

- [ ] Docker 已安装 (版本 >= 20.10)
- [ ] Docker Compose 已安装 (版本 >= 2.0)
- [ ] Node.js 已安装 (版本 >= 16.0，仅本地开发需要)
- [ ] 端口 1234 未被占用
- [ ] 防火墙已配置允许端口 1234

### 文件准备

- [ ] `yjs-collab-server/server.js` 存在
- [ ] `yjs-collab-server/package.json` 存在
- [ ] `yjs-collab-server/Dockerfile` 存在
- [ ] `deploy-htttps/docker-compose-prod.yml` 已更新

---

## 🔨 构建阶段

### 本地构建

- [ ] 运行构建脚本成功
  ```bash
  cd yjs-collab-server
  ./build-docker.sh  # 或 build-docker.bat
  ```
- [ ] 镜像创建成功
  ```bash
  docker images | grep deploy-https-yjs
  # 应显示: deploy-https-yjs   v1.0   ...
  ```
- [ ] 镜像大小合理 (< 200MB)
  ```bash
  docker images deploy-https-yjs:v1.0
  ```

### 镜像导出（可选，用于离线部署）

- [ ] 导出镜像成功
  ```bash
  docker save deploy-https-yjs:v1.0 -o deploy-https-yjs.tar
  ```
- [ ] tar 文件完整 (大小 > 0)
  ```bash
  ls -lh deploy-https-yjs.tar
  ```
- [ ] 复制到目标服务器
  ```bash
  scp deploy-https-yjs.tar user@server:/path/
  ```

---

## 🚀 部署阶段

### 镜像加载（生产环境）

- [ ] 在目标服务器加载镜像
  ```bash
  docker load -i deploy-https-yjs.tar
  ```
- [ ] 验证镜像已加载
  ```bash
  docker images | grep yjs
  ```

### 服务启动

- [ ] 启动 Yjs 服务
  ```bash
  cd deploy-htttps
  docker-compose -f docker-compose-prod.yml up -d yjs-server
  ```
- [ ] 容器状态为 Up
  ```bash
  docker-compose -f docker-compose-prod.yml ps yjs-server
  # 应显示: Up X seconds (healthy)
  ```
- [ ] 无错误日志
  ```bash
  docker logs pm-yjs-server
  # 应看到: ✅ WebSocket server is running on port 1234
  ```

---

## ✅ 验证阶段

### 健康检查

- [ ] HTTP 健康检查通过
  ```bash
  curl http://localhost:1234
  # 应返回 JSON: {"status":"ok",...}
  ```
- [ ] Docker 健康检查通过
  ```bash
  docker inspect pm-yjs-server | grep Health -A 10
  # 应显示: "Status": "healthy"
  ```

### WebSocket 连接测试

- [ ] wscat 测试通过
  ```bash
  npm install -g wscat
  wscat -c ws://localhost:1234/api/collaboration/yjs/test-doc-123
  # 应成功连接
  ```
- [ ] 浏览器测试通过
  ```javascript
  // 在浏览器控制台
  const ws = new WebSocket('ws://localhost:1234/api/collaboration/yjs/test')
  ws.onopen = () => console.log('✅ Connected')
  ```

### 前端集成测试

- [ ] 前端可以连接到 Yjs 服务器
- [ ] 创建新文档可以正常编辑
- [ ] 多用户协作正常工作
- [ ] 在线用户列表显示正确
- [ ] 光标位置同步正常
- [ ] 断线重连机制工作

---

## 🌐 网络配置

### 端口配置

- [ ] 容器内端口 1234 正常监听
- [ ] 宿主机端口 1234 可访问
  ```bash
  netstat -tlnp | grep 1234  # Linux
  netstat -an | findstr :1234  # Windows
  ```
- [ ] 外部可以访问 (如需要)
  ```bash
  curl http://<server-ip>:1234
  ```

### 防火墙配置

- [ ] 防火墙规则已添加

  ```bash
  # Linux (UFW)
  sudo ufw allow 1234/tcp

  # Linux (iptables)
  sudo iptables -A INPUT -p tcp --dport 1234 -j ACCEPT

  # Windows
  netsh advfirewall firewall add rule name="Yjs" dir=in action=allow protocol=TCP localport=1234
  ```

### Nginx 代理（如使用）

- [ ] Nginx 配置已更新
  ```nginx
  location /api/collaboration/yjs {
    proxy_pass http://pm-yjs-server:1234;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
  ```
- [ ] Nginx 已重载
  ```bash
  docker-compose -f docker-compose-prod.yml restart frontend
  ```
- [ ] 代理路径可访问
  ```bash
  curl http://localhost/api/collaboration/yjs
  ```

---

## 🔒 安全配置

### 访问控制

- [ ] 配置了 CORS（如需要）
- [ ] 限制了访问来源（如需要）
- [ ] 配置了 SSL/TLS（生产环境）
  ```nginx
  # 使用 wss:// 而不是 ws://
  location /api/collaboration/yjs {
    proxy_pass http://pm-yjs-server:1234;
    # ... SSL 配置
  }
  ```

### 资源限制

- [ ] 设置了内存限制
  ```yaml
  yjs-server:
    deploy:
      resources:
        limits:
          memory: 512M
  ```
- [ ] 设置了 CPU 限制（可选）
  ```yaml
  yjs-server:
    deploy:
      resources:
        limits:
          cpus: '0.5'
  ```

---

## 📊 监控配置

### 日志配置

- [ ] 日志正常输出
  ```bash
  docker logs pm-yjs-server
  ```
- [ ] 日志轮转已配置
  ```yaml
  yjs-server:
    logging:
      driver: 'json-file'
      options:
        max-size: '10m'
        max-file: '3'
  ```

### 性能监控

- [ ] CPU 使用率正常 (< 50%)
  ```bash
  docker stats pm-yjs-server
  ```
- [ ] 内存使用率正常 (< 80%)
  ```bash
  docker stats pm-yjs-server
  ```
- [ ] 网络流量正常

### 告警配置（可选）

- [ ] 配置了 Prometheus 监控
- [ ] 配置了 Grafana 仪表板
- [ ] 配置了告警规则

---

## 🔄 备份与恢复

### 备份策略

- [ ] 定期导出镜像
  ```bash
  docker save deploy-https-yjs:v1.0 -o yjs-backup-$(date +%Y%m%d).tar
  ```
- [ ] 备份配置文件
  ```bash
  cp docker-compose-prod.yml docker-compose-prod.yml.backup
  ```

### 恢复测试

- [ ] 测试镜像加载
  ```bash
  docker load -i yjs-backup-*.tar
  ```
- [ ] 测试快速恢复
  ```bash
  docker-compose -f docker-compose-prod.yml up -d yjs-server
  ```

---

## 📝 文档更新

### 内部文档

- [ ] 更新部署文档
- [ ] 更新运维手册
- [ ] 记录配置参数

### 团队通知

- [ ] 通知开发团队服务已部署
- [ ] 提供 WebSocket 连接地址
- [ ] 共享监控仪表板链接

---

## 🎯 性能基准

### 初始性能指标

- [ ] 记录启动时间
  ```bash
  docker logs pm-yjs-server | grep "running"
  ```
- [ ] 记录内存基线
  ```bash
  docker stats --no-stream pm-yjs-server
  ```
- [ ] 记录响应时间
  ```bash
  time curl http://localhost:1234
  ```

### 负载测试（可选）

- [ ] 单用户连接测试
- [ ] 多用户并发测试
- [ ] 长时间稳定性测试

---

## 🐛 故障排查准备

### 常用命令整理

```bash
# 查看状态
docker-compose -f docker-compose-prod.yml ps yjs-server

# 查看日志
docker logs -f pm-yjs-server

# 重启服务
docker-compose -f docker-compose-prod.yml restart yjs-server

# 进入容器
docker exec -it pm-yjs-server sh

# 查看网络
docker network inspect pm-network

# 测试连接
curl http://localhost:1234
```

### 联系方式

- [ ] 记录运维负责人联系方式
- [ ] 记录技术支持联系方式
- [ ] 准备故障上报流程

---

## ✨ 最终检查

### 功能验证

- [ ] 创建文档 → 多人编辑 → 实时同步 ✅
- [ ] 用户上线 → 显示在列表 → 光标可见 ✅
- [ ] 断线重连 → 数据恢复 → 继续编辑 ✅
- [ ] 服务重启 → 历史文档 → 可正常加载 ✅

### 性能验证

- [ ] 延迟 < 100ms
- [ ] CPU 使用率 < 50%
- [ ] 内存使用率 < 80%
- [ ] 并发连接数满足需求

### 文档完整性

- [ ] README.md 已更新
- [ ] DOCKER_DEPLOY.md 已创建
- [ ] QUICK_START.md 已创建
- [ ] 本检查清单已完成

---

## 🎉 部署完成

**恭喜！Yjs 协作服务器已成功部署！**

### 快速访问

- **服务地址**: http://localhost:1234
- **WebSocket**: ws://localhost:1234/api/collaboration/yjs
- **健康检查**: http://localhost:1234

### 下一步

1. 通知团队服务已上线
2. 开始使用实时协作功能
3. 监控服务运行状态
4. 收集用户反馈

---

**部署日期**: ******\_\_\_******  
**部署人员**: ******\_\_\_******  
**服务版本**: v1.0  
**签名**: ******\_\_\_******
