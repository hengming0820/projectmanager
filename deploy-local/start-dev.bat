@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 星像精准研发部管理系统 - 开发环境启动脚本 (Windows)

echo 🚀 启动星像精准研发部管理系统 - 开发环境
echo ================================================
echo.

REM 检查是否在正确的目录
if not exist "docker-compose.dev.yml" (
    echo ❌ 错误：请在 deploy-local 目录下运行此脚本
    pause
    exit /b 1
)

REM 1. 启动后端服务
echo 📦 1. 启动后端服务（PostgreSQL, Redis, MinIO, Backend）...
docker-compose -f docker-compose.dev.yml up -d
if errorlevel 1 (
    echo ❌ 启动失败！请检查 Docker 是否运行
    pause
    exit /b 1
)

REM 2. 等待服务启动
echo.
echo ⏳ 2. 等待服务启动...
timeout /t 5 /nobreak >nul

REM 3. 检查服务状态
echo.
echo 📊 3. 检查服务状态...
docker-compose -f docker-compose.dev.yml ps

REM 4. 获取本机 IP 地址
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set "ip=%%a"
    set "ip=!ip:~1!"
    if not "!ip:~0,3!"=="127" if not "!ip:~0,3!"=="169" if not "!ip:~0,6!"=="198.18" if not "!ip:~0,7!"=="172.18." (
        set "DEV_LOCAL_IP=!ip!"
    )
)

REM 5. 显示访问信息
echo.
echo ✅ 后端服务启动完成！
echo ================================================
echo.
echo 📌 本机访问地址
echo    后端 API        http://localhost:8000
echo    API 文档        http://localhost:8000/docs
if defined DEV_LOCAL_IP (
    echo.
    echo 📱 局域网访问地址
    echo    后端 API        http://!DEV_LOCAL_IP!:8000
    echo    MinIO 控制台    http://!DEV_LOCAL_IP!:9001
)
echo.
echo 🔧 服务端口
echo    PostgreSQL      localhost:5432
echo    Redis           localhost:6379
echo    MinIO API       localhost:9000
echo    MinIO 控制台    http://localhost:9001
echo      - 用户名 minioadmin
echo      - 密码 minioadmin123
echo.
echo 🎯 下一步
echo    1. 打开新终端 ^(PowerShell 或 CMD^)
echo    2. 进入项目根目录 ^(上一级目录^)
echo    3. 运行 npm run dev
echo    4. 本机访问 http://localhost:3008
if defined DEV_LOCAL_IP (
    echo    5. 局域网访问 http://!DEV_LOCAL_IP!:3008
)
echo.
echo 💡 提示
echo    - 查看日志 docker-compose -f docker-compose.dev.yml logs -f
echo    - 停止服务 docker-compose -f docker-compose.dev.yml down
echo.
echo 按任意键退出...
pause >nul

