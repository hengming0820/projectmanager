@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  快速重启后端服务（保留数据库和其他服务）                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM 检查是否在正确的目录
if not exist "docker-compose.yml" (
    echo ❌ 错误：请在 deploy-htttps 目录下运行此脚本
    pause
    exit /b 1
)

echo 📦 第1步：停止后端服务...
docker-compose stop backend
if errorlevel 1 (
    echo ⚠️ 停止后端失败，可能服务未运行
    pause
    exit /b 1
)
echo ✅ 后端已停止
echo.

echo 🏗️ 第2步：重新构建后端镜像...
docker-compose build backend
if errorlevel 1 (
    echo ❌ 构建失败！请检查错误信息
    pause
    exit /b 1
)
echo ✅ 后端镜像构建完成
echo.

echo 🚀 第3步：启动后端服务...
docker-compose up -d backend
if errorlevel 1 (
    echo ❌ 启动失败！请检查错误信息
    pause
    exit /b 1
)
echo ✅ 后端已启动
echo.

echo ⏳ 等待后端初始化（5秒）...
timeout /t 5 /nobreak >nul

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  🎉 后端重启完成！                                           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📊 检查服务状态：
docker-compose ps backend
echo.

echo 📋 后端最新日志（最后20行）：
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker-compose logs --tail=20 backend
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set /p view_logs="是否查看后端实时日志？(y/N): "
if /i "!view_logs!"=="y" (
    echo.
    echo 📋 后端实时日志（按 Ctrl+C 退出）：
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    docker-compose logs -f backend
) else (
    echo.
    echo ✅ 完成！后端服务已重启。
    echo.
    echo 💡 访问地址：
    echo    API 文档: http://localhost:8000/docs
    echo    前端应用: http://localhost:3006
    echo.
    pause
)

