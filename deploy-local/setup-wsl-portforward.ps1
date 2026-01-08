# WSL Docker 端口转发自动配置脚本
# 需要管理员权限运行

Write-Host "🐧 WSL Docker 端口转发配置脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ 此脚本需要管理员权限" -ForegroundColor Red
    Write-Host "   请右键选择 '以管理员身份运行'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# 获取 WSL IP
Write-Host "🔍 获取 WSL IP 地址..." -ForegroundColor Yellow
try {
    $wslIP = (wsl hostname -I).Trim()
} catch {
    Write-Host "❌ 无法获取 WSL IP 地址" -ForegroundColor Red
    Write-Host "   错误: $_" -ForegroundColor Red
    Write-Host "   请确保 WSL 正在运行" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

if ([string]::IsNullOrEmpty($wslIP)) {
    Write-Host "❌ 无法获取 WSL IP 地址" -ForegroundColor Red
    Write-Host "   请确保 WSL 正在运行" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ WSL IP: $wslIP" -ForegroundColor Green
Write-Host ""

# 删除旧的转发规则
Write-Host "🗑️  删除旧的端口转发规则..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=3006 2>$null
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=3008 2>$null
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=8000 2>$null
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=9001 2>$null
Write-Host "   ✅ 已删除" -ForegroundColor Green
Write-Host ""

# 添加新的转发规则
Write-Host "📡 配置端口转发..." -ForegroundColor Yellow

# 前端端口 3006 (生产)
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3006 connectaddress=$wslIP connectport=3006
Write-Host "   ✅ 3006 (前端-生产) -> $wslIP:3006" -ForegroundColor Green

# 前端端口 3008 (开发)
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3008 connectaddress=$wslIP connectport=3008
Write-Host "   ✅ 3008 (前端-开发) -> $wslIP:3008" -ForegroundColor Green

# 后端端口 8000
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8000 connectaddress=$wslIP connectport=8000
Write-Host "   ✅ 8000 (后端API) -> $wslIP:8000" -ForegroundColor Green

# MinIO 控制台端口 9001
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=9001 connectaddress=$wslIP connectport=9001
Write-Host "   ✅ 9001 (MinIO控制台) -> $wslIP:9001" -ForegroundColor Green

Write-Host ""

# 配置防火墙
Write-Host "🛡️  配置防火墙规则..." -ForegroundColor Yellow

# 检查规则是否已存在并创建
$rules = @(
    @{Name="WSL Docker - Frontend Prod"; Port=3006},
    @{Name="WSL Docker - Frontend Dev"; Port=3008},
    @{Name="WSL Docker - Backend"; Port=8000},
    @{Name="WSL Docker - MinIO"; Port=9001}
)

foreach ($rule in $rules) {
    $existingRule = Get-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue
    
    if (-not $existingRule) {
        New-NetFirewallRule -DisplayName $rule.Name -Direction Inbound -Protocol TCP -LocalPort $rule.Port -Action Allow | Out-Null
        Write-Host "   ✅ 添加端口 $($rule.Port) 防火墙规则" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  端口 $($rule.Port) 防火墙规则已存在" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ 配置完成！" -ForegroundColor Green
Write-Host ""

# 显示当前转发规则
Write-Host "📊 当前端口转发规则：" -ForegroundColor Cyan
Write-Host ""
$portProxyRules = netsh interface portproxy show all
if ($portProxyRules) {
    $portProxyRules | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "   (无规则)" -ForegroundColor Gray
}
Write-Host ""

# 获取 Windows 主机 IP
$windowsIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.IPAddress -like "192.168.*" -or 
    $_.IPAddress -like "10.*" -or 
    ($_.IPAddress -like "172.*" -and $_.IPAddress -notlike "172.1*")
} | Select-Object -First 1).IPAddress

if ($windowsIP) {
    Write-Host "📱 现在可以通过以下地址访问：" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   本机访问 (Windows)：" -ForegroundColor Yellow
    Write-Host "      前端(生产): http://localhost:3006" -ForegroundColor White
    Write-Host "      前端(开发): http://localhost:3008" -ForegroundColor White
    Write-Host "      后端 API:   http://localhost:8000" -ForegroundColor White
    Write-Host "      API 文档:   http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "   局域网访问：" -ForegroundColor Yellow
    Write-Host "      前端(生产): http://$windowsIP:3006" -ForegroundColor White
    Write-Host "      前端(开发): http://$windowsIP:3008" -ForegroundColor White
    Write-Host "      后端 API:   http://$windowsIP:8000" -ForegroundColor White
    Write-Host "      MinIO控制台: http://$windowsIP:9001" -ForegroundColor White
} else {
    Write-Host "📱 现在可以通过以下地址访问：" -ForegroundColor Cyan
    Write-Host "   前端(生产): http://[Windows主机IP]:3006" -ForegroundColor Yellow
    Write-Host "   前端(开发): http://[Windows主机IP]:3008" -ForegroundColor Yellow
    Write-Host "   后端 API:   http://[Windows主机IP]:8000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 重要提示：" -ForegroundColor Cyan
Write-Host "   - WSL 重启后 IP 可能变化，需要重新运行此脚本" -ForegroundColor Gray
Write-Host "   - 可以将此脚本添加到任务计划程序实现开机自启" -ForegroundColor Gray
Write-Host "   - 如果使用 Docker Desktop，通常不需要手动配置" -ForegroundColor Gray
Write-Host ""
Write-Host "📝 测试命令：" -ForegroundColor Cyan
Write-Host "   在 WSL 中: curl http://localhost:3006" -ForegroundColor Gray
Write-Host "   在 Windows: curl http://localhost:3006" -ForegroundColor Gray
Write-Host "   在手机: http://$windowsIP:3006" -ForegroundColor Gray
Write-Host ""
pause

