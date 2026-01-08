# Token 失效问题诊断报告

## 🔍 问题调查

### 用户反馈

> "为什么我没操作几分钟之后就叫我重新登陆"

### 📊 诊断结果

经过全面测试和代码审查，发现了以下情况：

## ✅ 后端Token机制 - **正常**

### 测试结果

```
✅ Redis 连接成功
✅ Token 可以正常存储到 Redis
✅ Token 可以正常验证
✅ Redis 中已有真实 Token（user1的Token，TTL: 35860秒 ≈ 9.96小时）
✅ Token 过期时间: 600分钟（10小时）
✅ Token 自动续期: 剩余 < 5分钟时自动续期
```

**测试脚本**: `backend/test_token_storage.py`

**测试命令**:

```bash
docker exec pm-backend2 python test_token_storage.py
```

## ⚠️ 前端Token存储 - **发现不一致**

### 问题1: Token存储位置不一致

#### 前端Store (正确)

**文件**: `src/store/modules/user.ts`

```typescript
const setToken = (newToken: string, refreshToken?: string) => {
  token.value = newToken
  localStorage.setItem('token', newToken) // ✅ 存储在 localStorage
  // ...
}
```

#### 后端API错误处理 (不一致)

**文件**: `src/utils/http/backendApi.ts`

```typescript
if (status === 401) {
  // 清除所有认证相关的存储（sessionStorage）❌
  sessionStorage.removeItem('token') // ❌ 清除 sessionStorage
  sessionStorage.removeItem('refreshToken')
  sessionStorage.removeItem('userId')

  // 问题：Token实际存储在 localStorage，但这里清除的是 sessionStorage
}
```

**影响**:

- Token存储在 `localStorage`
- 401错误时清除的是 `sessionStorage`
- 可能导致Token未被正确清除，或者清除了错误的位置

### 问题2: 多个HTTP客户端

项目中有两个HTTP客户端：

1. **`src/utils/http/index.ts`** - 主HTTP客户端

   - 401错误时调用 `logOut()`
   - `logOut()` 会清除 userStore 中的所有数据

2. **`src/utils/http/backendApi.ts`** - 后端API专用
   - 401错误时直接操作 `sessionStorage`（不一致）
   - 不调用 `logOut()`

## 🛠️ 解决方案

### 方案1: 统一Token存储清除逻辑 ⭐ **推荐**

修改 `src/utils/http/backendApi.ts`，使其调用 userStore 的 `logOut()` 方法：

```typescript
if (status === 401) {
  console.warn('⚠️ [BackendAPI] 未认证，清除token并跳转登录页')

  // 使用 userStore 的 logOut 方法，确保清除所有存储
  import { useUserStore } from '@/store/modules/user'
  const userStore = useUserStore()
  userStore.logOut() // ✅ 统一清除 localStorage

  setTimeout(() => {
    if (!window.location.href.includes('/login')) {
      window.location.href = '/login'
    }
  }, 100)
}
```

### 方案2: 修改清除目标为 localStorage

```typescript
if (status === 401) {
  console.warn('⚠️ [BackendAPI] 未认证，清除token并跳转登录页')

  // 清除 localStorage 而不是 sessionStorage
  localStorage.removeItem('token') // ✅ 修改为 localStorage
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('userId')

  // ...
}
```

## 🎯 推荐实施步骤

1. **立即修复**: 修改 `src/utils/http/backendApi.ts` 中的Token清除逻辑
2. **统一管理**: 所有401错误处理都调用 `userStore.logOut()`
3. **测试验证**:
   - 测试正常登录
   - 测试Token过期后的自动登出
   - 测试"记住密码"功能是否正常

## 📝 其他发现

### Token自动续期机制正常

每次API请求都会触发Token续期检查：

**文件**: `backend/app/utils/security.py`

```python
def get_current_user(...):
    # ...
    # 第三步：自动续期 Token（滑动窗口）
    renewed = token_manager.renew_token(token)
    if renewed:
        logger.info(f"🔄 [Security] Token 已自动续期")
```

### 理论上Token不会过期

只要用户持续操作（每次API请求），Token就会自动续期：

- 剩余时间 < 5分钟时 → 自动续期到10小时
- 持续操作的用户 → Token永不过期

## 🔍 如何确认问题

### 方法1: 浏览器控制台检查

登录后，在浏览器控制台执行：

```javascript
// 检查Token存储位置
console.log('localStorage Token:', localStorage.getItem('token'))
console.log('sessionStorage Token:', sessionStorage.getItem('token'))

// 监控Token变化
setInterval(() => {
  console.log('Token exists:', {
    localStorage: !!localStorage.getItem('token'),
    sessionStorage: !!sessionStorage.getItem('token')
  })
}, 5000)
```

### 方法2: 检查401错误

打开浏览器开发者工具 → Network，查看是否有401响应：

- 如果有401 → Token验证失败
- 查看Request Headers中的Authorization字段

### 方法3: 检查后端日志

```bash
docker logs -f pm-backend2 | Select-String -Pattern "(Token|401|Unauthorized)"
```

## 🎯 预期效果

修复后的行为：

1. 用户登录 → Token存储到 `localStorage` (10小时有效)
2. 用户操作 → Token自动续期（剩余<5分钟时）
3. Token过期 → 后端返回401 → 前端清除 `localStorage` → 跳转登录页
4. 关闭浏览器 → Token仍在 `localStorage` → 重新打开自动登录

## 📊 测试清单

- [ ] 修改 `src/utils/http/backendApi.ts` 的401错误处理
- [ ] 测试正常登录
- [ ] 测试长时间操作（验证自动续期）
- [ ] 测试关闭浏览器后重新打开（验证Token持久化）
- [ ] 测试Token真正过期后的登出（10小时无操作）
- [ ] 测试"记住密码"功能
- [ ] 验证Redis中的Token数据

---

**生成时间**: 2025-11-05  
**测试环境**: Docker生产环境  
**Redis状态**: ✅ 正常  
**Token机制**: ✅ 正常  
**前端存储**: ⚠️ 发现不一致
