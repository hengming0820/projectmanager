# 🔑 Token 存储迁移说明

## 📋 问题描述

### 原问题

用户在工作周中插入文章链接后，在新标签页中打开时，会自动跳转到登录页面。

### 根本原因

Token 存储方式使用了 **sessionStorage**，而 sessionStorage 有以下特点：

| 特性     | sessionStorage   | localStorage               |
| -------- | ---------------- | -------------------------- |
| 作用域   | 仅当前标签页     | 所有标签页共享             |
| 生命周期 | 关闭标签页即清除 | 持久化存储（除非手动清除） |
| 多标签页 | ❌ 不共享        | ✅ 共享                    |
| 安全性   | 较高（自动过期） | 中等（需配合后端）         |

**问题场景**：

1. 用户在标签页 A 登录，token 存储在标签页 A 的 sessionStorage
2. 用户点击工作周中的文章链接，在新标签页 B 打开
3. 标签页 B 没有 sessionStorage 中的 token
4. 路由守卫检测到未登录，跳转到登录页

---

## ✅ 解决方案

### 变更内容

将 Token 存储从 **sessionStorage** 迁移到 **localStorage**。

### 修改的文件

**`src/store/modules/user.ts`**

#### 1. 初始化 Token 读取

```typescript
// 修改前
const savedToken = sessionStorage.getItem('token')

// 修改后（向后兼容）
const savedToken = localStorage.getItem('token') || sessionStorage.getItem('token')
if (savedToken) {
  // 如果是从 sessionStorage 迁移，同步到 localStorage
  if (!localStorage.getItem('token') && sessionStorage.getItem('token')) {
    localStorage.setItem('token', savedToken)
    sessionStorage.removeItem('token')
  }
}
```

#### 2. 设置 Token

```typescript
// 修改前
sessionStorage.setItem('token', newToken)
sessionStorage.setItem('refreshToken', refreshToken)

// 修改后
localStorage.setItem('token', newToken)
localStorage.setItem('refreshToken', refreshToken)
```

#### 3. 登出清除

```typescript
// 修改前
sessionStorage.removeItem('token')
sessionStorage.removeItem('refreshToken')
sessionStorage.removeItem('userId')

// 修改后（兼容旧版本）
localStorage.removeItem('token')
localStorage.removeItem('refreshToken')
localStorage.removeItem('userId')
sessionStorage.removeItem('token') // 清理旧数据
sessionStorage.removeItem('refreshToken')
sessionStorage.removeItem('userId')
```

---

## 🎯 优势与权衡

### ✅ 优势

1. **多标签页支持**

   - 所有标签页共享登录状态
   - 在新标签页打开链接时无需重新登录
   - 提升用户体验

2. **向后兼容**

   - 自动迁移旧的 sessionStorage 数据
   - 用户无需重新登录

3. **配合后端 Redis**
   - 后端使用 Redis Token 白名单管理
   - Token 过期后端控制，安全性有保障
   - 前端只是存储载体

### ⚠️ 权衡

1. **持久化存储**

   - localStorage 不会随标签页关闭而清除
   - 但后端 Token 有过期时间（30分钟默认）
   - Redis 白名单机制确保安全性

2. **安全考虑**
   - localStorage 可被同源脚本访问
   - 但项目已有 CORS、CSP 等安全措施
   - Token 有效期短（30分钟）且自动续期

---

## 🔒 安全机制

### 多层安全保障

```
┌─────────────────────────────────────────┐
│     前端 localStorage 存储 Token        │
│  （只是存储，Token 本身是 JWT 签名）    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      后端 Redis Token 白名单            │
│  - Token 必须在白名单中才有效           │
│  - 30分钟过期（可配置）                 │
│  - 自动续期机制                         │
│  - 登出立即失效                         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       JWT Token 签名验证                │
│  - 密钥签名，防篡改                     │
│  - 包含用户信息和过期时间               │
└─────────────────────────────────────────┘
```

### Token 生命周期

1. **登录**

   - 后端生成 JWT Token
   - 加入 Redis 白名单（TTL 30分钟）
   - 前端存储到 localStorage

2. **使用**

   - 每次 API 请求携带 Token
   - 后端验证白名单 + JWT 签名
   - 剩余时间 < 5分钟自动续期

3. **过期/登出**
   - 登出：立即从 Redis 移除
   - 过期：Redis TTL 自动清除
   - 前端清除 localStorage

---

## 🧪 测试场景

### 场景 1：新标签页打开链接

**测试步骤**：

1. 登录系统
2. 进入工作周页面
3. 点击工作周中的文章链接（新标签页打开）
4. 验证是否直接显示文章内容

