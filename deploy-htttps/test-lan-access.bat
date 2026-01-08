@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo 局域网访问测试工具
echo ============================================
echo.

:: 检查 Docker 是否运行
docker ps >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未运行或未安装
    pause
    exit /b 1
)

:: 步骤1: 检查容器状态
echo ========================================
echo 1. 检查容器状态
echo ========================================
docker ps --filter "name=pm-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

:: 步骤2: 检查端口监听
echo ========================================
echo 2. 检查端口监听状态
echo ========================================
echo [HTTP - 端口 80]
netstat -an | findstr ":80 " | findstr "LISTENING"
if errorlevel 1 (
    echo   [警告] 端口 80 未监听
) else (
    echo   [成功] 端口 80 正在监听
)

echo.
echo [HTTPS - 端口 443]
netstat -an | findstr ":443 " | findstr "LISTENING"
if errorlevel 1 (
    echo   [警告] 端口 443 未监听
) else (
    echo   [成功] 端口 443 正在监听
)

echo.
echo [Backend API - 端口 8000]
netstat -an | findstr ":8000 " | findstr "LISTENING"
if errorlevel 1 (
    echo   [警告] 端口 8000 未监听
) else (
    echo   [成功] 端口 8000 正在监听
)

echo.

:: 步骤3: 测试本地访问
echo ========================================
echo 3. 测试本地访问
echo ========================================

echo [测试 HTTP 访问]
curl -s -o nul -w "  状态码: %%{http_code} (200 为正常)\n" http://localhost 2>nul
if errorlevel 1 (
    echo   [失败] 无法访问 HTTP
)

echo.
echo [测试 Backend API]
curl -s -o nul -w "  状态码: %%{http_code} (200 为正常)\n" http://localhost:8000/docs 2>nul
if errorlevel 1 (
    echo   [失败] 无法访问 Backend API
)

echo.

:: 步骤4: 获取本机 IP
echo ========================================
echo 4. 本机网络信息
echo ========================================
echo [本机 IP 地址]
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    echo   %%a
    set "LOCAL_IP=%%a"
)

echo.

:: 步骤5: 防火墙状态检查
echo ========================================
echo 5. 防火墙状态检查
echo ========================================
powershell -Command "Get-NetFirewallProfile | Select-Object Name, Enabled | Format-Table -AutoSize" 2>nul
if errorlevel 1 (
    echo   [提示] 无法获取防火墙状态（需要管理员权限）
)

echo.

:: 步骤6: 测试建议
echo ========================================
echo 6. 局域网访问测试建议
echo ========================================
echo.
echo 从局域网其他设备（手机、电脑等）访问以下地址：
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    set "ip=%%a"
    set "ip=!ip: =!"
    echo   HTTP:  http://!ip!
    echo   HTTPS: https://!ip!
    echo   API:   http://!ip!:8000/docs
    echo.
)

echo.

:: 步骤7: 常见问题
echo ========================================
echo 7. 如果无法访问，请检查：
echo ========================================
echo.
echo [1] 容器是否正常运行？
echo     docker-compose -f docker-compose-prod.yml ps
echo.
echo [2] 防火墙是否开放端口？
echo     以管理员身份运行 PowerShell：
echo     New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
echo     New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
echo.
echo [3] 其他设备是否在同一局域网？
echo     手机应连接到同一 WiFi，IP 应在同一网段（如 192.168.x.x）
echo.
echo [4] 是否可以 ping 通服务器？
echo     在其他设备上测试: ping !LOCAL_IP!
echo.

:: 步骤8: 快速修复建议
echo ========================================
echo 8. 快速修复
echo ========================================
echo.
set /p "fix=是否需要快速开放防火墙端口？(需要管理员权限) [y/n]: "
if /i "!fix!"=="y" (
    echo.
    echo [执行] 正在开放防火墙端口...
    powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList '-Command', 'New-NetFirewallRule -DisplayName \"项目前端 HTTP\" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow; New-NetFirewallRule -DisplayName \"项目前端 HTTPS\" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow; Write-Host \"防火墙规则已添加，按任意键退出...\"; Read-Host'" 2>nul
    if errorlevel 1 (
        echo   [失败] 请以管理员身份运行此脚本
    ) else (
        echo   [成功] 防火墙规则已添加
    )
)

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
pause

