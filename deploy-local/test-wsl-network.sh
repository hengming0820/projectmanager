#!/bin/bash

# WSL Docker 网络诊断脚本

echo "================================"
echo "🐧 WSL Docker 网络诊断"
echo "================================"
echo ""

# 1. WSL IP
echo "🔍 1. WSL IP 地址"
echo "--------------------------------"
WSL_IP=$(ip addr show eth0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1 | head -n1)
if [ -z "$WSL_IP" ]; then
    echo "   ❌ 无法获取 WSL IP"
else
    echo "   ✅ WSL IP: $WSL_IP"
fi
echo ""

# 2. Windows 主机 IP
echo "🔍 2. Windows 主机 IP (默认网关)"
echo "--------------------------------"
WINDOWS_IP=$(ip route | grep default | awk '{print $3}')
if [ -z "$WINDOWS_IP" ]; then
    echo "   ❌ 无法获取 Windows 主机 IP"
else
    echo "   ✅ Windows IP: $WINDOWS_IP"
fi
echo ""

# 3. Docker 状态
echo "🔍 3. Docker 服务状态"
echo "--------------------------------"
if ! command -v docker &> /dev/null; then
    echo "   ❌ Docker 未安装"
elif ! docker ps &> /dev/null; then
    echo "   ❌ Docker 未运行或无权限"
else
    echo "   ✅ Docker 正常运行"
fi
echo ""

# 4. Docker 容器状态
echo "🔍 4. Docker 容器状态"
echo "--------------------------------"
if docker ps &> /dev/null; then
    docker ps --format "   {{.Names}}: {{.Status}}" | grep "pm-" || echo "   ℹ️  没有运行的项目容器"
else
    echo "   ⚠️  无法检查容器状态"
fi
echo ""

# 5. 端口监听
echo "🔍 5. 端口监听情况"
echo "--------------------------------"
for port in 3006 3008 8000 9001; do
    echo "   端口 $port:"
    if ss -tlnp 2>/dev/null | grep ":$port " > /dev/null; then
        echo "      ✅ 正在监听"
    else
        echo "      ❌ 未监听"
    fi
done
echo ""

# 6. 测试 WSL 本地访问
echo "🔍 6. 测试 WSL 本地访问"
echo "--------------------------------"

test_url() {
    local url=$1
    local name=$2
    echo "   测试 $name..."
    local status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "$url" 2>/dev/null)
    if [ "$status" = "200" ] || [ "$status" = "301" ] || [ "$status" = "302" ]; then
        echo "      ✅ 可以访问 (状态码: $status)"
        return 0
    else
        echo "      ❌ 无法访问 (状态码: $status)"
        return 1
    fi
}

test_url "http://localhost:3006" "localhost:3006 (前端)"
test_url "http://localhost:8000/docs" "localhost:8000 (后端)"
echo ""

# 7. 测试 Windows 主机访问
if [ -n "$WINDOWS_IP" ]; then
    echo "🔍 7. 测试通过 Windows 主机访问"
    echo "--------------------------------"
    test_url "http://$WINDOWS_IP:3006" "$WINDOWS_IP:3006"
    echo ""
fi

# 8. 网络连通性测试
echo "🔍 8. 网络连通性测试"
echo "--------------------------------"
if [ -n "$WINDOWS_IP" ]; then
    echo "   Ping Windows 主机..."
    if ping -c 1 -W 1 "$WINDOWS_IP" > /dev/null 2>&1; then
        echo "      ✅ 可以 ping 通"
    else
        echo "      ❌ 无法 ping 通"
    fi
fi
echo ""

# 9. Docker 网络检查
echo "🔍 9. Docker 网络配置"
echo "--------------------------------"
if docker network ls &> /dev/null; then
    echo "   Docker 网络列表:"
    docker network ls --format "      {{.Name}} ({{.Driver}})" | grep -v "^   $"
fi
echo ""

# 10. 显示诊断结果
echo "================================"
echo "📊 诊断结果汇总"
echo "================================"
echo ""
echo "🌐 网络信息:"
[ -n "$WSL_IP" ] && echo "   WSL IP:         $WSL_IP"
[ -n "$WINDOWS_IP" ] && echo "   Windows 主机:   $WINDOWS_IP"
echo ""

echo "📱 访问地址:"
echo "   从 WSL 访问:"
echo "      http://localhost:3006 (前端)"
echo "      http://localhost:8000 (后端)"
echo ""
echo "   从 Windows 访问:"
echo "      http://localhost:3006 (前端)"
echo "      http://localhost:8000 (后端)"
echo ""
if [ -n "$WINDOWS_IP" ]; then
    echo "   从局域网访问:"
    echo "      http://$WINDOWS_IP:3006 (前端)"
    echo "      http://$WINDOWS_IP:8000 (后端)"
    echo ""
fi

echo "💡 故障排查:"
echo ""

# 检查是否需要配置端口转发
needs_portforward=false
if [ -n "$WINDOWS_IP" ]; then
    status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "http://$WINDOWS_IP:3006" 2>/dev/null)
    if [ "$status" != "200" ] && [ "$status" != "301" ] && [ "$status" != "302" ]; then
        needs_portforward=true
    fi
fi

if [ "$needs_portforward" = true ]; then
    echo "   ⚠️  从 Windows 主机 IP 无法访问"
    echo ""
    echo "   可能原因:"
    echo "   1. 使用原生 WSL Docker (非 Docker Desktop)"
    echo "   2. Windows 端口转发未配置"
    echo ""
    echo "   解决方案:"
    echo "   在 Windows PowerShell (管理员) 中运行:"
    echo "   cd d:\\project_maneger\\project_maneger\\project_maneger\\deploy-local"
    echo "   .\\setup-wsl-portforward.ps1"
    echo ""
else
    echo "   ✅ 网络访问正常"
    echo ""
fi

echo "📚 详细文档:"
echo "   - WSL_NETWORK_GUIDE.md      完整 WSL 网络配置指南"
echo "   - NETWORK_ACCESS_GUIDE.md   通用网络访问指南"
echo "   - fix-network-access.md     故障排查指南"
echo ""

