# 🚑 Redis 连接问题快速修复

## 问题症状

```bash
❌ WARNING: Redis不可用，缓存服务已禁用: Error 111 connecting to localhost:6379
❌ Connection refused
```

## 快速修复（3 步搞定）

### 方法 1: 使用自动化脚本 ⚡

**Linux/WSL**:

```bash
cd ~/xxjz_projectmanager/deploy-https
chmod +x fix-redis-connection.sh
./fix-redis-connection.sh
```

**Windows**:

```cmd
cd C:\path\to\xxjz_projectmanager\deploy-https
fix-redis-connection.bat
```

### 方法 2: 手动修复 🛠️

```bash
# 1. 进入部署目录
cd ~/xxjz_projectmanager/deploy-https

# 2. 停止服务
docker compose -f docker-compose-prod.yml down

# 3. 重新构建后端镜像（在项目根目录）
cd ~/xxjz_projectmanager
docker build -t deploy-https-backend:v1.0 -f backend/Dockerfile .

# 4. 启动服务
cd ~/xxjz_projectmanager/deploy-https
docker compose -f docker-compose-prod.yml up -d

# 5. 查看日志验证
docker logs -f pm-backend
```

## 验证修复

### ✅ 成功标志

日志应该显示：

```
🔧 Redis URL: redis://redis:6379
✅ Redis 连接成功
✅ Redis通知服务初始化成功
```

### 快速测试

```bash
# 测试 1: 检查容器网络
docker exec pm-backend ping -c 2 redis

# 测试 2: 检查 Redis 连接
docker exec pm-backend python -c "import redis; r=redis.from_url('redis://redis:6379'); print('PONG' if r.ping() else 'FAIL')"

# 测试 3: 检查环境变量
docker exec pm-backend env | grep REDIS_URL
```

期望输出：

```
✅ redis is alive (ping 测试)
✅ PONG (Redis 连接测试)
✅ REDIS_URL=redis://redis:6379 (环境变量)
```

## 为什么会出现这个问题？

**核心原因**: 在 Docker 容器中，`localhost` 指向容器本身，而不是其他容器。

```
❌ 错误配置: redis://localhost:6379  → 容器找不到 Redis
✅ 正确配置: redis://redis:6379      → 通过服务名找到 Redis 容器
```

## 相关修改

### 已修复的文件：

1. ✅ `backend/app/config.py` - 环境变量优先级修复
2. ✅ `deploy-htttps/docker-compose-prod.yml` - 添加调试日志

### 关键代码：

```python
# backend/app/config.py
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
```

```yaml
# deploy-htttps/docker-compose-prod.yml
environment:
  REDIS_URL: redis://redis:6379 # 使用服务名，不是 localhost
```

## 仍有问题？

查看详细文档：

```bash
cat DOCKER_REDIS_CONNECTION_FIX.md
```

或检查网络连通性：

```bash
# 查看所有容器
docker ps

# 查看网络
docker network inspect pm-network

# 进入后端容器调试
docker exec -it pm-backend bash
```

## 联系支持

如果以上方法都无法解决，请提供以下信息：

1. `docker ps` 的完整输出
2. `docker logs pm-backend` 的完整日志
3. `docker logs pm-redis` 的完整日志
4. 你的操作系统信息（Windows/Linux/WSL）

---

**最后更新**: 2025-11-03  
**版本**: v1.0
