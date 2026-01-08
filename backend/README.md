# 医学影像标注管理系统后端

这是一个专用于医学影像标注的内部项目管理系统后端，基于FastAPI构建。

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.104.1-009688.svg" alt="FastAPI">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB.svg" alt="Python">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/PostgreSQL-15+-336791.svg" alt="PostgreSQL">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Redis-5.0+-DC382D.svg" alt="Redis">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/MinIO-7.2.0-C72E49.svg" alt="MinIO">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0.23-D71F00.svg" alt="SQLAlchemy">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Pydantic-2.5.0-E92063.svg" alt="Pydantic">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/WebSocket-Enabled-4FC08D.svg" alt="WebSocket">
</p>

## 功能特性

- 🔐 **用户认证与授权** - JWT token认证，基于角色的权限控制
- 👥 **用户管理** - 用户创建、编辑、删除、状态管理
- 📊 **项目管理** - 创建、编辑、删除标注项目
- 📝 **任务管理** - 任务创建、分配、领取、提交、审核
- 📁 **文件管理** - 医学影像和标注截图的上传存储
- 📈 **绩效统计** - 个人和团队绩效统计
- 🎯 **仪表板** - 项目进度和统计数据展示
- 🔔 **实时通知系统**（v3.3+） - WebSocket + Redis Pub/Sub 实时消息推送
- ⚡ **Redis 全面集成**（v3.3+） - Token管理、消息队列、离线通知存储

## 技术栈

| 类别           | 技术              | 版本    | 说明                               |
| -------------- | ----------------- | ------- | ---------------------------------- |
| **核心框架**   | FastAPI           | 0.104.1 | 现代高性能 Web 框架                |
|                | Uvicorn           | 0.24.0  | ASGI 服务器                        |
|                | Python            | 3.11+   | 编程语言                           |
| **数据存储**   | PostgreSQL        | 15+     | 关系型数据库                       |
|                | Redis             | 5.0+    | 缓存、Token管理、Pub/Sub、离线通知 |
|                | MinIO             | 7.2.0   | 对象存储服务（S3兼容）             |
| **ORM & 验证** | SQLAlchemy        | 2.0.23  | Python ORM 框架                    |
|                | Alembic           | 1.12.1  | 数据库迁移工具                     |
|                | Pydantic          | 2.5.0   | 数据验证与序列化                   |
|                | Pydantic-Settings | 2.1.0   | 配置管理                           |
| **安全认证**   | Python-Jose       | 3.3.0   | JWT Token 处理                     |
|                | Passlib           | 1.7.4   | 密码加密                           |
|                | Bcrypt            | 4.0.1   | 密码哈希算法                       |
| **实时通信**   | WebSocket         | -       | 实时双向通信                       |
|                | Redis Pub/Sub     | -       | 消息队列与广播                     |
| **定时任务**   | APScheduler       | 3.10.4  | 定时任务调度                       |
| **报表生成**   | ReportLab         | 4.0.7   | PDF 报告生成                       |
|                | Matplotlib        | 3.8.2   | 数据可视化图表                     |
| **文件处理**   | Pillow            | 10.1.0  | 图像处理                           |
|                | aiofiles          | 23.2.1  | 异步文件操作                       |
|                | openpyxl          | 3.1.5   | Excel 文件处理                     |
| **其他工具**   | python-dotenv     | 1.0.0   | 环境变量管理                       |
|                | email_validator   | 2.2.0   | 邮箱验证                           |
|                | python-dateutil   | 2.8.2   | 日期时间工具                       |
| **API 文档**   | OpenAPI/Swagger   | -       | 自动 API 文档生成                  |

## 快速开始

### 1. 环境要求

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 环境配置

复制环境变量示例文件：

```bash
cp env_example.txt .env
```

编辑 `.env` 文件，配置数据库连接等信息。

### 4. 启动服务

#### 使用Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

#### 手动启动

