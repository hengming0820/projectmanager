# 通知与任务领取限制修复

## 📋 修复内容

### 问题 1: 管理员未收到跳过申请通知

**问题描述**：

- 标注员申请跳过任务后，审核员和管理员应该收到通知，但管理员没有收到
- 后端只向审核员发送了通知，遗漏了管理员

**根本原因**：

- 后端 `request_skip_task` 函数中只调用了一次 `broadcast_to_role(role="reviewer")`
- 没有像任务提交通知那样同时发送给 `admin` 角色
- 前端 WebSocket 连接的角色识别逻辑也需要优化，确保更可靠

**修复方案**：

#### 1. 后端添加管理员通知 (`backend/app/api/tasks.py`)

**修改前**（第986-1003行）：

```python
# 通知审核员：有新的跳过申请
try:
    pending_skips = db.query(Task).filter(Task.status == "skip_pending").count()
    from_name = getattr(current_user, 'real_name', None) or current_user.username
    content = f"{from_name} 提交了任务（{task.title}）的跳过申请，待审核"
    logger.info(f"🔔 [TaskAPI] 广播跳过申请 -> reviewer, 待审核跳过: {pending_skips}")
    await ws_manager.broadcast_to_role(
        role="reviewer",
        message={
            "type": "skip_requested",
            "title": "有新的跳过申请",
            "content": content,
            "pending_skip": pending_skips,
            "task_id": task_id
        }
    )
except Exception as _e:
    logger.warning(f"通知审核员跳过申请失败: {_e}")
```

**修改后**：

```python
# 通知审核员和管理员：有新的跳过申请
try:
    pending_skips = db.query(Task).filter(Task.status == "skip_pending").count()
    from_name = getattr(current_user, 'real_name', None) or current_user.username
    content = f"{from_name} 提交了任务（{task.title}）的跳过申请，待审核"

    # 通知审核员
    logger.info(f"🔔 [TaskAPI] 广播跳过申请 -> reviewer, 待审核跳过: {pending_skips}")
    await ws_manager.broadcast_to_role(
        role="reviewer",
        message={
            "type": "skip_requested",
            "title": "有新的跳过申请",
            "content": content,
            "pending_skip": pending_skips,
            "task_id": task_id
        }
    )

    # 通知管理员
    logger.info(f"🔔 [TaskAPI] 广播跳过申请 -> admin, 待审核跳过: {pending_skips}")
    await ws_manager.broadcast_to_role(
        role="admin",
        message={
            "type": "skip_requested",
            "title": "有新的跳过申请",
            "content": content,
            "pending_skip": pending_skips,
            "task_id": task_id
        }
    )
except Exception as _e:
    logger.warning(f"通知审核员和管理员跳过申请失败: {_e}")
```

#### 2. 优化前端角色识别逻辑 (`src/store/modules/user.ts`)

**修改前**：

```typescript
const payload = {
  role: (user.role || '').toLowerCase().includes('admin')
    ? 'admin'
    : (user.role || '').toLowerCase() ||
      ((user.roles || []).includes('R_REVIEWER') ? 'reviewer' : ''),
  user: { id: user.id, username: user.username, real_name: user.realName || user.real_name }
}
```

**修改后**：

```typescript
// 修复角色判断逻辑，确保审核员角色正确识别
let userRole = (user.role || '').toLowerCase()
const rolesArr: string[] = Array.isArray(user.roles) ? user.roles : []

// 优先判断 admin，其次是 reviewer，最后是 annotator
if (userRole === 'admin' || rolesArr.includes('R_ADMIN')) {
  userRole = 'admin'
} else if (userRole === 'reviewer' || rolesArr.includes('R_REVIEWER')) {
  userRole = 'reviewer'
} else if (userRole === 'annotator' || rolesArr.includes('R_ANNOTATOR')) {
  userRole = 'annotator'
}

const payload = {
  role: userRole,
  user: { id: user.id, username: user.username, real_name: user.realName || user.real_name }
}

console.log('🔔 [WS] 准备连接，角色信息:', {
  originalRole: user.role,
  finalRole: userRole,
  payload
})
```

