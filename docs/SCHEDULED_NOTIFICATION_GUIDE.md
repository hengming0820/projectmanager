# 定时通知功能使用指南

## 📋 功能概述

系统已实现**每天 17:10 自动下班提醒**功能，通过 WebSocket 实时推送通知给所有在线用户。

**提醒内容：**

> 🏃 **下班提醒**  
> 请及时保存文件，填写好今天的工作日志，下班请关电脑！

---

## 🏗️ 技术架构

### 后端实现（推荐方案）

- **定时任务库**：APScheduler 3.10.4
- **通知系统**：WebSocket (FastAPI)
- **时区**：Asia/Shanghai（北京时间）

### 关键组件

1. **`backend/app/services/scheduler_service.py`** - 定时任务服务
2. **`backend/app/services/notification_ws.py`** - WebSocket 通知管理器
3. **`backend/app/main.py`** - 应用启动和任务初始化

---

## 🚀 部署步骤

### 1. 安装依赖

更新后端依赖包：

```bash
cd backend
pip install -r requirements.txt
```

**新增依赖：**

- `APScheduler==3.10.4`

### 2. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 验证启动日志

启动成功后，应该看到以下日志：

```
⏰ [Startup] 正在初始化定时任务...
⏰ [Scheduler] 定时任务调度器已启动
⏰ [Scheduler] 已添加下班提醒任务：每天 17:10
⏰ [Scheduler] 下次执行时间：2025-10-22 17:10:00+08:00
✅ [Startup] 定时任务初始化成功，已加载 1 个任务
  📅 下班提醒 (ID: work_end_reminder) - 下次执行: 2025-10-22 17:10:00+08:00
```

---

## 🧪 测试功能

### 方法 1: API 手动触发（推荐）

**仅管理员可用**

#### 使用 Swagger UI

1. 访问：`http://localhost:8000/docs`
2. 找到 **定时任务** 分组
3. 点击 `POST /api/scheduler/trigger-work-reminder`
4. 点击 **Try it out** → **Execute**

#### 使用 curl

```bash
curl -X POST "http://localhost:8000/api/scheduler/trigger-work-reminder" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应示例：**

```json
{
  "success": true,
  "message": "下班提醒已发送给所有在线用户"
}
```

### 方法 2: 查看定时任务列表

```bash
curl -X GET "http://localhost:8000/api/scheduler/jobs" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应示例：**

```json
{
  "success": true,
  "total": 1,
  "jobs": [
    {
      "id": "work_end_reminder",
      "name": "下班提醒",
      "next_run_time": "2025-10-22 17:10:00.000000+08:00",
      "trigger": "cron[hour='17', minute='10']"
    }
  ]
}
```

### 方法 3: 等待自动触发

每天 17:10，系统会自动执行，后端日志会显示：

```
⏰ [Scheduler] 开始执行下班提醒任务
✅ [Scheduler] 下班提醒已发送给所有在线用户
🔔 [WS] 开始向所有在线用户广播，当前连接数: 5
🔔 [WS] 广播完成，成功: 5/5，失败: 0
```

---

## 🎨 前端接收通知

### 已更新的文件

**`src/store/modules/user.ts`** - WebSocket 通知处理

**关键修改：**

1. ✅ 添加了 `work_end_reminder` 类型的消息处理
2. ✅ 添加了通用通知处理逻辑（支持未来扩展）
3. ✅ 修改通知权限请求为**所有用户**（而不仅仅是管理员/审核员）

### 通知消息格式

```json
{
  "type": "work_end_reminder",
  "title": "🏃 下班提醒",
  "content": "请及时保存文件，填写好今天的工作日志，下班请关电脑！",
  "timestamp": "2025-10-22T17:10:00.123456",
  "priority": "high"
}
```

### 前端显示效果

✅ **页面内通知**（Element Plus Message）

- 黄色警告样式
- 显示 10 秒
- 可手动关闭

✅ **浏览器系统通知**（如果已授权）