**预期结果**：

- ✅ 直接显示文章内容（无需登录）

### 场景 2：多标签页同步

**测试步骤**：

1. 在标签页 A 登录
2. 打开新标签页 B
3. 在标签页 B 访问任意需要登录的页面
4. 验证是否已登录

**预期结果**：

- ✅ 标签页 B 已登录（无需重新登录）

### 场景 3：登出同步

**测试步骤**：

1. 打开两个标签页 A 和 B，都已登录
2. 在标签页 A 点击登出
3. 在标签页 B 刷新页面
4. 验证标签页 B 的登录状态

**预期结果**：

- ✅ 标签页 B 需要重新登录

### 场景 4：Token 过期

**测试步骤**：

1. 登录后等待 30 分钟（或修改后端 Token 过期时间为 1 分钟测试）
2. 在任意标签页发起 API 请求
3. 观察是否自动跳转到登录页

**预期结果**：

- ✅ Token 过期后自动跳转到登录页

### 场景 5：浏览器关闭重启

**测试步骤**：

1. 登录系统
2. 完全关闭浏览器
3. 重新打开浏览器，访问系统
4. 验证登录状态

**预期结果**：

- ⚠️ localStorage 仍存在，但 Token 可能已过期（取决于关闭浏览器的时长）
- ✅ 如果 Token 未过期（30分钟内），仍可自动登录
- ✅ 如果 Token 已过期，自动跳转到登录页

---

## 📝 配置说明

### 后端配置

**`backend/app/config.py`**

```python
# JWT 配置
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token 过期时间（分钟）
TOKEN_RENEW_THRESHOLD_MINUTES: int = 5  # 自动续期阈值（分钟）
```

**说明**：

- `ACCESS_TOKEN_EXPIRE_MINUTES`：Token 有效期，默认 30 分钟
- `TOKEN_RENEW_THRESHOLD_MINUTES`：剩余时间少于此值时自动续期

### 前端配置

**无需额外配置**，Token 存储逻辑已在 `src/store/modules/user.ts` 中实现。

---

## 🔄 迁移指南

### 对于现有用户

**无需任何操作**！

- 系统会自动检测旧的 sessionStorage
- 自动迁移到 localStorage
- 用户体验无感知

### 对于开发者

1. **拉取最新代码**

   ```bash
   git pull origin main
   ```

2. **重新构建前端**

   ```bash
   npm run build
   ```

3. **重启服务**
   ```bash
   cd deploy-local
   docker-compose down
   docker-compose up -d
   ```

---

## 🐛 故障排查

### 问题 1：新标签页仍然需要登录

**可能原因**：

1. 浏览器禁用了 localStorage
2. 隐私模式/无痕模式
3. 前端代码未更新

**解决方法**：

```bash
# 1. 清除浏览器缓存
Ctrl + Shift + Delete

# 2. 检查浏览器设置
浏览器设置 → 隐私和安全 → Cookie 和网站数据 → 允许

# 3. 强制刷新
Ctrl + Shift + R (或 Cmd + Shift + R)
```

### 问题 2：Token 无法自动续期

**检查**：

```bash
# 查看后端日志
docker logs pm-backend | grep "Token"

# 查看 Redis 连接
docker exec -it pm-redis redis-cli ping
```

### 问题 3：登出后仍然保持登录

**可能原因**：

- 多标签页缓存问题

**解决方法**：

```javascript
// 在浏览器控制台手动清除
localStorage.clear()
sessionStorage.clear()
// 然后刷新页面
```

---

## 📚 相关文档

- **REDIS_USAGE.md** - Redis Token 管理详细说明
- **TOKEN_EXPIRATION_GUIDE.md** - Token 过期和续期机制
- **docs/USER_API_PERMISSION_FIX.md** - 用户权限系统

---

## 🎉 总结

### 主要变更

- ✅ Token 存储从 sessionStorage 迁移到 localStorage
- ✅ 支持多标签页共享登录状态
- ✅ 向后兼容，自动迁移旧数据
- ✅ 安全性由后端 Redis 白名单保障

### 用户体验提升

- ✅ 新标签页打开链接无需重新登录
- ✅ 多标签页操作更流畅
- ✅ 减少重复登录次数

### 安全性保障

- ✅ 后端 Redis Token 白名单
- ✅ JWT 签名验证
- ✅ 30 分钟自动过期
- ✅ 登出立即失效

---

**版本**: 1.0.0  
**发布日期**: 2025-10-17  
**影响范围**: 所有用户  
**风险等级**: 低（向后兼容）
