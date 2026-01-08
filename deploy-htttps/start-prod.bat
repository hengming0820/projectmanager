@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 星像精准研发部管理系统 - 生产模式启动脚本 (Windows)

echo 🚀 启动星像精准研发部管理系统 - 生产模式
echo ================================================
echo.

REM 检查是否在正确的目录
if not exist "docker-compose.yml" (
    echo ❌ 错误：请在 deploy-htttps 目录下运行此脚本
    pause
    exit /b 1
)

REM 1. 检查 dist 目录
echo 📁 1. 检查前端构建产物...
if not exist "..\dist" (
    echo ⚠️ dist 目录不存在，开始构建前端...
    cd ..
    call npm run build
    if errorlevel 1 (
        echo ❌ 前端构建失败！
        pause
        exit /b 1
    )
    cd deploy-htttps
    echo ✅ 前端构建完成
) else (
    echo ✅ 发现 dist 目录
    
    REM 询问是否重新构建
    echo.
    set /p rebuild="是否重新构建前端？(y/N): "
    if /i "!rebuild!"=="y" (
        echo 🔨 重新构建前端...
        cd ..
        call npm run build
        if errorlevel 1 (
            echo ❌ 前端构建失败！
            pause
            exit /b 1
        )
        cd deploy-htttps
        echo ✅ 前端重新构建完成
    )
)

REM 2. 启动所有服务
echo.
echo 📦 2. 启动所有服务（PostgreSQL, Redis, MinIO, Backend, Frontend）...
docker-compose up -d
if errorlevel 1 (
    echo ❌ 启动失败！请检查 Docker 是否运行
    pause
    exit /b 1
)

REM 3. 等待服务启动
echo.
echo ⏳ 3. 等待服务启动...
timeout /t 8 /nobreak >nul

REM 4. 检查服务状态
echo.
echo 📊 4. 检查服务状态...
docker-compose ps

REM 5. 获取本机 IP 地址
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set "ip=%%a"
    set "ip=!ip:~1!"
    if not "!ip:~0,3!"=="127" if not "!ip:~0,3!"=="169" if not "!ip:~0,6!"=="198.18" if not "!ip:~0,7!"=="172.18." (
        set "LOCAL_IP=!ip!"
    )
)

REM 6. 显示访问信息
echo.
echo ✅ 所有服务启动完成！
echo ================================================
echo.
echo 📌 本机访问地址
echo    前端应用        http://localhost:3006
echo    后端 API        http://localhost:8000
echo    API 文档        http://localhost:8000/docs
if defined LOCAL_IP (
    echo.
    echo 📱 局域网访问地址
    echo    前端应用        http://!LOCAL_IP!:3006
    echo    后端 API        http://!LOCAL_IP!:8000
    echo    MinIO 控制台    http://!LOCAL_IP!:9001
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
echo 📝 默认登录账号
echo    用户名 admin
echo    密码 admin123
echo.
echo 💡 常用命令
echo    - 查看日志 docker-compose logs -f
echo    - 查看特定服务日志 docker-compose logs -f frontend
echo    - 停止服务 docker-compose down
echo    - 重启服务 docker-compose restart
echo.
echo 按任意键打开前端页面...
pause >nul

REM 打开浏览器
start http://localhost:3006

