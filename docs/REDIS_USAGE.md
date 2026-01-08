# Redis 使用说明

## 📋 目录

- [Token 管理（主要功能）](#token-管理主要功能)
- [实时协作功能](#实时协作功能)
- [技术架构](#技术架构)
- [优雅降级机制](#优雅降级机制)

---

## 🔐 Token 管理（主要功能）

Redis 在系统中的**核心作用**是实现基于白名单的 Token 管理机制，提供更高的安全性和控制能力。

### 1️⃣ Token 白名单机制

#### 工作原理

```
用户登录
  ↓
生成 JWT Token
  ↓
Token 存储到 Redis（白名单）
  ├─ Key: token:<token_hash>
  ├─ Value: {user_id, username, role, created_at, last_active, expire_at}
  └─ TTL: 30 分钟
  ↓
每次 API 请求
  ├─ 验证 JWT 签名（基础安全）
  └─ 检查 Redis 白名单（额外安全层）
```

#### 数据结构

```python
# Token 存储
Key:   token:<SHA256(token)[:16]>
Value: {
    "user_id": "uuid",
    "username": "张三",
    "role": "annotator",
    "created_at": "2025-10-16T10:00:00",
    "last_active": "2025-10-16T10:15:00",
    "expire_at": "2025-10-16T10:30:00"
}
TTL:   1800 秒（30 分钟）

# 用户 -> Token 映射（用于单点登录）
Key:   user_token:<user_id>
Value: <token_hash>
TTL:   1800 秒
```

### 2️⃣ 关闭浏览器自动登出 ✅

#### 实现机制

1. **前端**：Token 存储在 `sessionStorage`（关闭浏览器即清除）
2. **后端**：Token 在 Redis 中设置 30 分钟 TTL

```typescript
// 前端（src/utils/auth.ts）
export const setToken = (token: string) => {
  sessionStorage.setItem(TOKEN_KEY, token) // 关闭浏览器自动清除
}
```

```python
# 后端（backend/app/utils/token_manager.py）
redis_client.set(token_key, token_data, expire=1800)  # 30 分钟过期
```

#### 效果

- ✅ 关闭浏览器 → Token 自动清除 → 重新打开需要登录
- ✅ 即使有人拿到了 Token，30 分钟后也会自动失效
- ✅ 双重保障：前端 + 后端

### 3️⃣ Token 自动续期（滑动窗口） 🔄

#### 工作原理

```python
# 每次 API 请求时检查
if token_ttl < 5 分钟:
    # 自动续期到 30 分钟
    redis_client.set(token_key, token_data, expire=1800)
    logger.info("Token 已续期")
```

#### 效果

- ✅ 持续使用系统不会掉线
- ✅ 30 分钟内没有任何操作才会过期
- ✅ 活跃用户体验更好

### 4️⃣ 强制登出功能 ⛔

#### 使用场景

- 管理员强制用户下线
- 检测到异常登录行为
- 用户权限变更后立即生效

#### 实现方式

```python
# 撤销指定用户的所有 Token
TokenManager.revoke_user_tokens(user_id)
  ↓
从 Redis 删除该用户的 Token
  ↓
该用户的所有请求立即被拒绝
  ↓
必须重新登录
```

#### API 端点

```python
# 登出（撤销自己的 Token）
POST /auth/logout

# 强制登出（管理员撤销他人的 Token）
POST /admin/force-logout
  Body: {"user_id": "target_user_id"}
```

### 5️⃣ 单点登录控制 🔐

#### 实现机制

```python
# 每个用户只能有一个有效 Token
user_token:<user_id> → <latest_token_hash>

# 新登录时
1. 生成新 Token
2. 撤销旧 Token（如果存在）
3. 存储新 Token
4. 更新 user_token 映射
```

#### 效果

- ✅ 同一账号在其他地方登录，之前的登录会自动失效
- ✅ 防止账号共享
- ✅ 提高账号安全性

---

## 👥 实时协作功能

Redis 的第二个作用是支持**实时协作文档**的在线状态跟踪。

### 1️⃣ 用户在线状态

#### 数据结构

```python
# 全局在线标记
Key:   presence:user:<user_id>
Value: <timestamp>
TTL:   60 秒

# 每 30 秒心跳更新
r.set(f"presence:user:{user_id}", now, ex=60)
```

#### 作用

- 显示用户是否在线
- 超过 60 秒未更新自动标记为离线

### 2️⃣ 文档协作状态

#### 数据结构

```python
# 文档在线用户列表
Key:   presence:doc:<document_id>
Value: Hash {
    <user_id>: <timestamp>
}
TTL:   文档级别控制

# 示例
presence:doc:doc123 → {
    "user456": 1697456789,
    "user789": 1697456790
}
```

#### 作用

- 显示谁正在编辑某个文档
- 防止编辑冲突
- 实时协作提示

---

## 🏗️ 技术架构

### Redis 连接配置

```python
# backend/app/config.py
REDIS_URL: str = "redis://localhost:6379"

# 连接参数
redis.from_url(
    REDIS_URL,
    decode_responses=True,        # 自动解码为字符串
    socket_connect_timeout=5,     # 连接超时 5 秒
    socket_timeout=5,             # 操作超时 5 秒
    retry_on_timeout=True,        # 超时自动重试
    health_check_interval=30      # 每 30 秒健康检查
)
```

### RedisClient 单例模式

```python
class RedisClient:
    _instance = None    # 单例实例
    _connected = False  # 连接状态

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            # 初始化连接
            cls._instance = redis.from_url(...)
            cls._instance.ping()
            cls._connected = True
        return cls._instance

    @classmethod
    def is_connected(cls):
        # 检查连接状态
        return cls._connected and cls._instance is not None
```

### 启动时自动初始化

```python
# backend/app/main.py
@app.on_event("startup")
async def startup_event():
    logger.info("正在初始化 Redis 连接...")
    redis_status = redis_ping()
    if redis_status:
        logger.info("Redis 连接成功！Token 管理功能已启用")
    else:
        logger.warning("Redis 连接失败，系统将以降级模式运行")
```

---

## 🛡️ 优雅降级机制

### 降级策略

如果 Redis 不可用，系统会**自动降级**到纯 JWT 模式：

```python
if not redis_client.is_connected():
    logger.warning("Redis 未连接，跳过 token 存储")
    return False  # 但不影响 JWT 验证
```

### 功能对比

| 功能           | Redis 可用 | Redis 不可用（降级模式） |
| -------------- | ---------- | ------------------------ |
| JWT 签名验证   | ✅         | ✅                       |
| Token 白名单   | ✅         | ❌                       |
| Token 自动续期 | ✅         | ❌                       |
| 强制登出       | ✅         | ❌                       |
| 单点登录控制   | ✅         | ❌                       |
| 关闭浏览器登出 | ✅（双重） | ✅（仅前端）             |
| 实时协作状态   | ✅         | ❌                       |

### 降级模式下的行为

```python
# Token 验证逻辑
def get_current_user(token: str):
    # 1. 验证 JWT 签名（必须）
    payload = jwt.decode(token, SECRET_KEY)

    # 2. 检查 Redis 白名单（可选）
    if redis_client.is_connected():
        token_data = TokenManager.verify_token(token)
        if not token_data:
            raise HTTPException(401, "Token 已失效")
    else:
        logger.warning("Redis 未连接，降级为纯 JWT 模式")

    return payload
```

---

## 📊 Redis 数据概览

### 当前使用的 Key 前缀

| 前缀             | 用途            | TTL   | 示例                      |
| ---------------- | --------------- | ----- | ------------------------- |
| `token:`         | Token 白名单    | 1800s | `token:a1b2c3d4e5f6g7h8`  |
| `user_token:`    | 用户 Token 映射 | 1800s | `user_token:uuid-1234`    |
| `presence:user:` | 用户在线状态    | 60s   | `presence:user:uuid-1234` |
| `presence:doc:`  | 文档协作状态    | 动态  | `presence:doc:doc-5678`   |

### 内存使用估算

假设 1000 个在线用户：

```
Token 白名单:
  1000 个 token × 约 500 字节 = 500 KB

用户 Token 映射:
  1000 个映射 × 约 100 字节 = 100 KB

用户在线状态:
  1000 个用户 × 约 50 字节 = 50 KB

文档协作状态:
  100 个文档 × 平均 10 人 × 约 80 字节 = 80 KB

总计: 约 730 KB
```

**结论**：即使 10000 个在线用户，Redis 内存占用也不会超过 10 MB，非常轻量。

---

## 🔍 监控和调试

### 查看 Redis 中的 Token

```bash
# 连接到 Redis
docker exec -it pm-redis redis-cli

# 查看所有 token key
KEYS token:*

# 查看特定 token
GET token:a1b2c3d4e5f6g7h8

# 查看 TTL
TTL token:a1b2c3d4e5f6g7h8

# 查看用户映射
GET user_token:uuid-1234

# 查看在线用户
KEYS presence:user:*
```

### 诊断脚本

```bash
# 运行 Redis 连接诊断
python backend/diagnose_redis.py
```

### 日志关键字

```bash
# 查看 Redis 相关日志
grep "Redis" backend.log
grep "TokenManager" backend.log

# 关键日志示例
✅ [Redis] Redis 连接成功
✅ [TokenManager] Token 已存储 - User: 张三
🔄 [TokenManager] Token 已续期 - User: 张三
✅ [TokenManager] Token 已撤销 - User: 张三
⚠️ [TokenManager] Redis 未连接，跳过 token 存储
```

---

## 🎯 总结

### Redis 的核心价值

1. **🔐 安全性提升**

   - Token 白名单机制，服务端可控
   - 支持强制登出，立即生效
   - 防止 Token 泄露后长期滥用

2. **✨ 用户体验优化**

   - 关闭浏览器自动登出
   - 活跃用户自动续期，不会掉线
   - 单点登录，防止账号共享

3. **👥 实时协作支持**

   - 用户在线状态跟踪
   - 文档协作冲突检测
   - 实时协作提示

4. **🛡️ 系统健壮性**
   - 优雅降级，Redis 故障不影响系统运行
   - 自动重连机制
   - 详细日志，便于排查问题

### 未来扩展可能

Redis 还可以用于：

- 📊 **API 限流**：防止恶意请求
- 🔔 **消息队列**：异步任务处理
- 💾 **缓存热点数据**：提升性能
- 📈 **实时统计**：用户行为分析
- 🔒 **分布式锁**：并发控制

---

## 📚 相关文件

- `backend/app/utils/redis_client.py` - Redis 客户端封装
- `backend/app/utils/token_manager.py` - Token 管理服务
- `backend/app/utils/security.py` - 安全认证（集成 Token 验证）
- `backend/app/api/auth.py` - 登录/登出 API
- `backend/app/api/collaboration.py` - 协作功能 API
- `backend/app/main.py` - 应用启动（Redis 初始化）
- `backend/app/config.py` - Redis 配置
- `src/utils/auth.ts` - 前端 Token 管理（sessionStorage）

---

**最后更新**: 2025-10-16 **维护者**: AI Assistant
