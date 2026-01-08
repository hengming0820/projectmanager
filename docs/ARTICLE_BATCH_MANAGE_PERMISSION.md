# 文章批量管理权限控制

## 修改说明

为"知识与文章"模块下的"会议记录"和"模型测试"页面的"批量管理"功能添加了权限控制，确保只有管理员（admin）和审核员（reviewer）才能访问该功能。

## 修改的文件

### 1. `src/views/project/articles/meeting/index.vue` - 会议记录页面

#### 修改内容：

**添加权限控制计算属性**（第681-682行）：

```typescript
// 权限控制：只有管理员和审核员可以进行批量管理
const canManageArticles = computed(() =>
  ['admin', 'reviewer'].includes(userStore.currentUser?.role || '')
)
```

**为批量管理按钮添加权限判断**（第15行）：

```vue
<el-button v-if="canManageArticles" @click="showBatchManageDialog = true" size="large">
  <el-icon><Setting /></el-icon>
  批量管理
</el-button>
```

### 2. `src/views/project/articles/model-test/index.vue` - 模型测试页面

#### 修改内容：

**添加权限控制计算属性**（第680-681行）：

```typescript
// 权限控制：只有管理员和审核员可以进行批量管理
const canManageArticles = computed(() =>
  ['admin', 'reviewer'].includes(userStore.currentUser?.role || '')
)
```

**为批量管理按钮添加权限判断**（第15行）：

```vue
<el-button v-if="canManageArticles" @click="showBatchManageDialog = true" size="large">
  <el-icon><Setting /></el-icon>
  批量管理
</el-button>
```

## 权限控制逻辑

### 权限规则

- ✅ **admin（管理员）**：可以看到并使用"批量管理"按钮
- ✅ **reviewer（审核员）**：可以看到并使用"批量管理"按钮
- ❌ **其他角色**：不显示"批量管理"按钮

### 实现方式

与"工作周管理"页面的权限控制保持一致：

```typescript
const canManageArticles = computed(() =>
  ['admin', 'reviewer'].includes(userStore.currentUser?.role || '')
)
```

## 验证步骤

### 1. 管理员/审核员登录

1. 使用管理员账号（admin）或审核员账号登录
2. 访问 "知识与文章" > "会议记录"
3. ✅ 应该能看到"批量管理"按钮
4. 访问 "知识与文章" > "模型测试"
5. ✅ 应该能看到"批量管理"按钮
6. 点击"批量管理"按钮
7. ✅ 应该能正常打开批量管理对话框

### 2. 普通用户登录

1. 使用普通用户账号（如标注员 annotator）登录
2. 访问 "知识与文章" > "会议记录"
3. ❌ 不应该看到"批量管理"按钮（只显示"发布会议记录"和"刷新"按钮）
4. 访问 "知识与文章" > "模型测试"
5. ❌ 不应该看到"批量管理"按钮（只显示"发布测试记录"和"刷新"按钮）

## 技术细节

### 使用的技术

- **Vue 3 Composition API**: `computed()` 计算属性
- **Pinia Store**: `useUserStore()` 获取当前用户信息
- **Vue 指令**: `v-if` 条件渲染

### 依赖项

- `@/store/modules/user` - 用户状态管理
- `userStore.currentUser?.role` - 当前用户角色信息

### 与其他功能的一致性

此实现方式与以下页面的权限控制保持一致：

- ✅ 工作周管理 - "创建工作周"按钮（`canManageWorkLog`）
- ✅ 工作周管理 - "批量管理"按钮（`canManageWorkLog`）

## 安全说明

### 前端权限控制

- 此修改仅实现了**前端UI层面的权限控制**
- 通过 `v-if` 指令隐藏按钮，防止普通用户看到和点击

### 后端权限控制

- ⚠️ **重要**: 前端权限控制只是第一道防线
- 后端API应该也要有相应的权限验证
- 建议检查以下后端接口的权限控制：
  - `DELETE /api/articles/batch` - 批量删除文章
  - `PATCH /api/articles/batch` - 批量编辑文章

### 推荐的后端验证

后端应该使用类似的权限装饰器：

```python
from app.utils.dependencies import require_permission

@router.delete("/articles/batch")
async def batch_delete_articles(
    current_user: User = Depends(get_current_user)
):
    # 检查用户角色
    if current_user.role not in ['admin', 'reviewer']:
        raise HTTPException(status_code=403, detail="权限不足")
    # ... 执行批量删除逻辑
```

## 用户体验优化

### 按钮显示逻辑

- 有权限：显示"批量管理"、"发布记录"、"刷新"三个按钮
- 无权限：只显示"发布记录"、"刷新"两个按钮
- 无需显示"权限不足"等提示，直接隐藏按钮更简洁

### 响应式更新

- 如果用户在使用过程中角色发生变化（例如被提升为管理员）
- 由于使用了 `computed` 属性，按钮会自动显示/隐藏
- 无需刷新页面

## 后续建议

### 1. 统一权限常量

建议创建一个权限常量文件：

```typescript
// src/config/permissions.ts
export const ROLES = {
  ADMIN: 'admin',
  REVIEWER: 'reviewer',
  ANNOTATOR: 'annotator',
  DEVELOPER: 'developer'
} as const

export const PERMISSIONS = {
  CAN_MANAGE_ARTICLES: [ROLES.ADMIN, ROLES.REVIEWER],
  CAN_MANAGE_WORKLOG: [ROLES.ADMIN, ROLES.REVIEWER],
  CAN_MANAGE_PROJECTS: [ROLES.ADMIN]
  // ... 其他权限定义
} as const
```

使用方式：

```typescript
import { PERMISSIONS } from '@/config/permissions'

const canManageArticles = computed(() =>
  PERMISSIONS.CAN_MANAGE_ARTICLES.includes(userStore.currentUser?.role || '')
)
```

### 2. 创建权限辅助函数

```typescript
// src/utils/permission.ts
import { useUserStore } from '@/store/modules/user'

export function usePermission() {
  const userStore = useUserStore()

  const hasRole = (roles: string[]) => {
    return roles.includes(userStore.currentUser?.role || '')
  }

  const canManageArticles = computed(() => hasRole(['admin', 'reviewer']))
  const canManageWorkLog = computed(() => hasRole(['admin', 'reviewer']))

  return {
    hasRole,
    canManageArticles,
    canManageWorkLog
  }
}
```

### 3. 其他可能需要权限控制的功能

建议检查以下功能是否也需要添加权限控制：

- [ ] 项目管理中的"批量操作"
- [ ] 用户管理中的"批量编辑"
- [ ] 任务管理中的"批量分配"

## 更新日期

- 2025-10-21: 初始版本 - 添加会议记录和模型测试的批量管理权限控制

## 维护者

- AI Assistant
