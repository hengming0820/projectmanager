# Docker 环境 Redis 连接问题修复指南

## 🔍 问题描述

在 Windows 本地环境中使用 Python 直接运行后端时，Redis 连接正常：

```
✅ Redis 连接成功 (redis://localhost:6379)
```

但在 Docker/WSL 环境中启动后端时，报错：

```
❌ Error 111 connecting to localhost:6379. Connection refused.
```

## 📋 问题根因

### 原因 1：Docker 网络隔离

在 Docker 容器中，**`localhost` 指的是容器本身**，而不是宿主机或其他容器。

```
┌─────────────────────────────────────────┐
│  宿主机 (Windows/Linux)                  │
│  ├─ Redis 运行在 localhost:6379         │ ← Windows 本地可以访问
│  │                                       │
│  ├─ Docker 容器 1 (pm-backend)          │
│  │  └─ localhost → 容器自己 (❌ 无Redis) │ ← 容器内 localhost 不是宿主机
│  │                                       │
│  └─ Docker 容器 2 (pm-redis)            │
│     └─ Redis 运行在 6379 端口           │ ← 正确的 Redis 位置
└─────────────────────────────────────────┘
```

### 原因 2：配置优先级问题

后端配置文件 `backend/app/config.py` 的默认值可能未被 Docker Compose 的环境变量正确覆盖。

## ✅ 解决方案

### 1. 修改后端配置文件（已修复）

**文件**: `backend/app/config.py`

**修改前**:

```python
class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379"  # ❌ 硬编码默认值
```

**修改后**:

```python
class Settings(BaseSettings):
    # Docker环境：redis://redis:6379
    # 本地开发：redis://localhost:6379
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")  # ✅ 优先读取环境变量
```

**关键改进**:

- ✅ 使用 `os.getenv()` 确保环境变量优先级最高
- ✅ 添加注释说明不同环境的配置
- ✅ 保留本地开发的默认值

### 2. Docker Compose 配置（已确认正确）

**文件**: `deploy-htttps/docker-compose-prod.yml`

```yaml
services:
  redis:
    image: deploy-https-redis:v1.0
    container_name: pm-redis
    networks:
      - pm-network # ✅ 在同一网络中

  backend:
    image: deploy-https-backend:v1.0
    container_name: pm-backend
    environment:
      DEBUG: 'true' # ✅ 启用调试日志
      REDIS_URL: redis://redis:6379 # ✅ 使用服务名 'redis' 而不是 'localhost'
    networks:
      - pm-network # ✅ 在同一网络中
    depends_on:
      - redis

networks:
  pm-network:
    driver: bridge
```

**关键配置**:

- ✅ Redis 服务名: `redis`（定义在第 21 行）
- ✅ Redis URL: `redis://redis:6379`（使用服务名，不是 `localhost`）
- ✅ 网络配置: 所有服务在同一 `pm-network` 中
- ✅ 依赖关系: `depends_on: - redis` 确保 Redis 先启动

## 🚀 部署步骤

### 步骤 1: 重新构建后端镜像

由于修改了 `config.py`，需要重新构建 Docker 镜像：

```bash
# 进入项目根目录
cd ~/xxjz_projectmanager

# 重新构建后端镜像
docker build -t deploy-https-backend:v1.0 -f backend/Dockerfile .

# 或使用提供的脚本（如果有）
cd deploy-https
./rebuild-backend.sh
```

### 步骤 2: 重启服务

```bash
cd ~/xxjz_projectmanager/deploy-https

# 停止所有服务
docker compose down

# 启动所有服务
docker compose up -d

# 查看后端日志，确认配置
docker logs -f pm-backend
```

### 步骤 3: 验证配置

启动后，查看日志应该看到：

```
✅ 正确的日志:
🔧 Redis URL: redis://redis:6379
✅ Redis 连接成功
✅ Redis通知服务初始化成功

❌ 错误的日志:
⚠️ Redis不可用，缓存服务已禁用: Error 111 connecting to localhost:6379
```

## 🔧 故障排查

### 检查点 1: 容器网络连通性

```bash
# 进入后端容器
docker exec -it pm-backend bash

# 测试 Redis 连接（使用服务名）
ping redis
# 应该能 ping 通

# 测试 Redis 端口
nc -zv redis 6379
# 或
telnet redis 6379
```

### 检查点 2: 环境变量是否生效

```bash
# 查看容器的环境变量
docker exec pm-backend env | grep REDIS
# 应该输出: REDIS_URL=redis://redis:6379
```

### 检查点 3: Redis 容器是否正常运行

```bash
# 检查 Redis 容器状态
docker ps | grep redis
# 应该显示 pm-redis 容器在运行

# 查看 Redis 日志
docker logs pm-redis
# 应该没有错误信息

# 直接连接 Redis（从宿主机）
redis-cli -h localhost -p 6379 ping
# 应该返回 PONG
```

### 检查点 4: Docker 网络配置

```bash
# 查看网络
docker network ls
# 应该有 pm-network

# 查看网络详情
docker network inspect pm-network
# 应该看到 pm-backend 和 pm-redis 都在这个网络中
```

## 📚 最佳实践

### 1. 环境变量配置优先级

```
高优先级 ←──────────────────────→ 低优先级
Docker Compose环境变量 > .env文件 > 代码默认值
```

**推荐做法**:

```python
# ✅ 推荐：使用 os.getenv() 明确优先级
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

# ❌ 不推荐：硬编码可能被 Pydantic 优先使用
REDIS_URL: str = "redis://localhost:6379"
```

### 2. Docker 服务命名规范

在 Docker Compose 中：

- ✅ 使用服务名: `redis://redis:6379`
- ✅ 使用容器名: `redis://pm-redis:6379`（需要在同一网络）
- ❌ 使用 localhost: `redis://localhost:6379`（容器内无效）

### 3. 配置文档化

在配置文件中添加注释：

```python
# Redis配置
# Docker环境：redis://redis:6379
# 本地开发：redis://localhost:6379
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
```

### 4. 调试模式

在 Docker Compose 中启用调试：

```yaml
environment:
  DEBUG: 'true' # 打印配置信息
```

## 🎯 验证清单

部署后验证以下内容：

- [ ] 后端容器启动成功（`docker ps` 显示 `pm-backend` 运行中）
- [ ] Redis 容器启动成功（`docker ps` 显示 `pm-redis` 运行中）
- [ ] 后端日志显示 `Redis URL: redis://redis:6379`
- [ ] 后端日志显示 `✅ Redis 连接成功`
- [ ] 后端日志显示 `✅ Redis通知服务初始化成功`
- [ ] 前端可以正常登录
- [ ] 实时通知功能正常工作
- [ ] Token 管理正常（登录后刷新页面不需要重新登录）

## 📝 相关文件

- `backend/app/config.py` - 后端配置文件（已修复）
- `deploy-htttps/docker-compose-prod.yml` - Docker Compose 生产配置（已确认）
- `backend/Dockerfile` - 后端 Docker 镜像构建文件

## 🔗 相关文档

- [Docker Network Documentation](https://docs.docker.com/network/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Redis Connection String Format](https://redis.io/docs/getting-started/connection-strings/)

---

**版本**: v1.0  
**日期**: 2025-11-03  
**状态**: ✅ 已修复
