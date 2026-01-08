# 🐧 WSL Docker 局域网访问配置指南

## 📋 WSL 网络架构说明

### WSL2 网络特点

1. **虚拟化网络**：WSL2 运行在 Hyper-V 虚拟机中，拥有独立的虚拟网卡
2. **动态 IP**：WSL2 的 IP 地址每次启动可能变化
3. **NAT 网络**：WSL2 通过 NAT 与 Windows 主机通信
4. **端口转发**：需要 Windows 主机转发端口到 WSL2

### 网络层次结构

```
局域网其他设备
    ↓
Windows 主机 (192.168.200.20)
    ↓ (需要端口转发)
WSL2 虚拟机 (172.x.x.x - 动态)
    ↓
Docker 容器
```

---

## ✅ 方案 1：使用 Docker Desktop (推荐)

如果您使用 **Docker Desktop for Windows**，它会自动处理端口转发。

### 1. 确认 Docker Desktop 配置

1. 打开 Docker Desktop
2. 设置 → Resources → WSL Integration
3. 确保启用了您的 WSL 发行版（如 Ubuntu）
4. 点击 "Apply & Restart"

### 2. 验证端口转发

Docker Desktop 会自动将 WSL2 中的端口转发到 Windows 主机。

**测试**：

```bash
# 在 WSL 终端中
curl http://localhost:3006

# 在 Windows PowerShell 中
curl http://localhost:3006

# 在局域网其他设备
curl http://192.168.200.20:3006
```

如果都能访问，说明 Docker Desktop 的自动转发已生效，**无需额外配置**。

---

## ✅ 方案 2：手动配置端口转发（原生 WSL Docker）

如果您在 WSL 中安装了原生 Docker（不是 Docker Desktop），需要手动配置。

### 1. 查看 WSL IP 地址

**在 WSL 终端中运行**：

```bash
ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1 | head -n1
```

记下这个 IP，例如 `172.25.208.1`

### 2. 配置 Windows 端口转发

**在 Windows PowerShell（管理员）中运行**：

```powershell
# 获取 WSL IP（每次 WSL 重启后可能变化）
wsl hostname -I

# 假设 WSL IP 是 172.25.208.1
$wslIP = "172.25.208.1"

# 转发前端端口 3006
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3006 connectaddress=$wslIP connectport=3006

# 转发后端端口 8000
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8000 connectaddress=$wslIP connectport=8000

# 转发 MinIO 控制台端口 9001
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=9001 connectaddress=$wslIP connectport=9001

# 查看已配置的转发规则
netsh interface portproxy show all
```

### 3. 配置防火墙

**在 Windows PowerShell（管理员）中运行**：

```powershell
New-NetFirewallRule -DisplayName "WSL Docker - Frontend" -Direction Inbound -Protocol TCP -LocalPort 3006 -Action Allow
New-NetFirewallRule -DisplayName "WSL Docker - Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "WSL Docker - MinIO" -Direction Inbound -Protocol TCP -LocalPort 9001 -Action Allow
```

### 4. 删除端口转发（如果需要重新配置）

```powershell
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=3006
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=8000
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=9001
```

---

## 🔧 自动化脚本

### 创建自动转发脚本

创建 `setup-wsl-portforward.ps1`：

