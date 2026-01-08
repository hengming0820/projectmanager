@echo off
REM Yjs 协作服务器 Docker 构建脚本 (Windows)

setlocal

echo ========================================
echo  Yjs 协作服务器 Docker 镜像构建
echo ========================================
echo.

REM 检查 Docker 是否安装
echo [1/4] 检查 Docker 环境...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
  echo ❌ 错误: 未检测到 Docker，请先安装 Docker Desktop
  echo.
  echo 下载地址: https://www.docker.com/products/docker-desktop
  echo.
  pause
  exit /b 1
)
echo ✅ Docker 已安装
docker --version
echo.

REM 检查 Docker 是否运行
echo [2/4] 检查 Docker 服务状态...
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

REM 镜像名称和版本
set IMAGE_NAME=deploy-https-yjs
set VERSION=v1.0
set FULL_IMAGE_NAME=%IMAGE_NAME%:%VERSION%

REM 构建镜像
echo [3/4] 构建 Docker 镜像: %FULL_IMAGE_NAME%
echo.
docker build -t %FULL_IMAGE_NAME% .

if %errorlevel% equ 0 (
  echo.
  echo ========================================
  echo ✅ Docker 镜像构建成功
  echo ========================================
  echo.
  
  REM 显示镜像信息
  echo [4/4] 镜像信息:
  docker images %IMAGE_NAME%
  
  echo.
  echo ========================================
  echo 📝 后续步骤:
  echo ========================================
  echo 1. 导出镜像:
  echo    docker save %FULL_IMAGE_NAME% -o %IMAGE_NAME%-v1.0.tar
  echo.
  echo 2. 在目标服务器加载:
  echo    docker load -i %IMAGE_NAME%-v1.0.tar
  echo.
  echo 3. 启动服务:
  echo    cd ..\deploy-htttps
  echo    docker-compose -f docker-compose-prod.yml up -d yjs-server
  echo.
  echo 4. 查看服务状态:
  echo    docker-compose -f docker-compose-prod.yml ps
  echo    docker logs -f pm-yjs-server
  echo ========================================
  echo.
  echo 按任意键退出...
  pause >nul
  exit /b 0
) else (
  echo.
  echo ========================================
  echo ❌ Docker 镜像构建失败
  echo ========================================
  echo.
  echo 常见问题排查:
  echo 1. 检查 Dockerfile 是否存在
  echo 2. 检查 package.json 是否存在
  echo 3. 检查 server.js 是否存在
  echo 4. 查看上方的错误信息
  echo.
  echo 按任意键退出...
  pause >nul
  exit /b 1
)

endlocal

