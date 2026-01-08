# 🌐 网络访问配置指南

本指南说明如何配置和使用局域网访问功能。

---

## 📋 问题说明

**问题**：默认情况下，Docker 容器只能通过 `localhost` 访问，无法通过本机 IP 地址访问。

**原因**：

1. Docker 端口绑定默认可能只绑定到 `127.0.0.1`
2. 后端的 CORS 配置限制了允许的来源

**影响**：

- ❌ 局域网内其他设备无法访问应用
- ❌ 手机、平板等移动设备无法访问
- ❌ 团队成员无法访问你的开发环境

---

## ✅ 解决方案

我们已经完成以下配置，使应用可以通过局域网 IP 访问：

### 1. Docker 端口绑定配置

**修改文件**：`docker-compose.yml`, `docker-compose.dev.yml`

**修改内容**：将所有端口绑定从 `"3006:80"` 改为 `"0.0.0.0:3006:80"`

```yaml
# 修改前（只能本机访问）
ports:
  - "3006:80"
  - "8000:8000"

# 修改后（可以局域网访问）
ports:
  - "0.0.0.0:3006:80"
  - "0.0.0.0:8000:8000"
```

**说明**：

- `0.0.0.0` 表示绑定到所有网络接口
- 允许从任何 IP 地址访问该端口
- 包括本机 IP、localhost、127.0.0.1 等

### 2. CORS 跨域配置

**修改文件**：`docker-compose.yml`, `docker-compose.dev.yml`

**修改内容**：在 `ALLOWED_ORIGINS` 环境变量中添加本机 IP 地址

```yaml
# 修改前
ALLOWED_ORIGINS: '["http://localhost:3006","http://127.0.0.1:3006"]'

# 修改后
ALLOWED_ORIGINS: '["http://localhost:3006","http://127.0.0.1:3006","http://192.168.200.20:3006","http://192.168.200.20:8000"]'
```

**说明**：

- 添加了本机 IP 地址到允许列表
- 前端和后端都需要添加
- 开发模式还需要添加 Vite 的端口 3008

### 3. 启动脚本增强

**修改文件**：`start-prod.bat`, `start-prod.sh`, `start-dev.bat`, `start-dev.sh`

**新功能**：

- ✅ 自动检测本机 IP 地址
- ✅ 显示局域网访问地址
- ✅ 区分本机访问和局域网访问

**示例输出**：

```
✅ 所有服务启动完成！
================================================

📌 本机访问地址：
   前端应用:       http://localhost:3006
   后端 API:       http://localhost:8000
   API 文档:       http://localhost:8000/docs

📱 局域网访问地址：
   前端应用:       http://192.168.200.20:3006
   后端 API:       http://192.168.200.20:8000
   MinIO 控制台:   http://192.168.200.20:9001
```

---

## 🚀 使用方法

### 方式 1：使用启动脚本（推荐）

```bash
# Windows
cd deploy-local
start-prod.bat

# Linux/macOS
cd deploy-local
./start-prod.sh
```

脚本会自动：

1. 检测本机 IP 地址
2. 显示所有可用的访问地址
3. 包括本机访问和局域网访问

### 方式 2：手动查看 IP

如果脚本未能自动检测 IP，可以手动查看：

**Windows**：

```bash
ipconfig
# 查找 "IPv4 地址" 或 "IPv4 Address"
```

**Linux/macOS**：

```bash
ifconfig
# 或
ip addr show
# 查找 inet 后面的地址
```

---

## 📱 访问地址说明

### 本机访问（开发者自己使用）

| 服务     | 地址                         | 说明                    |
| -------- | ---------------------------- | ----------------------- |
| 前端     | `http://localhost:3006`      | 生产模式                |
| 前端     | `http://localhost:3008`      | 开发模式（npm run dev） |
| 后端     | `http://localhost:8000`      | API 服务                |
| API 文档 | `http://localhost:8000/docs` | Swagger 文档            |
| MinIO    | `http://localhost:9001`      | 对象存储控制台          |

### 局域网访问（团队成员、移动设备）

| 服务         | 地址格式               | 示例                         |
| ------------ | ---------------------- | ---------------------------- |
| 前端         | `http://<你的IP>:3006` | `http://192.168.200.20:3006` |
| 前端（开发） | `http://<你的IP>:3008` | `http://192.168.200.20:3008` |
| 后端         | `http://<你的IP>:8000` | `http://192.168.200.20:8000` |
| MinIO        | `http://<你的IP>:9001` | `http://192.168.200.20:9001` |

---

## 🔧 手动配置（如果 IP 变更）

如果您的 IP 地址变更（例如更换网络），需要手动更新配置：

### 1. 查看当前 IP

```bash
# Windows
ipconfig

# Linux/macOS
ifconfig
```

### 2. 更新 docker-compose.yml

编辑 `deploy-local/docker-compose.yml`，找到 `ALLOWED_ORIGINS` 并添加新 IP：

```yaml
ALLOWED_ORIGINS: '["http://localhost:3006","http://localhost:8000","http://127.0.0.1:3006","http://<新IP>:3006","http://<新IP>:8000"]'
```

### 3. 更新 docker-compose.dev.yml

同样更新开发模式配置：

```yaml
ALLOWED_ORIGINS: '["http://localhost:3006","http://localhost:3008","http://localhost:8000","http://127.0.0.1:3006","http://127.0.0.1:3008","http://<新IP>:3006","http://<新IP>:3008","http://<新IP>:8000"]'
```