#### 3. 主动请求通知权限（额外优化）

为确保审核员和管理员能收到通知，前端也进行了优化：

**在用户登录时（`setUserInfo` 函数）**：

```typescript
// 对于审核员和管理员，立即请求通知权限
const role = (currentUser.value?.role || '').toLowerCase()
if (role === 'reviewer' || role === 'admin') {
  console.log('🔔 [UserStore] 检测到审核员/管理员，请求通知权限')
  setTimeout(() => {
    ensureNotificationPermission().then((granted) => {
      if (granted) {
        console.log('✅ [UserStore] 通知权限已授予')
      } else {
        console.warn('⚠️ [UserStore] 通知权限未授予，用户可能拒绝了通知')
      }
    })
  }, 500)
}
```

**在 WebSocket 连接成功时**：

```typescript
notifySocket.onopen = () => {
  opened = true
  clearTimeout(safetyTimer)
  try {
    localStorage.setItem('ws_notify_url', url)
  } catch {}
  try {
    notifySocket?.send(JSON.stringify(payload))
    console.log('🔔 [WS] 通知连接已建立:', url, '角色:', payload.role)
  } catch {}

  // 建立连接后尝试申请系统通知权限（审核员和管理员）
  const role = payload.role
  if (role === 'reviewer' || role === 'admin') {
    setTimeout(() => {
      ensureNotificationPermission().then((granted) => {
        console.log(`🔔 [WS] ${role} 通知权限请求结果:`, granted ? '已授予' : '未授予')
      })
    }, 800)
  }
}
```

---

### 问题 2: 任务领取超限时前端没有提示

**问题描述**：

- 标注员领取第四个任务时，后端会返回错误，但前端只显示"领取失败"，没有说明具体原因
- 用户不知道为什么无法领取，体验不好

**根本原因**：

- 前端的 `claimTask` 函数错误处理过于简单，没有提取后端返回的详细错误信息

**修复方案**：

#### 改进错误处理 (`src/views/project/task-pool/index.vue`)

**修改前**：

```typescript
const claimTask = async (task: Task) => {
  try {
    await ElMessageBox.confirm(`确定要领取任务"${task.title}"吗？`, '确认领取', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    await projectStore.claimTask(task.id)
    ElMessage.success('领取成功')
    fetchTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('领取失败')
    }
  }
}
```

**修改后**：

```typescript
const claimTask = async (task: Task) => {
  try {
    await ElMessageBox.confirm(`确定要领取任务"${task.title}"吗？`, '确认领取', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    await projectStore.claimTask(task.id)
    ElMessage.success('领取成功')
    fetchTasks()
  } catch (error: any) {
    if (error !== 'cancel') {
      // 显示详细的错误信息
      const errorMessage = error?.response?.data?.detail || error?.message || '领取失败'

      // 特殊处理任务上限错误
      if (errorMessage.includes('上限') || errorMessage.includes('已达')) {
        ElMessageBox.alert(
          '您当前有3个进行中或已提交的任务，已达到可领取任务上限。请先完成部分任务后再领取新任务。',
          '无法领取任务',
          {
            confirmButtonText: '我知道了',
            type: 'warning'
          }
        )
      } else {
        ElMessage.error(errorMessage)
      }
    }
  }
}
```

---

## ✅ 测试验证

### 通知功能测试

#### 1. **跳过申请通知测试（本次修复重点）**：

**标注员申请跳过**：

- 标注员在"我的工作台"页面，对一个进行中的任务申请跳过
- 后端日志应显示：
  ```
  🔔 [TaskAPI] 广播跳过申请 -> reviewer, 待审核跳过: 1
  🔔 [TaskAPI] 广播跳过申请 -> admin, 待审核跳过: 1
  ```

**审核员和管理员接收通知**：

- ✅ **审核员**应收到浏览器通知：`有新的跳过申请`
- ✅ **管理员**也应收到浏览器通知：`有新的跳过申请`（**本次修复**）
- 两者都应看到 Element Plus 消息提示
- 控制台应显示：`🔔 [WS] 收到消息: {type: "skip_requested", ...}`

#### 2. **审核员/管理员登录测试**：

