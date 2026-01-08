# 通知自动标记已读功能修复

## 修复时间

2025-11-06

## 问题描述

用户报告通知功能存在以下问题：

### 1. 405 错误 (Method Not Allowed)

```
Failed to load resource: the server responded with a status of 405 (Method Not Allowed)
/api/api/notifications/17c405c2-5e20-4784-b5ae-7891d5f6bce0/read
```

### 2. URL路径重复

URL中出现两个`/api/`：`/api/api/notifications/...`

### 3. 需要手动点击标记已读

- 用户需要点击通知才能标记为已读
- 用户希望：通知一旦显示就自动标记为已读

---

## 根本原因分析

### 问题1：URL路径重复 `/api/api/...`

**原因**：

- `backendApi.ts` 配置了 `baseURL: '/api'`
- `notificationApi.ts` 中的URL包含 `/api/notifications/...`
- 最终URL = baseURL + url = `/api` + `/api/notifications/...` = `/api/api/notifications/...`

**代码位置**：

```typescript
// src/utils/http/backendApi.ts
baseURL: '/api'

// src/api/notificationApi.ts (修复前)
markAsRead: (notificationId: string) => {
  return http.put({ url: `/api/notifications/${notificationId}/read` })
}
```

### 问题2：HTTP方法不匹配

**原因**：

- **前端使用**: `http.put()` - PUT方法
- **后端定义**: `@router.post("/{notification_id}/read")` - POST方法
- HTTP方法不匹配导致405错误

**代码位置**：

```typescript
// 前端 (修复前)
markAsRead: (notificationId: string) => {
  return http.put({ url: `/api/notifications/${notificationId}/read` })
}

// 后端
@router.post("/{notification_id}/read")
def mark_as_read(notification_id: str, current_user = Depends(get_current_user)):
    """标记通知为已读（从 Redis 中删除）"""
```

### 问题3：需要手动点击

**原因**：

- 标记已读的逻辑在 `onClick` 事件中
- 用户需要点击通知才会触发标记

**代码位置**：

```typescript
// 修复前
ElNotification({
  // ...
  onClick: () => {
    // 只有点击才标记为已读
    notificationApi.markAsRead(notification.id).catch((e) => {
      console.error('标记通知已读失败:', e)
    })
  }
})
```

---

## 解决方案

### 修复1：移除URL中重复的 `/api/` 前缀

**文件**: `src/api/notificationApi.ts`

```typescript
// 修复前 ❌
export const notificationApi = {
  getNotifications: (params?: { limit?: number }) => {
    return http.get({ url: '/api/notifications/', params })
  },
  markAsRead: (notificationId: string) => {
    return http.put({ url: `/api/notifications/${notificationId}/read` })
  }
  // ...
}

// 修复后 ✅
export const notificationApi = {
  getNotifications: (params?: { limit?: number }) => {
    return http.get({ url: '/notifications/', params }) // 移除 /api/
  },
  markAsRead: (notificationId: string) => {
    return http.post({ url: `/notifications/${notificationId}/read` }) // 移除 /api/
  }
  // ...
}
```

**修改内容**：

- ✅ 所有URL移除 `/api/` 前缀
- ✅ 由 `baseURL: '/api'` 自动添加前缀
- ✅ 最终URL: `/api` + `/notifications/...` = `/api/notifications/...`

### 修复2：统一HTTP方法为POST

**文件**: `src/api/notificationApi.ts`

```typescript
// 修复前 ❌
markAsRead: (notificationId: string) => {
  return http.put({ url: `/notifications/${notificationId}/read` })
}

markAllAsRead: () => {
  return http.put({ url: '/notifications/read-all' })
}

// 修复后 ✅
markAsRead: (notificationId: string) => {
  return http.post({ url: `/notifications/${notificationId}/read` })
}

markAllAsRead: () => {
  return http.post({ url: '/notifications/read-all' })
}
```

**为什么用POST而不是PUT？**

- 后端已定义为 `@router.post`
- POST语义更符合"标记动作"
- 保持与后端一致

### 修复3：自动标记为已读

**文件**: `src/views/auth/login/index.vue`

```typescript
// 修复前 ❌
ElNotification({
  title: friendlyTitle,
  message: notification.content,
  type: notifType,
  duration: 6000,
  position: 'top-right',
  zIndex: 10000 + index,
  onClick: () => {
    // 只有点击才标记为已读
    notificationApi.markAsRead(notification.id).catch((e) => {
      console.error('标记通知已读失败:', e)
    })
  }
})

// 修复后 ✅
ElNotification({
  title: friendlyTitle,
  message: notification.content,
  type: notifType,
  duration: 6000,
  position: 'top-right',
  zIndex: 10000 + index
  // 移除 onClick
})

// 在系统通知之后，立即自动标记为已读
notificationApi.markAsRead(notification.id).catch((e) => {
  console.error('⚠️ [Login] 自动标记通知已读失败:', e)
})
```

**修改内容**：

1. ✅ 移除 `onClick` 事件中的标记逻辑
2. ✅ 在显示通知后立即自动标记为已读
3. ✅ 系统通知的 `onclick` 只保留 `window.focus()`

---

## 修复后的完整流程

### 用户登录后的通知流程

