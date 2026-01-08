@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  重新构建后端服务 - 修复PDF中文字体问题                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM 检查是否在正确的目录
if not exist "docker-compose.yml" (
    echo ❌ 错误：请在 deploy-htttps 目录下运行此脚本
    pause
    exit /b 1
)

echo 📦 第1步：停止所有服务...
docker-compose down
if errorlevel 1 (
    echo ⚠️ 停止服务失败，可能服务未运行，继续...
)
echo ✅ 服务已停止
echo.

echo 🗑️ 第2步：删除旧的后端镜像...
docker rmi deploy-htttps-backend -f
if errorlevel 1 (
    echo ⚠️ 删除镜像失败，可能镜像不存在，继续...
)
echo ✅ 旧镜像已删除
echo.

echo 🧹 第3步：清理Docker缓存（可选）...
set /p clean_cache="是否清理Docker构建缓存？(y/N): "
if /i "!clean_cache!"=="y" (
    docker builder prune -f
    echo ✅ 缓存已清理
) else (
    echo ⏭️ 跳过缓存清理
)
echo.

echo 🏗️ 第4步：重新构建后端镜像（这可能需要几分钟）...
echo 正在下载并安装中文字体包...
docker-compose build --no-cache backend
if errorlevel 1 (
    echo ❌ 构建失败！请检查错误信息
    pause
    exit /b 1
)
echo ✅ 后端镜像构建完成
echo.

echo 🚀 第5步：启动所有服务...
docker-compose up -d
if errorlevel 1 (
    echo ❌ 启动失败！请检查错误信息
    pause
    exit /b 1
)
echo ✅ 所有服务已启动
echo.

echo ⏳ 等待服务初始化（10秒）...
timeout /t 10 /nobreak >nul

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  🎉 重新构建完成！                                           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📋 第6步：检查后端日志中的字体加载情况...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docker-compose logs backend | findstr /C:"字体" /C:"font" /C:"Font"
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo 💡 验证建议：
echo    1. 上面应该看到 "✅ 成功加载字体: WQYZenHei" 的日志
echo    2. 如果看到 "❌ 无法加载任何中文字体"，请联系技术支持
echo    3. 访问前端测试PDF导出功能：http://localhost:3006
echo.

echo 📊 查看服务状态：
docker-compose ps
echo.

set /p view_logs="是否查看后端实时日志？(y/N): "
if /i "!view_logs!"=="y" (
    echo.
    echo 📋 后端实时日志（按 Ctrl+C 退出）：
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    docker-compose logs -f backend
) else (
    echo.
    echo ✅ 完成！现在可以测试PDF导出功能了。
    echo.
    pause
)