```powershell
# WSL Docker 端口转发自动配置脚本
# 需要管理员权限运行

Write-Host "🐧 WSL Docker 端口转发配置脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 获取 WSL IP
Write-Host "🔍 获取 WSL IP 地址..." -ForegroundColor Yellow
$wslIP = (wsl hostname -I).Trim()

if ([string]::IsNullOrEmpty($wslIP)) {
    Write-Host "❌ 无法获取 WSL IP 地址" -ForegroundColor Red
    Write-Host "   请确保 WSL 正在运行" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "✅ WSL IP: $wslIP" -ForegroundColor Green
Write-Host ""

# 删除旧的转发规则
Write-Host "🗑️  删除旧的端口转发规则..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=3006 2>$null
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=8000 2>$null
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=9001 2>$null

# 添加新的转发规则
Write-Host "📡 配置端口转发..." -ForegroundColor Yellow

# 前端端口 3006
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3006 connectaddress=$wslIP connectport=3006
Write-Host "   ✅ 3006 (前端) -> $wslIP:3006" -ForegroundColor Green

# 后端端口 8000
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8000 connectaddress=$wslIP connectport=8000
Write-Host "   ✅ 8000 (后端) -> $wslIP:8000" -ForegroundColor Green

# MinIO 控制台端口 9001
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=9001 connectaddress=$wslIP connectport=9001
Write-Host "   ✅ 9001 (MinIO) -> $wslIP:9001" -ForegroundColor Green

Write-Host ""

# 配置防火墙
Write-Host "🛡️  配置防火墙规则..." -ForegroundColor Yellow

# 检查规则是否已存在
$rule3006 = Get-NetFirewallRule -DisplayName "WSL Docker - Frontend" -ErrorAction SilentlyContinue
$rule8000 = Get-NetFirewallRule -DisplayName "WSL Docker - Backend" -ErrorAction SilentlyContinue
$rule9001 = Get-NetFirewallRule -DisplayName "WSL Docker - MinIO" -ErrorAction SilentlyContinue

if (-not $rule3006) {
    New-NetFirewallRule -DisplayName "WSL Docker - Frontend" -Direction Inbound -Protocol TCP -LocalPort 3006 -Action Allow | Out-Null
    Write-Host "   ✅ 添加端口 3006 防火墙规则" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  端口 3006 防火墙规则已存在" -ForegroundColor Gray
}

if (-not $rule8000) {
    New-NetFirewallRule -DisplayName "WSL Docker - Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow | Out-Null
    Write-Host "   ✅ 添加端口 8000 防火墙规则" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  端口 8000 防火墙规则已存在" -ForegroundColor Gray
}

if (-not $rule9001) {
    New-NetFirewallRule -DisplayName "WSL Docker - MinIO" -Direction Inbound -Protocol TCP -LocalPort 9001 -Action Allow | Out-Null
    Write-Host "   ✅ 添加端口 9001 防火墙规则" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  端口 9001 防火墙规则已存在" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ 配置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📊 当前端口转发规则：" -ForegroundColor Cyan
netsh interface portproxy show all
Write-Host ""
Write-Host "📱 现在可以通过局域网访问：" -ForegroundColor Cyan

# 获取 Windows 主机 IP
$windowsIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*"} | Select-Object -First 1).IPAddress

if ($windowsIP) {
    Write-Host "   前端: http://$windowsIP:3006" -ForegroundColor Yellow
    Write-Host "   后端: http://$windowsIP:8000" -ForegroundColor Yellow
    Write-Host "   MinIO: http://$windowsIP:9001" -ForegroundColor Yellow
} else {
    Write-Host "   前端: http://[Windows主机IP]:3006" -ForegroundColor Yellow
    Write-Host "   后端: http://[Windows主机IP]:8000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Cyan
Write-Host "   - WSL 重启后 IP 可能变化，需要重新运行此脚本" -ForegroundColor Gray
Write-Host "   - 可以将此脚本添加到开机自启动" -ForegroundColor Gray
Write-Host ""
pause
```

### 使用方法

1. **保存脚本**：

   - 将上述内容保存为 `setup-wsl-portforward.ps1`
   - 放在 `deploy-local` 目录

2. **运行脚本**（每次 WSL 重启后）：
   ```powershell
   # 在 Windows PowerShell 中（管理员）
   cd deploy-local
   .\setup-wsl-portforward.ps1
   ```

---

## 🧪 测试脚本

创建 `test-wsl-network.sh`（在 WSL 中运行）：

```bash
#!/bin/bash

echo "================================"
echo "🐧 WSL Docker 网络诊断"
echo "================================"
echo ""

# 1. WSL IP
echo "🔍 1. WSL IP 地址"
echo "--------------------------------"
WSL_IP=$(ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1 | head -n1)
echo "   WSL IP: $WSL_IP"
echo ""

# 2. Windows 主机 IP
echo "🔍 2. Windows 主机 IP (默认网关)"
echo "--------------------------------"
WINDOWS_IP=$(ip route | grep default | awk '{print $3}')
echo "   Windows IP: $WINDOWS_IP"
echo ""

# 3. Docker 容器状态
echo "🔍 3. Docker 容器状态"
echo "--------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "pm-|NAMES"
echo ""

# 4. 端口监听
echo "🔍 4. 端口监听情况"
echo "--------------------------------"
echo "   端口 3006:"
ss -tlnp | grep :3006 || echo "       ❌ 未监听"
echo "   端口 8000:"
ss -tlnp | grep :8000 || echo "       ❌ 未监听"
echo ""

# 5. 测试 WSL 本地访问
echo "🔍 5. 测试 WSL 本地访问"
echo "--------------------------------"
echo "   测试 localhost:3006..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3006 | grep -q "200\|301\|302"; then
    echo "       ✅ 可以访问"
else
    echo "       ❌ 无法访问"
fi

echo "   测试 localhost:8000..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200\|301\|302"; then
    echo "       ✅ 可以访问"
else
    echo "       ❌ 无法访问"
fi
echo ""

# 6. 测试 Windows 主机访问
echo "🔍 6. 测试 Windows 主机访问"
echo "--------------------------------"
echo "   测试 $WINDOWS_IP:3006..."
if curl -s -o /dev/null -w "%{http_code}" http://$WINDOWS_IP:3006 | grep -q "200\|301\|302"; then
    echo "       ✅ 可以访问"
else
    echo "       ❌ 无法访问（可能需要配置 Windows 端口转发）"
fi
echo ""

# 7. 显示诊断结果
echo "================================"
echo "📊 诊断结果"
echo "================================"
echo ""
echo "WSL IP: $WSL_IP"
echo "Windows 主机 IP: $WINDOWS_IP"
echo ""
echo "📱 访问地址："
echo "   从 WSL 访问:      http://localhost:3006"
echo "   从 Windows 访问:  http://localhost:3006 或 http://$WINDOWS_IP:3006"
echo "   从局域网访问:     http://$WINDOWS_IP:3006"
echo ""
echo "💡 如果从 Windows 或局域网无法访问，请在 Windows PowerShell（管理员）运行："
echo "   cd deploy-local"
echo "   .\\setup-wsl-portforward.ps1"
echo ""
```

