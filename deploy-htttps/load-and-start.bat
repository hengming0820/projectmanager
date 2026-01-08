@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 生产环境镜像加载和启动脚本 (Windows)
:: Usage: load-and-start.bat [backend-image.tar]

echo ============================================
echo 医学影像标注管理系统 - 生产环境部署
echo ============================================
echo.

:: 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

:: 检查 Docker Compose 是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

:: 获取脚本所在目录
cd /d "%~dp0"
echo [信息] 当前目录: %CD%
echo.

:: ================================
:: 步骤 1/4: 加载 Backend 镜像
:: ================================
echo ================================
echo 步骤 1/4: 加载 Backend 镜像
echo ================================

set "BACKEND_TAR=%~1"
if "%BACKEND_TAR%"=="" set "BACKEND_TAR=deploy-https-backend-v1.0.tar"

:: 支持加载多个镜像文件
set "IMAGE_FILES=%BACKEND_TAR% deploy-https-postgres-v1.0.tar deploy-https-redis-v1.0.tar deploy-https-minio-v1.0.tar"

for %%i in (%IMAGE_FILES%) do (
    if exist "%%i" (
        echo [信息] 正在加载镜像: %%i
        docker load -i "%%i"
        if errorlevel 1 (
            echo [错误] 镜像加载失败: %%i
        ) else (
            echo [成功] 镜像加载成功: %%i
        )
    ) else (
        echo [警告] 未找到镜像文件: %%i ^(跳过^)
    )
)

echo.

:: ================================
:: 步骤 2/4: 验证镜像
:: ================================
echo ================================
echo 步骤 2/4: 验证镜像
echo ================================

docker images | findstr "deploy-https-backend" >nul
if errorlevel 1 (
    echo [错误] Backend 镜像不存在，请检查
    echo [提示] 请确保已加载 deploy-https-backend:v1.0 镜像
    pause
    exit /b 1
)

echo [成功] Backend 镜像已存在
docker images | findstr "deploy-https-backend"
echo.

:: ================================
:: 步骤 3/4: 检查配置文件
:: ================================
echo ================================
echo 步骤 3/4: 检查配置文件
echo ================================

if not exist "docker-compose-prod.yml" (
    echo [错误] 未找到 docker-compose-prod.yml
    pause
    exit /b 1
)

if not exist "..\dist" (
    echo [警告] 未找到前端 dist 目录
    echo 请确保已解压前端文件到上级目录
    set /p "continue=是否继续？(y/n): "
    if /i not "!continue!"=="y" (
        exit /b 1
    )
)

echo [成功] 配置文件检查完成
echo.

:: ================================
:: 步骤 4/4: 启动服务
:: ================================
echo ================================
echo 步骤 4/4: 启动服务
echo ================================

echo [信息] 正在停止旧服务（如果存在）...
docker-compose -f docker-compose-prod.yml down 2>nul

echo.
echo [信息] 正在启动新服务...
docker-compose -f docker-compose-prod.yml up -d

if errorlevel 1 (
    echo [错误] 服务启动失败
    pause
    exit /b 1
)

echo [成功] 服务启动成功
echo.

:: 等待服务启动
echo [信息] 等待服务启动...
timeout /t 10 /nobreak >nul

:: 显示服务状态
echo.
echo ================================
echo 服务状态
echo ================================
docker-compose -f docker-compose-prod.yml ps

echo.
echo ================================
echo 健康检查
echo ================================

:: 检查 Backend
echo [检查] Backend API...
curl -f -s http://localhost:8000/docs >nul 2>&1
if errorlevel 1 (
    echo   Backend API: [失败] 无法访问
) else (
    echo   Backend API: [成功] 正常
)

:: 检查 Frontend
echo [检查] Frontend...
curl -f -s http://localhost/ >nul 2>&1
if errorlevel 1 (
    echo   Frontend:    [失败] 无法访问
) else (
    echo   Frontend:    [成功] 正常
)

:: 检查 PostgreSQL
echo [检查] PostgreSQL...
docker exec pm-postgres2 pg_isready -U admin >nul 2>&1
if errorlevel 1 (
    echo   PostgreSQL:  [失败] 无法连接
) else (
    echo   PostgreSQL:  [成功] 正常
)

:: 检查 Redis
echo [检查] Redis...
docker exec pm-redis2 redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo   Redis:       [失败] 无法连接
) else (
    echo   Redis:       [成功] 正常
)

:: 检查 MinIO
echo [检查] MinIO...
curl -f -s http://localhost:9000/minio/health/live >nul 2>&1
if errorlevel 1 (
    echo   MinIO:       [失败] 无法连接
) else (
    echo   MinIO:       [成功] 正常
)

echo.
echo ================================
echo 部署完成！
echo ================================
echo.
echo 访问地址：
echo   - 前端: http://localhost
echo   - API 文档: http://localhost:8000/docs
echo   - MinIO 控制台: http://localhost:9001
echo.
echo 查看日志：
echo   docker-compose -f docker-compose-prod.yml logs -f
echo.
echo 停止服务：
echo   docker-compose -f docker-compose-prod.yml down
echo.
echo [成功] 部署成功！
echo.
pause

