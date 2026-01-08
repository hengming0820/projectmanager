# Token 失效机制说明文档

## 📋 概述

本项目使用 **JWT + Redis 白名单** 的双重认证机制，实现了安全的用户会话管理和自动续期功能。

## ⏱️ Token 过期时间配置

### 1. 后端配置文件

**位置**: `backend/app/config.py`

```python
# JWT配置
SECRET_KEY: str = "your-secret-key-here"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 600  # ✅ Token过期时间：600分钟（10小时）
# Token 自动续期阈值（分钟）- 剩余时间少于此值时触发续期
TOKEN_RENEW_THRESHOLD_MINUTES: int = 5  # ✅ 自动续期阈值：5分钟
```

**关键参数说明**：

- `ACCESS_TOKEN_EXPIRE_MINUTES = 600`：Token 有效期为 **10小时**
- `TOKEN_RENEW_THRESHOLD_MINUTES = 5`：剩余时间少于 **5分钟** 时自动续期

## 🔄 Token 自动续期机制（滑动窗口）

### 2. 后端 Token 管理器

**位置**: `backend/app/utils/token_manager.py`

```python
class TokenManager:
    # Token 默认过期时间（秒）
    TOKEN_EXPIRE_SECONDS = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 36000秒
    # Token 自动续期阈值（秒）
    TOKEN_RENEW_THRESHOLD = settings.TOKEN_RENEW_THRESHOLD_MINUTES * 60  # 300秒

    @classmethod
    def renew_token(cls, token: str) -> bool:
        """
        续期 token（滑动窗口机制）
        - 检查剩余时间
        - 如果剩余时间 < 5分钟，自动续期到10小时
        - 更新 last_active 时间
        """
```

### 3. Token 验证与续期触发点

**位置**: `backend/app/utils/security.py`

```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前用户（支持 Redis Token 白名单和自动续期）

    验证流程：
    1. 验证 JWT 签名
    2. 检查 Redis 白名单
    3. 自动续期 Token（滑动窗口）✅
    4. 从数据库查询用户
    """
    # ... 验证逻辑 ...

    # 第三步：自动续期 Token（滑动窗口）
    renewed = token_manager.renew_token(token)
    if renewed:
        logger.info(f"🔄 [Security] Token 已自动续期")
```

**重要**：每次发起API请求时，后端都会自动检查Token剩余时间，如果少于5分钟则自动续期到10小时。

## 📦 Token 存储机制

### 4. 前端存储

**位置**: `src/store/modules/user.ts`

```typescript
// 设置Token
const setToken = (newToken: string, refreshToken?: string) => {
  token.value = newToken
  // 使用 localStorage 支持多标签页共享 ✅
  localStorage.setItem('token', newToken)
  if (refreshToken) {
    localStorage.setItem('refreshToken', refreshToken)
  }
  isLogin.value = true
}
```

**存储位置**: `localStorage`（支持多标签页共享）

### 5. 后端存储

**位置**: Redis 白名单

```python
# Token 数据结构
token_data = {
    "user_id": user_id,
    "username": username,
    "role": role,
    "created_at": now.isoformat(),
    "last_active": now.isoformat(),  # 续期时会更新
    "expire_at": (now + timedelta(seconds=expire)).isoformat()
}

# Redis Key: "token:{token_hash}"
# TTL: 36000秒（600分钟）
```

## 🚫 Token 失效原因分析

### 您遇到的"几分钟就需要重新登录"问题，可能原因如下：

#### 1. **Redis 连接问题** ⚠️

如果 Redis 未正常连接，Token 白名单验证会失败，导致频繁登出。

**检查方法**：

```bash
# 查看后端日志
docker logs -f pm-backend | grep -i redis

# 预期输出（正常）：
# ✅ [Redis] 连接成功: redis://redis:6379

# 异常输出（异常）：
# ❌ [Redis] 连接失败: Connection refused
```

**解决方法**：

- 确保 Redis 服务正常运行
- 检查 `REDIS_URL` 环境变量配置
- 参考：`docs/DOCKER_REDIS_CONNECTION_FIX.md`

#### 2. **Redis 时区或时间不同步问题** ⏰

Docker 容器内外时间不同步可能导致 Token 过期时间计算错误。

**检查方法**：

```bash
# 检查主机时间
date

# 检查 Redis 容器时间
docker exec pm-redis date

# 检查后端容器时间
docker exec pm-backend date
```

**解决方法**：

```yaml
# docker-compose.yml 中添加时区设置
services:
  backend:
    environment:
      TZ: Asia/Shanghai # 设置时区
    volumes:
      - /etc/localtime:/etc/localtime:ro # 同步主机时区
```

