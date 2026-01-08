@echo off
chcp 65001 >nul
REM 定时通知功能快速安装脚本（Windows）

echo ==========================================
echo 🚀 开始安装定时通知功能...
echo ==========================================

REM 1. 安装依赖
echo.
echo 📦 正在安装 APScheduler...
pip install APScheduler==3.10.4

if %ERRORLEVEL% EQU 0 (
    echo ✅ APScheduler 安装成功
) else (
    echo ❌ APScheduler 安装失败
    pause
    exit /b 1
)

REM 2. 检查必要文件
echo.
echo 🔍 检查必要文件...

set FILES=app\services\scheduler_service.py app\services\notification_ws.py app\main.py

for %%f in (%FILES%) do (
    if exist "%%f" (
        echo ✅ %%f 存在
    ) else (
        echo ❌ %%f 不存在
        pause
        exit /b 1
    )
)

REM 3. 测试导入
echo.
echo 🧪 测试 Python 导入...
python -c "from apscheduler.schedulers.background import BackgroundScheduler; print('✅ APScheduler 导入成功')"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ APScheduler 导入失败
    pause
    exit /b 1
)

REM 4. 完成
echo.
echo ==========================================
echo ✅ 定时通知功能安装完成！
echo ==========================================
echo.
echo 📝 下一步：
echo   1. 启动后端服务：
echo      python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo   2. 查看启动日志，确认定时任务已加载
echo.
echo   3. 测试功能：
echo      访问 http://localhost:8000/docs
echo      找到 POST /api/scheduler/trigger-work-reminder
echo.
echo 📖 详细文档：..\SCHEDULED_NOTIFICATION_GUIDE.md
echo.
pause