```
1. 用户登录成功
   ↓
2. 拉取未读通知 (GET /api/notifications/)
   ↓
3. 遍历每条通知，延迟显示 (500ms间隔)
   ├─ 显示网页内通知 (ElNotification)
   ├─ 显示系统通知 (Notification API)
   └─ 立即自动标记为已读 (POST /api/notifications/{id}/read) ✨
   ↓
4. 通知从Redis中删除
   ↓
5. 下次登录不再显示该通知
```

### API调用示例

**正确的URL**：

```
POST /api/notifications/17c405c2-5e20-4784-b5ae-7891d5f6bce0/read
```

**错误的URL（已修复）**：

```
PUT /api/api/notifications/17c405c2-5e20-4784-b5ae-7891d5f6bce0/read
     ^^^^^ 重复的 /api/
```

---

## 技术细节

### baseURL 的工作原理

```typescript
// backendApi.ts
const instance = axios.create({
  baseURL: '/api' // 基础路径
  // ...
})

// notificationApi.ts
http.get({ url: '/notifications/' }) // 相对路径

// 最终请求
// baseURL + url = /api + /notifications/ = /api/notifications/
```

### 为什么不在后端改？

**选项1：修改前端** ✅ (采用)

- 移除前端URL中的 `/api/` 前缀
- 让 `baseURL` 统一管理

**选项2：修改后端** ❌ (不采用)

- 修改后端 `prefix="/api/notifications"` 为 `prefix="/notifications"`
- 但这会影响所有其他API调用

**结论**：修改前端更合理，保持 `baseURL` 作为统一的API前缀。

### Redis通知存储机制

```python
# backend/app/services/redis_notification_storage.py

def mark_as_read(self, user_id: str, notification_id: str):
    """标记通知为已读（从 Redis 中删除）"""
    # 从未读列表中移除
    redis.lrem(f"notifications:unread:{user_id}", 0, notification_id)
    # 从哈希表中删除
    redis.hdel(f"notifications:data:{user_id}", notification_id)
```

**设计理念**：

- ✅ 已读即删除，节省Redis内存
- ✅ 通知7天自动过期
- ✅ 只保存未读通知
- ✅ 不需要"已读/未读"状态字段

---

## 测试清单

### 功能测试

- [x] 登录后自动显示未读通知
- [x] 通知显示后自动标记为已读
- [x] 无需手动点击
- [x] 不再出现405错误
- [x] URL路径正确 (`/api/notifications/...`)
- [x] 再次登录不会重复显示相同通知

### API测试

```bash
# 1. 获取通知列表
GET /api/notifications/
# 应该返回 200

# 2. 标记单个通知为已读
POST /api/notifications/{notification_id}/read
# 应该返回 200，不再返回405

# 3. 标记所有通知为已读
POST /api/notifications/read-all
# 应该返回 200
```

### 日志检查

```
✅ [Login] 已显示 7 条未读通知（自动标记为已读）
⚠️ [Login] 自动标记通知已读失败: ...  // 如果失败会有警告
```

---

## 修改的文件

| 文件                             | 修改内容                             | 状态 |
| -------------------------------- | ------------------------------------ | ---- |
| `src/api/notificationApi.ts`     | 移除URL中的`/api/`前缀，改为POST方法 | ✅   |
| `src/views/auth/login/index.vue` | 自动标记已读，移除onClick逻辑        | ✅   |

---

## 用户体验改进

### 修复前 ❌

```
1. 用户登录
2. 弹出7条通知
3. 用户需要逐一点击才能标记已读
4. 不点击的话，下次登录还会显示
5. 点击时报405错误
```

### 修复后 ✅

```
1. 用户登录
2. 弹出7条通知
3. 通知自动标记为已读 ✨
4. 下次登录不会重复显示
5. 无需任何手动操作
6. 不再有405错误
```

---

## 相关配置

### Vite代理配置

```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    // 不重写路径，直接转发 /api/xxx 到后端
  }
}
```

### 后端路由

```python
# backend/app/api/notifications.py
router = APIRouter(prefix="/api/notifications", tags=["通知"])

@router.post("/{notification_id}/read")
def mark_as_read(notification_id: str, current_user = Depends(get_current_user)):
    """标记通知为已读（从 Redis 中删除）"""
```

---

## 总结

✅ **问题1：URL重复** - 已修复

- 移除了notificationApi中所有URL的`/api/`前缀
- 由`baseURL`统一管理

✅ **问题2：405错误** - 已修复

- 将前端的`http.put`改为`http.post`
- 与后端的`@router.post`保持一致

✅ **问题3：需要手动点击** - 已修复

- 通知显示即自动标记为已读
- 用户无需任何手动操作
- 提升用户体验

🎉 **通知功能现在完全正常！**

---

## 未来优化建议

### 可选的改进

1. **批量标记已读**

   - 当前：逐个调用 `markAsRead(id)`
   - 优化：一次性调用 `markAllAsRead()`
   - 优点：减少API请求次数

2. **错误重试机制**

   - 当前：标记失败只打印错误
   - 优化：失败时自动重试1-2次
   - 优点：提高可靠性

3. **离线通知队列**
   - 当前：登录时才显示离线通知
   - 优化：持久化到localStorage，下次一定显示
   - 优点：防止通知丢失

但目前的实现已经足够满足需求！✅