---

## 📋 完整操作步骤

### 步骤 1：在 WSL 中启动服务

```bash
# 在 WSL 终端中
cd /mnt/d/project_maneger/project_maneger/project_maneger/deploy-local

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps
```

### 步骤 2：配置 Windows 端口转发（如果需要）

**在 Windows PowerShell（管理员）中**：

```powershell
# 方式 1：使用自动化脚本（推荐）
cd d:\project_maneger\project_maneger\project_maneger\deploy-local
.\setup-wsl-portforward.ps1

# 方式 2：手动配置
$wslIP = (wsl hostname -I).Trim()
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3006 connectaddress=$wslIP connectport=3006
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8000 connectaddress=$wslIP connectport=8000
```

### 步骤 3：测试访问

```bash
# 在 WSL 中测试
curl http://localhost:3006

# 在 Windows 中测试
curl http://localhost:3006
curl http://192.168.200.20:3006

# 在局域网其他设备测试
curl http://192.168.200.20:3006
```

---

## 🔄 开机自启动（可选）

### 方式 1：任务计划程序

1. 打开 "任务计划程序"
2. 创建任务
3. 触发器：登录时
4. 操作：启动程序
   - 程序：`powershell.exe`
   - 参数：`-ExecutionPolicy Bypass -File "D:\project_maneger\project_maneger\project_maneger\deploy-local\setup-wsl-portforward.ps1"`
5. 勾选 "使用最高权限运行"

### 方式 2：启动脚本

创建 `startup-wsl-docker.bat`：

```batch
@echo off
echo 正在配置 WSL Docker 端口转发...
powershell -ExecutionPolicy Bypass -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File D:\project_maneger\project_maneger\project_maneger\deploy-local\setup-wsl-portforward.ps1' -Verb RunAs"
```

将此文件添加到：`C:\Users\[你的用户名]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

---

## 🐛 常见问题

### Q1: WSL IP 地址经常变化

**原因**：WSL2 使用动态 IP

**解决**：

1. 使用自动化脚本 `setup-wsl-portforward.ps1`
2. 配置开机自启动
3. 或切换到 Docker Desktop（自动处理）

### Q2: 端口转发不生效

**排查**：

```powershell
# 检查转发规则
netsh interface portproxy show all

# 检查防火墙
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*WSL*"}

# 测试连接
Test-NetConnection -ComputerName localhost -Port 3006
```

### Q3: Docker Desktop vs 原生 Docker

| 特性     | Docker Desktop | 原生 WSL Docker |
| -------- | -------------- | --------------- |
| 端口转发 | ✅ 自动        | ❌ 需手动配置   |
| GUI      | ✅ 有          | ❌ 无           |
| 性能     | 好             | 更好            |
| 资源占用 | 较高           | 较低            |

**建议**：如果需要局域网访问，**Docker Desktop 更方便**。

---

## 📞 获取帮助

如果按照上述步骤仍无法访问：

1. 在 WSL 中运行：`./test-wsl-network.sh`
2. 在 Windows 中查看端口转发：`netsh interface portproxy show all`
3. 检查防火墙规则
4. 提供诊断结果以便进一步排查

---

**版本**: 1.0.0  
**适用于**: WSL2 + Docker  
**最后更新**: 2025-10-17