### 4. 重启服务

```bash
cd deploy-local
docker-compose down
docker-compose up -d
```

---

## 🛡️ 防火墙配置

如果局域网内其他设备仍无法访问，可能是防火墙阻止了连接。

### Windows 防火墙

**方法 1：临时关闭（不推荐）**

控制面板 → Windows Defender 防火墙 → 关闭防火墙

**方法 2：添加端口规则（推荐）**

```powershell
# 以管理员身份运行 PowerShell

# 允许 3006 端口（前端）
netsh advfirewall firewall add rule name="Project Manager - Frontend" dir=in action=allow protocol=TCP localport=3006

# 允许 8000 端口（后端）
netsh advfirewall firewall add rule name="Project Manager - Backend" dir=in action=allow protocol=TCP localport=8000

# 允许 3008 端口（开发前端）
netsh advfirewall firewall add rule name="Project Manager - Dev Frontend" dir=in action=allow protocol=TCP localport=3008
```

### Linux 防火墙（UFW）

```bash
# 允许 3006 端口
sudo ufw allow 3006/tcp

# 允许 8000 端口
sudo ufw allow 8000/tcp

# 允许 3008 端口
sudo ufw allow 3008/tcp

# 重新加载防火墙
sudo ufw reload
```

### macOS 防火墙

系统偏好设置 → 安全性与隐私 → 防火墙 → 防火墙选项 → 允许特定应用

---

## 📊 网络连接测试

### 测试端口是否开放

**在本机测试**：

```bash
# Windows
Test-NetConnection -ComputerName localhost -Port 3006

# Linux/macOS
nc -zv localhost 3006
```

**从其他设备测试**：

```bash
# 替换 <IP> 为服务器 IP
telnet <IP> 3006

# 或使用浏览器直接访问
http://<IP>:3006
```

### 测试 API 连接

```bash
# Windows (PowerShell)
Invoke-WebRequest -Uri http://192.168.200.20:8000/docs

# Linux/macOS
curl http://192.168.200.20:8000/docs
```

---

## 🐛 常见问题

### Q1: 启动脚本没有显示局域网 IP

**原因**：脚本未能自动检测 IP 地址

**解决**：

1. 手动运行 `ipconfig` (Windows) 或 `ifconfig` (Linux/macOS)
2. 找到你的局域网 IP（通常是 192.168.x.x）
3. 直接使用 `http://<IP>:3006` 访问

### Q2: 可以访问前端，但 API 请求失败

**原因**：CORS 配置问题

**解决**：

1. 检查 `docker-compose.yml` 中的 `ALLOWED_ORIGINS`
2. 确保包含了你的 IP 地址
3. 重启服务：`docker-compose down && docker-compose up -d`

### Q3: 局域网内其他设备无法访问

**可能原因**：

1. 防火墙阻止
2. 不在同一局域网
3. Docker 端口绑定错误

**解决步骤**：

1. 检查防火墙设置（参见上方防火墙配置）
2. 确认两台设备在同一局域网（同一 WiFi 或路由器）
3. 验证 docker-compose.yml 中端口绑定为 `0.0.0.0:xxxx:xxxx`

### Q4: 移动设备访问速度很慢

**原因**：网络带宽或路由器性能限制

**建议**：

1. 使用 5GHz WiFi（如果支持）
2. 确保路由器支持足够的并发连接
3. 考虑使用开发模式（压缩更少，调试更方便）

### Q5: IP 地址经常变化怎么办？

**原因**：使用 DHCP 动态分配 IP

**解决**：

1. 在路由器中为你的电脑设置静态 IP（推荐）
2. 或使用通配符 CORS（不推荐用于生产）：
   ```yaml
   ALLOWED_ORIGINS: '["*"]' # 允许所有来源，仅开发环境！
   ```

---

## 📝 配置文件清单

以下文件已修改以支持局域网访问：

| 文件                     | 修改内容               |
| ------------------------ | ---------------------- |
| `docker-compose.yml`     | 端口绑定 + CORS 配置   |
| `docker-compose.dev.yml` | 端口绑定 + CORS 配置   |
| `start-prod.bat`         | 自动检测 IP + 显示地址 |
| `start-prod.sh`          | 自动检测 IP + 显示地址 |
| `start-dev.bat`          | 自动检测 IP + 显示地址 |
| `start-dev.sh`           | 自动检测 IP + 显示地址 |

---

## 🔒 安全建议

### 开发环境

✅ **可以**：

- 允许局域网访问
- 使用宽松的 CORS 配置
- 绑定到 0.0.0.0

### 生产环境

⚠️ **应该**：

1. 使用反向代理（Nginx, Traefik）
2. 配置 HTTPS/SSL 证书
3. 严格限制 CORS 来源
4. 使用环境变量管理配置
5. 考虑使用 VPN 或堡垒机

❌ **不要**：

- 直接暴露端口到公网
- 使用 `ALLOWED_ORIGINS: '["*"]'`
- 使用默认密码

---

## 📞 获取帮助

如果遇到网络访问问题：

1. 查看日志：`docker-compose logs -f backend`
2. 检查端口占用：`netstat -ano | findstr "3006"`
3. 测试网络连接：`telnet <IP> 3006`
4. 查看防火墙规则
5. 提交 Issue 到项目仓库

---

**版本**: 1.0.0  
**最后更新**: 2025-10-17
