@echo off
REM Redis 连接问题快速修复脚本 (Windows 版本)
REM 用于重新构建后端镜像并重启服务

setlocal enabledelayedexpansion

echo ==================================
echo 🔧 Redis 连接问题快速修复
echo ==================================
echo.

REM 步骤 1: 检查当前位置
echo 步骤 1/5: 检查环境...
if not exist "docker-compose-prod.yml" (
    echo ❌ 错误: 未找到 docker-compose-prod.yml
    echo 请在 deploy-https 目录下运行此脚本
    pause
    exit /b 1
)
echo ✅ 环境检查通过
echo.

REM 步骤 2: 停止现有服务
echo 步骤 2/5: 停止现有服务...
docker compose -f docker-compose-prod.yml down
echo ✅ 服务已停止
echo.

REM 步骤 3: 重新构建后端镜像
echo 步骤 3/5: 重新构建后端镜像...
cd ..
docker build -t deploy-https-backend:v1.0 -f backend/Dockerfile .
if errorlevel 1 (
    echo ❌ 后端镜像构建失败
    pause
    exit /b 1
)
echo ✅ 后端镜像构建成功
cd deploy-https
echo.

REM 步骤 4: 启动所有服务
echo 步骤 4/5: 启动所有服务...
docker compose -f docker-compose-prod.yml up -d
echo ✅ 服务已启动
echo.

REM 步骤 5: 等待服务启动并查看日志
echo 步骤 5/5: 检查服务状态...
echo 等待 10 秒让服务完全启动...
timeout /t 10 /nobreak > nul

echo.
echo ==================================
echo 📊 服务状态
echo ==================================
docker compose -f docker-compose-prod.yml ps

echo.
echo ==================================
echo 📋 后端启动日志（最后 30 行）
echo ==================================
docker logs pm-backend --tail 30

echo.
echo ==================================
echo ✅ 修复完成！
echo ==================================
echo.
echo 🔍 验证步骤：
echo 1. 检查上方日志是否显示: ✅ Redis 连接成功
echo 2. 如果看到 '⚠️ Redis不可用'，请运行:
echo    docker logs -f pm-backend
echo    查看完整日志以诊断问题
echo.
echo 3. 测试 Redis 连接:
echo    docker exec pm-backend python -c "import redis; r=redis.from_url('redis://redis:6379'); print(r.ping())"
echo.
echo 4. 如果仍有问题，请查看详细文档:
echo    type DOCKER_REDIS_CONNECTION_FIX.md
echo.
pause