- 标题：🏃 下班提醒
- 内容：完整提醒文本
- 点击后聚焦到页面

✅ **自动权限请求**

- 用户登录后自动请求通知权限
- 控制台会显示授权结果

---

## ⚙️ 配置说明

### 修改提醒时间

编辑 `backend/app/services/scheduler_service.py`：

```python
def add_work_end_reminder(self):
    """添加下班提醒任务：每天 17:10"""
    self.scheduler.add_job(
        func=self._send_work_end_reminder,
        trigger=CronTrigger(
            hour=17,      # 修改小时
            minute=10,    # 修改分钟
            timezone='Asia/Shanghai'
        ),
        # ...
    )
```

### 修改提醒内容

编辑 `backend/app/services/scheduler_service.py`：

```python
def _send_work_end_reminder(self):
    """发送下班提醒"""
    message = {
        "type": "work_end_reminder",
        "title": "🏃 下班提醒",
        "content": "请及时保存文件，填写好今天的工作日志，下班请关电脑！",  # 修改这里
        "timestamp": datetime.now().isoformat(),
        "priority": "high"
    }
```

### 添加更多定时任务

在 `scheduler_service.py` 的 `start()` 方法中添加：

```python
def start(self):
    """启动定时任务调度器"""
    if not self.scheduler.running:
        self.scheduler.start()
        logger.info("⏰ [Scheduler] 定时任务调度器已启动")

        # 现有任务
        self.add_work_end_reminder()

        # 添加新任务示例：每天上午9点的早安提醒
        self.add_morning_reminder()

        # 添加新任务示例：每周五下午5点的周报提醒
        self.add_weekly_report_reminder()

def add_morning_reminder(self):
    """添加早安提醒：每天 9:00"""
    self.scheduler.add_job(
        func=self._send_morning_reminder,
        trigger=CronTrigger(hour=9, minute=0, timezone='Asia/Shanghai'),
        id='morning_reminder',
        name='早安提醒',
        replace_existing=True
    )

def _send_morning_reminder(self):
    """发送早安提醒"""
    message = {
        "type": "morning_reminder",
        "title": "☀️ 早安提醒",
        "content": "新的一天开始了，今天也要加油哦！",
        "timestamp": datetime.now().isoformat(),
        "priority": "normal"
    }
    if self._loop and self._loop.is_running():
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast_to_all(message),
            self._loop
        )
```

---

## 🔧 Docker 部署

### 更新 requirements.txt

确保 Docker 容器安装了 APScheduler：

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# 复制并安装依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ... 其他配置
```

### 重新构建镜像

```bash
cd deploy-htttps
docker-compose down
docker-compose build backend
docker-compose up -d
```

---

## 📊 监控和日志

### 查看定时任务日志

```bash
# 开发环境
tail -f backend/app/logs/app.log | grep Scheduler

# Docker 环境
docker logs -f medical-annotation-backend | grep Scheduler
```

### 关键日志标记

- `⏰ [Scheduler]` - 定时任务相关
- `🔔 [WS]` - WebSocket 通知相关
- `✅` - 成功操作
- `❌` - 错误操作
- `⚠️` - 警告信息

---

## ❓ 常见问题

### Q1: 为什么没有收到通知？

**可能原因：**

1. **用户未登录** - 必须登录并建立 WebSocket 连接
2. **浏览器未授权通知** - 检查浏览器通知权限
3. **前端代码未更新** - 确认 `src/store/modules/user.ts` 已更新
4. **时区问题** - 确认服务器时区为 `Asia/Shanghai`
5. **任务未启动** - 检查启动日志是否有错误

**前端排查步骤：**

1. **检查浏览器控制台**

```javascript
// 打开浏览器开发者工具 (F12)
// 查看 Console 标签，应该看到：
🔔 [WS] 收到消息: {type: "work_end_reminder", title: "🏃 下班提醒", ...}
✅ [UserStore] 通知权限已授予
```

2. **检查通知权限**

```javascript
// 在浏览器控制台执行：
Notification.permission
// 应该返回 "granted"，如果是 "denied" 或 "default"，需要重新授权
```

3. **手动授权通知**

- Chrome/Edge: 地址栏左侧 🔒 → 网站设置 → 通知 → 允许
- Firefox: 地址栏左侧 🔒 → 权限 → 接收通知 → 允许

4. **检查 WebSocket 连接**

```javascript
// 浏览器开发者工具 → Network → WS (WebSocket)
// 应该看到 ws://localhost:8000/ws/notifications 连接
// Status: 101 Switching Protocols
```

**后端排查步骤：**

```bash
# 1. 检查在线用户数
curl -X GET "http://localhost:8000/api/scheduler/jobs"

