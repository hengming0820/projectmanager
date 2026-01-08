@echo off
REM 🔄 快速重新部署脚本 (Windows)
REM 用于更新 Nginx 配置后重启服务

setlocal

echo ================================================
echo 🔄 开始重新部署服务
echo ================================================
echo.

REM 1. 检查 Docker 是否运行
echo [1/6] 检查 Docker 环境...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
  echo ❌ 错误: Docker 服务未运行
  echo.
  echo 请启动 Docker Desktop 后重试
  echo.
  pause
  exit /b 1
)
echo ✅ Docker 服务正常运行
echo.

REM 2. 检查 Nginx 配置
echo [2/6] 检查 Nginx 配置...
docker exec pm-frontend nginx -t >nul 2>&1
if %errorlevel% equ 0 (
  echo ✅ Nginx 配置验证通过
) else (
  echo ❌ Nginx 配置验证失败，请检查配置文件
  docker exec pm-frontend nginx -t
  pause
  exit /b 1
)
echo.

REM 3. 停止服务
echo [3/6] 停止所有服务...
docker-compose down
echo ✅ 服务已停止
echo.

REM 4. 启动服务
echo [4/6] 启动所有服务...
docker-compose up -d
echo ✅ 服务已启动
echo.

REM 5. 等待服务就绪
echo [5/6] 等待服务就绪...
timeout /t 5 /nobreak >nul
echo.

REM 6. 验证服务状态
echo [6/6] 验证服务状态...
echo.
docker-compose ps
echo.

echo ================================================
echo 🔍 检查关键服务健康状态
echo ================================================
echo.

REM 检查 Yjs 服务器
docker logs pm-yjs-server 2>&1 | findstr /C:"Running" >nul
if %errorlevel% equ 0 (
  echo 🔹 Yjs 服务器: ✅ 正常
) else (
  echo 🔹 Yjs 服务器: ⚠️ 可能未就绪，请稍后检查
)

REM 检查 Postgres
docker exec pm-postgres pg_isready -U admin >nul 2>&1
if %errorlevel% equ 0 (
  echo 🔹 数据库: ✅ 正常
) else (
  echo 🔹 数据库: ❌ 异常
)

REM 检查 Redis
docker exec pm-redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
  echo 🔹 缓存服务: ✅ 正常
) else (
  echo 🔹 缓存服务: ❌ 异常
)

echo.
echo ================================================
echo 🎉 重新部署完成！
echo ================================================
echo.
echo 📝 后续操作：
echo   1. 访问: https://YOUR_SERVER_IP
echo   2. 清除浏览器缓存（Ctrl+Shift+Delete）
echo   3. 重新登录测试
echo   4. 测试协作文档功能
echo.
echo 📊 查看日志：
echo   docker-compose logs -f              # 所有服务
echo   docker logs pm-yjs-server -f        # Yjs 服务器
echo   docker logs pm-frontend -f          # Nginx
echo   docker logs pm-backend -f           # 后端
echo.
echo 按任意键退出...
pause >nul
exit /b 0

