@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================
echo 网络访问诊断脚本
echo ================================
echo.

REM 1. 获取本机 IP
echo 🔍 1. 检测本机 IP 地址
echo --------------------------------
set "LOCAL_IP="
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set "ip=%%a"
    set "ip=!ip:~1!"
    if not "!ip:~0,3!"=="127" if not "!ip:~0,3!"=="169" if not "!ip:~0,6!"=="198.18" if not "!ip:~0,7!"=="172.18." (
        if not defined LOCAL_IP (
            set "LOCAL_IP=!ip!"
        )
        echo    - !ip!
    )
)

if not defined LOCAL_IP (
    echo ❌ 未能检测到有效的局域网 IP
    echo    请手动运行 ipconfig 查看
    pause
    exit /b 1
)

echo.
echo ✅ 检测到局域网 IP: !LOCAL_IP!
echo.

REM 2. 检查 Docker 服务
echo 🔍 2. 检查 Docker 服务状态
echo --------------------------------
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未运行或无法连接
    echo    请先启动 Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker 服务正常
echo.

REM 3. 检查容器状态
echo 🔍 3. 检查容器状态
echo --------------------------------
docker ps --filter "name=pm-frontend" --filter "name=pm-backend" --format "{{.Names}}: {{.Status}}"
echo.

REM 4. 检查端口占用
echo 🔍 4. 检查端口占用情况
echo --------------------------------
echo    端口 3006 (前端):
netstat -ano | findstr ":3006 " | findstr "LISTENING"
if errorlevel 1 (
    echo       ❌ 端口 3006 未监听
) else (
    echo       ✅ 端口 3006 正在监听
)

echo    端口 8000 (后端):
netstat -ano | findstr ":8000 " | findstr "LISTENING"
if errorlevel 1 (
    echo       ❌ 端口 8000 未监听
) else (
    echo       ✅ 端口 8000 正在监听
)
echo.

REM 5. 测试本机访问
echo 🔍 5. 测试本机访问
echo --------------------------------
echo    测试 localhost:3006...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3006' -TimeoutSec 5 -UseBasicParsing; Write-Host '       ✅ 可以访问 (状态码:' $response.StatusCode ')' } catch { Write-Host '       ❌ 无法访问:' $_.Exception.Message }"

echo    测试 localhost:8000...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/docs' -TimeoutSec 5 -UseBasicParsing; Write-Host '       ✅ 可以访问 (状态码:' $response.StatusCode ')' } catch { Write-Host '       ❌ 无法访问:' $_.Exception.Message }"
echo.

REM 6. 测试局域网 IP 访问
echo 🔍 6. 测试局域网 IP 访问
echo --------------------------------
echo    测试 !LOCAL_IP!:3006...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://!LOCAL_IP!:3006' -TimeoutSec 5 -UseBasicParsing; Write-Host '       ✅ 可以访问 (状态码:' $response.StatusCode ')' } catch { Write-Host '       ❌ 无法访问:' $_.Exception.Message }"

echo    测试 !LOCAL_IP!:8000...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://!LOCAL_IP!:8000/docs' -TimeoutSec 5 -UseBasicParsing; Write-Host '       ✅ 可以访问 (状态码:' $response.StatusCode ')' } catch { Write-Host '       ❌ 无法访问:' $_.Exception.Message }"
echo.

REM 7. 检查防火墙状态
echo 🔍 7. 检查防火墙状态
echo --------------------------------
powershell -Command "Get-NetFirewallProfile | Select-Object Name, Enabled | Format-Table -AutoSize"
echo.

REM 8. 显示诊断结果
echo ================================
echo 📊 诊断结果汇总
echo ================================
echo.
echo 如果上面所有测试都通过，说明局域网访问已正常配置。
echo.
echo 📱 请使用以下地址访问：
echo    前端: http://!LOCAL_IP!:3006
echo    后端: http://!LOCAL_IP!:8000
echo.
echo 如果有任何测试失败，请检查：
echo    1. Docker 容器是否正在运行 ^(docker ps^)
echo    2. 端口绑定是否为 0.0.0.0:xxxx:xxxx
echo    3. 防火墙是否阻止了端口 3006 和 8000
echo    4. CORS 配置是否包含您的 IP
echo.
echo 💡 详细说明请查看 NETWORK_ACCESS_GUIDE.md
echo.
pause