```bash
# 启动数据库和Redis（需要先安装）
# 启动MinIO（需要先安装）

# 初始化数据库
python scripts/init_db.py

# 启动应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问服务

- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health
- **MinIO控制台**: http://localhost:9001

## 默认用户

系统初始化后会创建以下默认用户：

| 用户名     | 密码         | 角色      | 说明       |
| ---------- | ------------ | --------- | ---------- |
| admin      | admin123     | admin     | 系统管理员 |
| annotator1 | annotator123 | annotator | 标注员1    |
| annotator2 | annotator123 | annotator | 标注员2    |
| annotator3 | annotator123 | annotator | 标注员3    |

## API接口

### 认证相关

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 用户管理

- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建用户
- `GET /api/users/{id}` - 获取用户详情
- `PUT /api/users/{id}` - 更新用户信息
- `DELETE /api/users/{id}` - 删除用户
- `POST /api/users/{id}/toggle-status` - 切换用户状态
- `GET /api/users/stats/summary` - 获取用户统计

### 项目管理

- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建项目
- `GET /api/projects/{id}` - 获取项目详情
- `PUT /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目

### 任务管理

- `GET /api/tasks` - 获取任务列表
- `POST /api/tasks` - 创建任务
- `GET /api/tasks/{id}` - 获取任务详情
- `POST /api/tasks/{id}/claim` - 领取任务
- `POST /api/tasks/{id}/submit` - 提交任务
- `POST /api/tasks/{id}/abandon` - 放弃任务
- `POST /api/tasks/{id}/review` - 审核任务
- `DELETE /api/tasks/{id}` - 删除任务

### 绩效管理

- `GET /api/performance/stats` - 获取绩效统计
- `GET /api/performance/personal` - 获取个人绩效
- `GET /api/performance/project/{id}/stats` - 获取项目统计
- `GET /api/performance/dashboard` - 获取仪表板数据

### 通知管理（v3.3+）

- `GET /api/notifications/` - 获取未读通知列表
- `GET /api/notifications/unread-count` - 获取未读通知数量
- `PUT /api/notifications/{id}/read` - 标记单条通知已读
- `PUT /api/notifications/read-all` - 标记全部通知已读
- `DELETE /api/notifications/{id}` - 删除单条通知
- `DELETE /api/notifications/clear-read` - 清除所有已读通知

### WebSocket 实时通知（v3.3+）

**连接地址**: `ws://localhost:8000/ws/notifications`

**初始消息**（连接后立即发送）:

```json
{
  "role": "annotator",
  "user": "user_id"
}
```

**接收消息格式**:

```json
{
  "type": "task_submitted",
  "content": "标注员提交了任务：肺部CT标注",
  "task_id": "uuid",
  "priority": "high",
  "pending": 5
}
```

**心跳机制**:

- 客户端每30秒发送 `{"type": "ping", "user_id": "xxx", "timestamp": 123456}`
- 服务端响应 `{"type": "pong", "timestamp": 123456}`

## 数据库设计

### 核心表结构

1. **users** - 用户表
2. **projects** - 项目表
3. **tasks** - 任务表
4. **task_attachments** - 任务附件表
5. **performance_stats** - 绩效统计表
6. **project_stats** - 项目统计表

### 文件存储

- 医学影像文件存储在MinIO的 `medical-annotations` 桶中
- 文件按类型分类存储：
  - `annotations/{task_id}/` - 标注截图
  - `reviews/{task_id}/` - 审核截图
  - `uploads/` - 其他上传文件

### Redis 存储设计（v3.3+）

#### Token 管理

```python
# Redis Key 格式
token:{token_hash}  # SET, TTL=ACCESS_TOKEN_EXPIRE_MINUTES
user:{user_id}:token  # STRING, 存储当前 token
```

#### 离线通知存储

```python
# Redis Key 格式
notifications:user:{user_id}  # LIST, TTL=7天, 最多50条
```

**数据结构示例**：

