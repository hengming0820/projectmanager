# 🔧 局域网访问修复指南

## 📋 问题确认

您遇到的问题：**无法通过 192.168.x.x 访问服务**

## ✅ 已完成的修复

### 1. Docker 端口绑定配置

已将所有端口从 `"xxxx:xxxx"` 改为 `"0.0.0.0:xxxx:xxxx"`：

```yaml
# 修复前（只能本机访问）
ports:
  - "3006:80"
  - "8000:8000"

# 修复后（支持局域网访问）
ports:
  - "0.0.0.0:3006:80"
  - "0.0.0.0:8000:8000"
```

### 2. CORS 配置

已确认 `ALLOWED_ORIGINS` 包含您的 IP：

```yaml
ALLOWED_ORIGINS: '["http://localhost:3006","http://localhost:8000","http://127.0.0.1:3006","http://192.168.200.20:3006","http://192.168.200.20:8000"]'
```

---

## 🚀 重启服务（必须执行！）

配置修改后**必须重启 Docker 服务**才能生效：

### 方式 1：使用脚本（推荐）

```batch
cd deploy-local

REM 停止服务
stop-all.bat

REM 重新启动
start-prod.bat
```

### 方式 2：手动重启

```batch
cd deploy-local

REM 停止服务
docker-compose down

REM 重新启动（重新读取配置）
docker-compose up -d

REM 查看状态
docker-compose ps
```

---

## 🧪 测试网络访问

### 自动诊断脚本

我创建了一个诊断脚本，可以自动检测所有可能的问题：

```batch
cd deploy-local
test-network.bat
```

**这个脚本会检查**：

- ✅ 本机 IP 地址
- ✅ Docker 服务状态
- ✅ 容器运行状态
- ✅ 端口监听情况
- ✅ 本机访问测试
- ✅ 局域网 IP 访问测试
- ✅ 防火墙状态

### 手动测试

#### 1. 检查容器状态

```batch
docker ps
```

应该看到以下容器运行中：

- `pm-frontend` (前端)
- `pm-backend` (后端)
- `pm-postgres` (数据库)
- `pm-redis` (缓存)
- `pm-minio` (存储)

#### 2. 检查端口监听

```batch
netstat -ano | findstr "3006"
netstat -ano | findstr "8000"
```

应该看到端口正在监听（LISTENING）。

#### 3. 测试访问

**本机测试**：

```
浏览器访问: http://localhost:3006
```

**局域网测试**：

```
浏览器访问: http://192.168.200.20:3006
```

---

## 🛡️ 防火墙配置

如果服务重启后仍无法访问，可能是防火墙阻止了连接。

### Windows 防火墙规则

**以管理员身份运行 PowerShell**：

```powershell
# 允许 3006 端口（前端）
New-NetFirewallRule -DisplayName "Project Manager - Frontend" -Direction Inbound -Protocol TCP -LocalPort 3006 -Action Allow

# 允许 8000 端口（后端）
New-NetFirewallRule -DisplayName "Project Manager - Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# 允许 3008 端口（开发前端）
New-NetFirewallRule -DisplayName "Project Manager - Dev Frontend" -Direction Inbound -Protocol TCP -LocalPort 3008 -Action Allow
```

### 或者使用图形界面

1. 打开 "Windows Defender 防火墙"
2. 点击 "高级设置"
3. 点击 "入站规则" → "新建规则"
4. 选择 "端口" → 下一步
5. 选择 "TCP"，输入 "3006, 8000, 3008"
6. 选择 "允许连接"
7. 全部勾选（域、专用、公用）
8. 命名为 "Project Manager"
9. 完成

---

## 📊 故障排查清单

### ✅ 配置检查

- [ ] `docker-compose.yml` 中端口绑定为 `0.0.0.0:xxxx:xxxx`
- [ ] `ALLOWED_ORIGINS` 包含您的局域网 IP
- [ ] 已重启 Docker 服务

### ✅ 服务检查

```batch
# 检查容器状态
docker ps

# 检查前端日志
docker logs pm-frontend

# 检查后端日志
docker logs pm-backend
```

### ✅ 网络检查

```batch
# 检查本机 IP
ipconfig

# 检查端口监听
netstat -ano | findstr "3006"
netstat -ano | findstr "8000"

# 测试连接
curl http://localhost:3006
curl http://192.168.200.20:3006
```

### ✅ 防火墙检查

```powershell
# 查看防火墙状态
Get-NetFirewallProfile | Select-Object Name, Enabled

# 查看端口规则
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*3006*"}
```

---

## 🎯 常见问题

### Q1: 重启后仍无法访问

**检查端口绑定是否正确**：

```batch
docker inspect pm-frontend | findstr "HostPort"
docker inspect pm-backend | findstr "HostPort"
```

应该看到类似输出：

```json
"HostIp": "0.0.0.0",
"HostPort": "3006"
```

如果显示 `"HostIp": "127.0.0.1"` 或空，说明配置未生效。

**解决方法**：

```batch
docker-compose down
docker-compose up -d --force-recreate
```

### Q2: 本机可以访问，局域网无法访问

**可能原因**：

1. 防火墙阻止
2. 路由器隔离（AP 隔离）
3. 不在同一网段

**排查步骤**：

1. **在另一台设备上测试 ping**：

   ```batch
   ping 192.168.200.20
   ```

   如果 ping 不通，说明网络不通。

2. **临时关闭防火墙测试**（仅用于诊断）：

   - 控制面板 → Windows Defender 防火墙 → 关闭防火墙
   - 测试访问
   - **重要**：测试完成后记得重新开启！

3. **检查路由器设置**：
   - 登录路由器管理界面
   - 检查是否启用了"AP 隔离"或"客户端隔离"
   - 如果启用，请关闭

### Q3: IP 地址变了怎么办

如果您的 IP 地址经常变化，需要：

1. **更新 docker-compose.yml**：

   ```yaml
   ALLOWED_ORIGINS: '["http://localhost:3006","http://新IP:3006",...]'
   ```

2. **重启服务**：

   ```batch
   docker-compose down
   docker-compose up -d
   ```

3. **建议**：在路由器中设置静态 IP

---

## 📱 成功标志

当一切配置正确后，您应该能够：

✅ 在本机浏览器访问：`http://localhost:3006`  
✅ 在本机浏览器访问：`http://192.168.200.20:3006`  
✅ 在手机浏览器访问：`http://192.168.200.20:3006`  
✅ 在另一台电脑访问：`http://192.168.200.20:3006`

---

## 🔗 相关文档

- **NETWORK_ACCESS_GUIDE.md** - 完整的网络访问配置指南
- **test-network.bat** - 自动诊断脚本
- **README.md** - 部署文档

---

## 📞 仍需帮助？

如果按照上述步骤操作后仍无法访问：

1. 运行诊断脚本：`test-network.bat`
2. 将诊断结果截图或复制
3. 查看容器日志：`docker logs pm-frontend` 和 `docker logs pm-backend`
4. 提供以上信息以便进一步排查

---

**修复日期**: 2025-10-17  
**状态**: ✅ 配置已修复，需要重启服务
