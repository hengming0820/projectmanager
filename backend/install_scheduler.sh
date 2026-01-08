#!/bin/bash
# 定时通知功能快速安装脚本

echo "=========================================="
echo "🚀 开始安装定时通知功能..."
echo "=========================================="

# 1. 安装依赖
echo ""
echo "📦 正在安装 APScheduler..."
pip install APScheduler==3.10.4

if [ $? -eq 0 ]; then
    echo "✅ APScheduler 安装成功"
else
    echo "❌ APScheduler 安装失败"
    exit 1
fi

# 2. 检查必要文件
echo ""
echo "🔍 检查必要文件..."

FILES=(
    "app/services/scheduler_service.py"
    "app/services/notification_ws.py"
    "app/main.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
        exit 1
    fi
done

# 3. 测试导入
echo ""
echo "🧪 测试 Python 导入..."
python -c "from apscheduler.schedulers.background import BackgroundScheduler; print('✅ APScheduler 导入成功')"

if [ $? -ne 0 ]; then
    echo "❌ APScheduler 导入失败"
    exit 1
fi

# 4. 完成
echo ""
echo "=========================================="
echo "✅ 定时通知功能安装完成！"
echo "=========================================="
echo ""
echo "📝 下一步："
echo "  1. 启动后端服务："
echo "     python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "  2. 查看启动日志，确认定时任务已加载"
echo ""
echo "  3. 测试功能："
echo "     curl -X POST http://localhost:8000/api/scheduler/trigger-work-reminder \\"
echo "       -H 'Authorization: Bearer YOUR_TOKEN'"
echo ""
echo "📖 详细文档：../SCHEDULED_NOTIFICATION_GUIDE.md"
echo ""