```json
{
  "id": "uuid",
  "type": "task_approved",
  "title": "任务通过审核",
  "content": "您的任务已通过审核",
  "priority": "normal",
  "created_at": "2025-11-03T10:00:00Z",
  "task_id": "task_uuid"
}
```

#### Pub/Sub 频道

```
notify:user:{user_id}       # 用户私有频道
notify:role:{role}           # 角色广播频道（admin/reviewer/annotator）
notify:project:{project_id}  # 项目频道
notify:global                # 全局广播频道
```

## 用户管理功能

### 用户角色

- **admin** - 管理员：可以管理所有功能，包括用户管理
- **annotator** - 标注员：只能进行任务标注和查看个人绩效

### 用户状态

- **active** - 活跃：用户可以正常登录和使用系统
- **inactive** - 禁用：用户无法登录系统

### 安全限制

- 管理员不能删除自己的账户
- 管理员不能修改自己的角色
- 管理员不能禁用自己的账户
- 有未完成任务的用户不能被删除

## 开发指南

### 项目结构

```
backend/
├── app/
│   ├── api/              # API路由
│   │   ├── auth.py       # 认证登录
│   │   ├── users.py      # 用户管理
│   │   ├── tasks.py      # 任务管理
│   │   ├── notifications.py  # 通知管理（v3.3+）
│   │   └── ...
│   ├── models/           # 数据库模型
│   ├── schemas/          # Pydantic模型
│   ├── services/         # 业务逻辑
│   │   ├── notification_ws.py  # WebSocket通知服务（v3.3+）
│   │   ├── redis_notification_service.py  # Redis Pub/Sub服务（v3.3+）
│   │   ├── redis_notification_storage.py  # Redis离线通知存储（v3.3+）
│   │   └── ...
│   ├── utils/            # 工具函数
│   │   ├── security.py   # JWT、密码加密
│   │   ├── redis_client.py  # Redis客户端
│   │   ├── token_manager.py  # Token管理
│   │   └── ...
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接
│   └── main.py           # 应用入口（包含WebSocket端点）
├── scripts/              # 脚本文件
├── requirements.txt      # 依赖列表
├── docker-compose.yml    # Docker配置
├── Dockerfile           # Docker镜像
└── README.md            # 项目说明
```

### 添加新功能

1. 在 `app/models/` 中定义数据库模型
2. 在 `app/schemas/` 中定义Pydantic模型
3. 在 `app/services/` 中实现业务逻辑
4. 在 `app/api/` 中定义API路由
5. 在 `app/main.py` 中注册路由

### 发送实时通知（v3.3+）

```python
from app.services.notification_ws import ws_manager

# 1. 发送用户通知
await ws_manager.send_to_user_id(
    user_id=user.id,
    message={
        "type": "task_approved",
        "content": "您的任务已通过审核",
        "task_id": task.id,
        "priority": "normal"
    }
)

# 2. 角色广播
await ws_manager.broadcast_to_role(
    role="admin",
    message={
        "type": "task_submitted",
        "content": f"标注员提交了任务：{task.title}",
        "pending": pending_count,
        "priority": "high"
    }
)

# 3. 全局广播
await ws_manager.broadcast_to_all(
    message={
        "type": "work_end_reminder",
        "title": "下班提醒",
        "content": "请及时保存文件，填写工作日志，关闭电脑",
        "priority": "normal"
    }
)
```

**离线通知自动保存**：

- `ws_manager.send_to_user_id()` 会自动保存到 Redis
- 如果用户离线，消息会存储在 Redis List 中
- 用户下次登录时自动恢复

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

## 部署

### 生产环境配置

1. 修改 `.env` 文件中的配置
2. 设置强密码和安全的SECRET_KEY
3. 配置HTTPS
4. 设置数据库连接池
5. 配置日志记录

### Docker部署

```bash
# 构建镜像
docker build -t medical-annotation-backend .

# 运行容器
docker run -d -p 8000:8000 medical-annotation-backend
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
