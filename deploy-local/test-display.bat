@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 测试脚本 - 验证显示输出

echo ================================
echo 测试 Windows Batch 脚本显示
echo ================================
echo.

REM 设置测试 IP
set "TEST_IP=192.168.200.20"

echo 📌 本机访问地址
echo    前端应用        http://localhost:3006
echo    后端 API        http://localhost:8000
echo    API 文档        http://localhost:8000/docs
echo.
echo 📱 局域网访问地址
echo    前端应用        http://!TEST_IP!:3006
echo    后端 API        http://!TEST_IP!:8000
echo    MinIO 控制台    http://!TEST_IP!:9001
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
echo ================================
echo 测试完成！如果上面显示正常，说明脚本已修复
echo ================================
echo.
pause