#### 3. **多标签页冲突** 🔄

如果在多个标签页同时登录同一用户，可能触发单点登录机制。

**检查方法**：

- 尝试只在一个标签页登录
- 观察是否仍然频繁登出

**当前配置**: 项目支持多标签页共享（使用 localStorage），但后端有单点登录控制（一个用户一个有效Token）。

#### 4. **前端 Token 丢失** 💾

浏览器隐私模式或扩展插件可能清除 localStorage。

**检查方法**：

```javascript
// 在浏览器控制台执行
console.log('Token:', localStorage.getItem('token'))
```

#### 5. **后端配置被覆盖** ⚙️

Docker 环境变量可能覆盖了配置文件中的默认值。

**检查方法**：

```bash
# 查看后端容器的环境变量
docker exec pm-backend env | grep TOKEN

# 预期输出：
# ACCESS_TOKEN_EXPIRE_MINUTES=600
# TOKEN_RENEW_THRESHOLD_MINUTES=5
```

## 🔍 调试步骤

### 方法1: 查看后端日志

```bash
# 实时查看后端日志
docker logs -f pm-backend

# 关注以下关键日志：
# 🔐 [Security] 开始获取当前用户
# ✅ [TokenManager] Token 验证通过
# 🔄 [TokenManager] Token 已续期
# ❌ [TokenManager] Token 不在白名单中或已过期
```

### 方法2: 检查 Token 剩余时间

在后端添加临时调试代码：

```python
# backend/app/utils/security.py 中的 get_current_user 函数

# 在自动续期前添加：
token_info = token_manager.get_token_info(token)
if token_info:
    logger.info(f"🕐 [Security] Token TTL: {token_info.get('ttl')}秒")
```

### 方法3: 前端控制台监控

```javascript
// 在浏览器控制台执行，监控Token变化
setInterval(() => {
  const token = localStorage.getItem('token')
  console.log('Token exists:', !!token, 'Length:', token?.length)
}, 5000)
```

### 方法4: Redis 直接检查

```bash
# 连接到 Redis
docker exec -it pm-redis redis-cli

# 查看所有 Token
KEYS token:*

# 查看某个 Token 的剩余时间（TTL）
TTL token:abc123...

# 查看 Token 数据
GET token:abc123...
```

## 🛠️ 临时解决方案

### 选项1: 延长 Token 有效期

```python
# backend/app/config.py
ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 改为24小时
```

### 选项2: 调整续期阈值

```python
# backend/app/config.py
TOKEN_RENEW_THRESHOLD_MINUTES: int = 30  # 改为30分钟
```

### 选项3: 禁用单点登录（允许多设备同时登录）

修改 `backend/app/utils/token_manager.py`：

```python
@classmethod
def store_token(cls, token: str, user_id: str, username: str, role: str, expire_seconds: Optional[int] = None) -> bool:
    # ...

    # 注释掉单点登录控制
    # user_token_key = cls._get_user_token_key(user_id)
    # token_hash = cls._get_token_hash(token)
    # redis_client.set(user_token_key, token_hash, expire)
```

## 📊 理想工作流程

1. **用户登录** → Token有效期设为10小时
2. **用户操作** → 每次API请求自动检查Token剩余时间
3. **剩余时间 < 5分钟** → 自动续期到10小时（滑动窗口）
4. **用户10小时内无任何操作** → Token真正过期，需要重新登录
5. **用户持续操作** → Token永不过期（持续滑动续期）

## 🎯 推荐配置

**适用场景**: 内网办公系统

```python
# 推荐配置（平衡安全与用户体验）
ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8小时（一个工作日）
TOKEN_RENEW_THRESHOLD_MINUTES: int = 60  # 1小时
```

**说明**：

- 用户在8小时内任何操作都会触发续期（剩余<1小时时）
- 即使用户中途离开1小时内，回来后仍然有效
- 长时间离开（>8小时）则需要重新登录，符合安全要求

## 📝 相关文件

- 后端配置: `backend/app/config.py`
- Token管理: `backend/app/utils/token_manager.py`
- 安全验证: `backend/app/utils/security.py`
- 前端Store: `src/store/modules/user.ts`
- HTTP拦截器: `src/utils/http/index.ts`

## 🆘 仍然无法解决？

如果按照上述方法仍然频繁登出，请提供以下信息：

1. 后端日志（`docker logs pm-backend | tail -100`）
2. Redis 连接状态（`docker logs pm-redis | tail -50`）
3. 浏览器控制台错误信息
4. Token 剩余时间（使用上述调试方法）
5. 是否使用了多标签页
6. 是否在不同设备/浏览器登录

---

**更新日期**: 2025-11-04  
**版本**: v1.0