- 审核员或管理员登录后，浏览器应弹出通知权限请求
- 控制台应显示：`🔔 [UserStore] 检测到审核员/管理员，请求通知权限`
- 控制台应显示：`🔔 [WS] 通知连接已建立: ... 角色: reviewer` 或 `admin`

#### 3. **其他通知功能测试**：

- ✅ 标注员提交任务 → 审核员和管理员收到通知
- ✅ 审核员审核通过/驳回 → 标注员收到通知
- ✅ 管理员审核跳过申请 → 标注员收到通知

### 任务领取限制测试

1. **正常领取测试**：

   - 标注员领取第1、2、3个任务 → 成功，显示"领取成功"

2. **超限领取测试**：

   - 标注员尝试领取第4个任务
   - 应显示详细提示对话框：

     ```
     无法领取任务

     您当前有3个进行中或已提交的任务，已达到可领取任务上限。
     请先完成部分任务后再领取新任务。

     [我知道了]
     ```

3. **管理员特权测试**：
   - 管理员不受3个任务限制，可以领取更多任务

---

## 🔧 相关代码

### 修改的文件

#### 后端修改：

1. **`backend/app/api/tasks.py`**（第986-1019行）
   - **核心修复**：在 `request_skip_task` 函数中添加了向管理员广播通知的代码
   - 原来只通知审核员 `broadcast_to_role(role="reviewer")`
   - 现在同时通知管理员 `broadcast_to_role(role="admin")`

#### 前端优化：

1. **`src/store/modules/user.ts`**

   - 优化 WebSocket 角色识别逻辑，确保角色正确发送到后端
   - 添加主动通知权限请求（登录时和 WebSocket 连接时）
   - 改进日志输出，便于调试

2. **`src/views/project/task-pool/index.vue`**
   - 改进任务领取错误处理
   - 添加任务上限专用提示对话框

### 后端相关代码（参考）

- **`backend/app/api/tasks.py`**

  - 第378-456行：`submit_task` 函数 - 任务提交通知（已完整，同时通知 reviewer 和 admin）
  - 第296-376行：`claim_task` 函数 - 任务领取限制检查（已完整）
  - 第936-1020行：`request_skip_task` 函数 - 跳过申请通知（**本次修复**）

- **`backend/app/services/notification_ws.py`**
  - `broadcast_to_role` 函数：根据角色广播通知
  - `send_to_user_id` 函数：向特定用户发送通知

---

## 📌 注意事项

1. **通知权限**：

   - 用户首次登录时需要授予浏览器通知权限
   - 如果用户拒绝，后续可以在浏览器设置中重新授予

2. **WebSocket 连接**：

   - 需要确保后端 WebSocket 服务正常运行
   - 检查控制台日志确认连接成功

3. **角色配置**：
   - 确保用户的 `role` 字段为 `'reviewer'`、`'admin'` 或 `'annotator'`
   - 如果使用 `roles` 数组，确保包含 `'R_REVIEWER'`、`'R_ADMIN'` 或 `'R_ANNOTATOR'`

---

## 📝 总结

这次修复解决了两个关键问题：

### 1. **跳过申请通知缺失（核心问题）**

- **问题**：标注员申请跳过任务时，管理员没有收到通知
- **原因**：后端代码遗漏了向管理员发送通知的逻辑
- **修复**：在 `request_skip_task` 函数中添加 `broadcast_to_role(role="admin")` 调用
- **效果**：现在标注员申请跳过时，审核员和管理员都会收到通知

### 2. **任务领取超限提示不友好**

- **问题**：标注员领取第4个任务时，只显示"领取失败"，没有说明原因
- **原因**：前端错误处理过于简单，没有提取详细错误信息
- **修复**：改进错误处理，特别处理任务上限错误，显示详细说明对话框
- **效果**：用户能清楚了解为什么无法领取更多任务，并知道如何解决

### 附加优化：

- 优化了前端 WebSocket 角色识别逻辑，确保更可靠
- 改进了通知权限请求时机，审核员/管理员登录时主动请求
- 增强了日志输出，便于问题排查

修复后，整个通知和任务管理流程更加完善和用户友好。