# 2. 手动触发测试
curl -X POST "http://localhost:8000/api/scheduler/trigger-work-reminder" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 查看后端日志
tail -f backend/app/logs/app.log | grep -E "Scheduler|WS"
```

### Q2: 如何临时禁用定时任务？

**方法 1：注释代码**

编辑 `scheduler_service.py`：

```python
def start(self):
    if not self.scheduler.running:
        self.scheduler.start()
        # self.add_work_end_reminder()  # 注释掉
```

**方法 2：环境变量控制**

添加配置项：

```python
# backend/app/config.py
ENABLE_SCHEDULED_NOTIFICATIONS = os.getenv("ENABLE_SCHEDULED_NOTIFICATIONS", "true").lower() == "true"

# scheduler_service.py
from app.config import settings

def start(self):
    if settings.ENABLE_SCHEDULED_NOTIFICATIONS:
        self.add_work_end_reminder()
```

### Q3: 生产环境时间不准确怎么办？

确保服务器和容器时区正确：

```bash
# 检查系统时区
timedatectl

# 设置时区
sudo timedatectl set-timezone Asia/Shanghai

# Docker 中设置时区
docker-compose.yml:
  backend:
    environment:
      - TZ=Asia/Shanghai
```

---

## 📝 文件清单

### 后端文件

| 文件路径                                    | 说明                                     |
| ------------------------------------------- | ---------------------------------------- |
| `backend/requirements.txt`                  | 添加了 APScheduler==3.10.4               |
| `backend/app/services/scheduler_service.py` | **新增**：定时任务服务                   |
| `backend/app/services/notification_ws.py`   | 更新：添加 `broadcast_to_all` 方法       |
| `backend/app/main.py`                       | 更新：启动时初始化定时任务，添加测试接口 |
| `backend/install_scheduler.sh`              | **新增**：Linux 快速安装脚本             |
| `backend/install_scheduler.bat`             | **新增**：Windows 快速安装脚本           |

### 前端文件

| 文件路径                    | 说明                                                          |
| --------------------------- | ------------------------------------------------------------- |
| `src/store/modules/user.ts` | 更新：添加 `work_end_reminder` 消息处理，所有用户请求通知权限 |
| `src/config/headerBar.ts`   | 更新：关闭快速入口控件                                        |

### 文档

| 文件路径                          | 说明                 |
| --------------------------------- | -------------------- |
| `SCHEDULED_NOTIFICATION_GUIDE.md` | **新增**：本使用指南 |

---

## 🎯 总结

✅ **已实现功能：**

- 每天 17:10 自动下班提醒
- WebSocket 实时推送给所有在线用户
- 管理员可手动触发测试
- 查看定时任务列表
- 完善的日志记录

✅ **技术优势：**

- 服务端统一管理，时间准确
- 异步非阻塞，性能优秀
- 支持动态添加任务
- 易于扩展和维护

✅ **用户体验：**

- 无需用户打开页面即可调度
- 关闭页面重新打开后自动重连
- 浏览器原生通知支持

---

## 📞 技术支持

如有问题，请查看：

- 后端日志：`backend/app/logs/app.log`
- API 文档：`http://localhost:8000/docs`
- WebSocket 连接状态：浏览器开发者工具 Network → WS
