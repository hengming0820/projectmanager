@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 星像精准研发部管理系统 - 停止所有服务

echo 🛑 停止星像精准研发部管理系统
echo ================================================
echo.

REM 检查是否在正确的目录
if not exist "docker-compose.yml" (
    echo ❌ 错误 请在 deploy-local 目录下运行此脚本
    pause
    exit /b 1
)

REM 询问是否删除数据卷
echo ⚠️ 警告 即将停止所有 Docker 服务
echo.
set /p remove_volumes="是否同时删除数据卷 ^(数据库数据将丢失^)? (y/N): "

echo.
if /i "!remove_volumes!"=="y" (
    echo 🗑️ 停止服务并删除数据卷...
    docker-compose down -v
    echo.
    echo ✅ 服务已停止，数据卷已删除
) else (
    echo 🛑 停止服务（保留数据）...
    docker-compose down
    echo.
    echo ✅ 服务已停止，数据已保留
)

echo.
echo 💡 提示
echo    - 查看状态 docker-compose ps
echo    - 重新启动开发模式 start-dev.bat
echo    - 重新启动生产模式 start-prod.bat
echo.
pause

