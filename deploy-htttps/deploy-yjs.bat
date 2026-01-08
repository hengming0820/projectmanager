@echo off
REM Yjs 协作服务器部署脚本 (Windows)

setlocal enabledelayedexpansion

echo 🚀 Yjs 协作服务器部署脚本
echo ================================

REM 检查 Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装，请先安装 Docker
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker Compose 未安装，请先安装 Docker Compose
    exit /b 1
)

echo ✅ Docker 环境检查通过

REM 检查镜像是否存在
set IMAGE_NAME=deploy-https-yjs:v1.0
docker images | findstr /C:"deploy-https-yjs" >nul 2>nul

if %errorlevel% neq 0 (
    echo ⚠️  未找到 Yjs 镜像，开始构建...
    
    REM 检查 tar 文件
    if exist "deploy-https-yjs.tar" (
        echo 📦 从 tar 文件加载镜像...
        docker load -i deploy-https-yjs.tar
        echo ✅ 镜像加载成功
    ) else (
        echo 🔨 从源码构建镜像...
        cd ..\yjs-collab-server
        
        if not exist "Dockerfile" (
            echo ❌ 未找到 Dockerfile，请检查 yjs-collab-server 目录
            exit /b 1
        )
        
        docker build -t %IMAGE_NAME% .
        echo ✅ 镜像构建成功
        cd ..\deploy-htttps
    )
) else (
    echo ✅ 找到现有 Yjs 镜像
)

REM 显示当前运行的服务
echo.
echo 📊 当前运行的服务:
docker-compose -f docker-compose-prod.yml ps

REM 询问是否继续
echo.
set /p CONTINUE="是否启动 Yjs 服务？(y/n) "
if /i not "%CONTINUE%"=="y" (
    echo 取消部署
    exit /b 0
)

REM 启动 Yjs 服务
echo.
echo 🚀 启动 Yjs 协作服务器...
docker-compose -f docker-compose-prod.yml up -d yjs-server

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务状态
echo.
echo 📊 Yjs 服务状态:
docker-compose -f docker-compose-prod.yml ps yjs-server

REM 健康检查
echo.
echo 🔍 健康检查:
curl -s http://localhost:1234 >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Yjs 服务运行正常
    echo 📡 WebSocket 地址: ws://localhost:1234/api/collaboration/yjs
) else (
    echo ⚠️  服务可能还在启动中，请稍后检查
    echo 查看日志: docker logs pm-yjs-server
)

REM 显示日志
echo.
set /p SHOWLOGS="是否查看实时日志？(y/n) "
if /i "%SHOWLOGS%"=="y" (
    docker-compose -f docker-compose-prod.yml logs -f yjs-server
)

echo.
echo 🎉 部署完成！
echo.
echo 📝 常用命令:
echo   查看状态: docker-compose -f docker-compose-prod.yml ps yjs-server
echo   查看日志: docker-compose -f docker-compose-prod.yml logs -f yjs-server
echo   重启服务: docker-compose -f docker-compose-prod.yml restart yjs-server
echo   停止服务: docker-compose -f docker-compose-prod.yml stop yjs-server
echo   删除服务: docker-compose -f docker-compose-prod.yml down yjs-server

endlocal

