# 文章删除权限控制

## 修改说明

为所有文章删除功能添加了严格的权限控制，确保**只有文章创建者和管理员可以删除文章**。

## 权限规则

| 用户角色/身份       | 是否可以删除文章          | 说明                       |
| ------------------- | ------------------------- | -------------------------- |
| **admin（管理员）** | ✅ 可以删除任何文章       | 管理员拥有最高权限         |
| **文章创建者**      | ✅ 只能删除自己创建的文章 | 通过 `author_id` 匹配判断  |
| 其他被授权的编辑者  | ❌ 不能删除               | 即使有编辑权限，也不能删除 |
| 其他角色            | ❌ 不能删除               | 无权限                     |

## 修改的文件

### 1. `src/views/project/management/components/ArticleListView.vue` - 项目下的文章列表

#### 修改内容：

**导入依赖**（第117-122行）：

```typescript
import { ref, watch, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User, Clock, View } from '@element-plus/icons-vue'
import { articlesApi } from '@/api/articlesApi'
import { useUserStore } from '@/store/modules/user' // 新增
```

**添加权限控制函数**（第140-149行）：

```typescript
const router = useRouter()
const userStore = useUserStore()

// 权限控制：判断是否可以删除某篇文章
const canDeleteArticle = (article: any) => {
  if (!userStore.currentUser) return false
  const currentUserId = userStore.currentUser.id
  const currentUserRole = userStore.currentUser.role
  // 只有管理员和作者可以删除
  return currentUserRole === 'admin' || article.author_id === currentUserId
}
```

**为删除按钮添加权限判断**（第76行）：

```vue
<el-button
  v-if="canDeleteArticle(article)"
  type="danger"
  size="small"
  text
  @click.stop="handleDelete(article)"
>
  删除
</el-button>
```

---

### 2. `src/views/project/management/components/ArticleDetailView.vue` - 项目下的文章详情

#### 修改内容：

**修改 canDelete 计算属性**（第426-432行）：

```typescript
// 删除权限：只有管理员和作者可以删除
const canDelete = computed(() => {
  if (!article.value || !userStore.currentUser) return false
  const currentUserId = userStore.currentUser.id
  const currentUserRole = userStore.currentUser.role
  return currentUserRole === 'admin' || article.value.author_id === currentUserId
})
```

**之前的问题**：

- 旧代码：`const canDelete = computed(() => canEdit.value)`
- 问题：删除权限等同于编辑权限，导致被授权的编辑者也能删除文章
- 修复：单独定义删除权限，只允许管理员和作者删除

---

### 3. `src/views/project/articles/detail/index.vue` - 独立的文章详情页

#### 修改内容：

**添加 canDelete 计算属性**（第259-265行）：

```typescript
// 删除权限：只有管理员和作者可以删除
const canDelete = computed(() => {
  if (!article.value || !userStore.currentUser) return false
  const currentUserId = userStore.currentUser.id
  const currentUserRole = userStore.currentUser.role
  return currentUserRole === 'admin' || article.value.author_id === currentUserId
})
```

**修改删除按钮条件**（第120行）：

```vue
<!-- 之前 -->
<el-button v-if="canEdit" class="tool-btn danger" text @click="remove">
  <el-icon><Delete /></el-icon><span class="tool-text">删除</span>
</el-button>

<!-- 之后 -->
<el-button v-if="canDelete" class="tool-btn danger" text @click="remove">
  <el-icon><Delete /></el-icon><span class="tool-text">删除</span>
</el-button>
```

---

### 4. `src/views/project/articles/meeting/index.vue` - 会议记录页面

**状态**：✅ 已有正确的权限控制，无需修改

现有权限控制（第782-790行）：

```typescript
const canDelete = computed(() => {
  if (!currentArticle.value || !userStore.currentUser) return false

  const currentUserId = userStore.currentUser.id
  const currentUserRole = userStore.currentUser.role

  // 只有管理员和作者可以删除
  return currentUserRole === 'admin' || currentArticle.value.author_id === currentUserId
})
```

---

### 5. `src/views/project/articles/model-test/index.vue` - 模型测试页面

**状态**：✅ 已有正确的权限控制，无需修改

现有权限控制（第781-789行）：

```typescript
const canDelete = computed(() => {
  if (!currentArticle.value || !userStore.currentUser) return false

  const currentUserId = userStore.currentUser.id
  const currentUserRole = userStore.currentUser.role

  // 只有管理员和作者可以删除
  return currentUserRole === 'admin' || currentArticle.value.author_id === currentUserId
})
```

---

## 权限控制实现细节

### 权限判断逻辑

```typescript
// 通用的权限判断模式
const canDelete = computed(() => {
  // 1. 基础检查：文章和用户必须存在
  if (!article.value || !userStore.currentUser) return false

  // 2. 获取当前用户信息
  const currentUserId = userStore.currentUser.id
  const currentUserRole = userStore.currentUser.role

  // 3. 权限判断：管理员 OR 作者
  return currentUserRole === 'admin' || article.value.author_id === currentUserId
})
```

### 与编辑权限的区别

| 功能         | 管理员 | 文章创建者 | 被授权的编辑者    | 其他用户 |
| ------------ | ------ | ---------- | ----------------- | -------- |
| **编辑文章** | ✅     | ✅         | ✅ (如果被授权)   | ❌       |
| **删除文章** | ✅     | ✅         | ❌ (即使有编辑权) | ❌       |

**编辑权限** (`canEdit`) 包括：

- 管理员
- 文章创建者
- `editable_user_ids` 中指定的用户
- `editable_roles` 中指定角色的用户

**删除权限** (`canDelete`) 只包括：

- 管理员
- 文章创建者

---

## 验证步骤

### 1. 作为文章创建者测试

#### 在项目文章列表中：

1. 登录后访问"项目管理" > 选择某个项目 > "会议记录"或"模型测试"标签
2. ✅ 应该能看到自己创建的文章的"删除"按钮
3. ❌ 不应该看到其他人创建的文章的"删除"按钮
4. 点击自己文章的"删除"按钮
5. ✅ 应该能成功删除

#### 在文章详情页：

1. 访问自己创建的文章详情页
2. ✅ 右侧工具栏应该显示"删除"按钮
3. 点击"删除"按钮
4. ✅ 应该能成功删除

### 2. 作为管理员测试

1. 使用管理员账号（admin）登录
2. 访问任意文章列表或详情页
3. ✅ 应该能看到所有文章的"删除"按钮
4. 点击任何文章的"删除"按钮
5. ✅ 应该能成功删除

### 3. 作为被授权编辑者测试

假设用户 A 被授权编辑用户 B 的文章：

1. 使用用户 A 登录
2. 访问用户 B 创建的文章详情页
3. ✅ 应该能看到"编辑正文"和"编辑其他"按钮（有编辑权限）
4. ❌ 不应该看到"删除"按钮（无删除权限）
5. 在文章列表中
6. ❌ 用户 B 的文章卡片上不应该显示"删除"按钮

### 4. 作为普通用户测试

1. 使用普通用户账号（非管理员，非作者）登录
2. 访问其他人的文章列表或详情页
3. ❌ 不应该看到任何"删除"按钮
4. ❌ 不应该看到"编辑"按钮

---

## 技术细节

### 前端权限控制方式

1. **条件渲染**：使用 `v-if` 指令控制按钮显示

   ```vue
   <el-button v-if="canDelete" @click="deleteArticle">删除</el-button>
   ```

2. **计算属性**：动态计算权限状态

   ```typescript
   const canDelete = computed(() => {
     /* 权限逻辑 */
   })
   ```

3. **响应式更新**：当用户角色或文章作者变化时，权限自动更新

### 数据依赖

权限判断依赖以下数据：

- `userStore.currentUser` - 当前登录用户信息
  - `id` - 用户ID
  - `role` - 用户角色
- `article.author_id` - 文章创建者ID

### 安全性说明

⚠️ **重要**：前端权限控制只是第一道防线！

**后端权限验证**：后端API也应该有相应的权限检查。建议检查以下接口：

```python
# backend/app/api/articles.py

@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. 查询文章
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 2. 权限检查
    is_admin = current_user.role == 'admin'
    is_author = article.author_id == current_user.id

    if not (is_admin or is_author):
        raise HTTPException(
            status_code=403,
            detail="权限不足：只有管理员和文章创建者可以删除文章"
        )

    # 3. 执行删除
    db.delete(article)
    db.commit()
    return {"message": "删除成功"}
```

---

## 用户体验优化

### 1. 优雅降级

- 无权限时直接隐藏删除按钮，避免用户点击后提示"权限不足"
- 保持界面简洁，不显示不可用的功能

### 2. 视觉反馈

- 删除按钮使用危险色（红色）：`type="danger"`
- 删除前弹出确认对话框，防止误操作

### 3. 一致性

- 所有文章删除场景使用相同的权限规则
- 与编辑权限明确区分，避免混淆

---

## 相关文档

- [文章批量管理权限控制](./ARTICLE_BATCH_MANAGE_PERMISSION.md) - 批量管理功能的权限控制
- [工作周管理权限](./src/views/work-log/index.vue) - 参考实现

---

## 后续建议

### 1. 统一权限管理

建议创建统一的权限辅助函数：

```typescript
// src/utils/article-permission.ts
import { useUserStore } from '@/store/modules/user'

export function useArticlePermission() {
  const userStore = useUserStore()

  /**
   * 判断是否可以删除文章
   * @param article 文章对象
   * @returns 是否有删除权限
   */
  const canDeleteArticle = (article: any): boolean => {
    if (!article || !userStore.currentUser) return false
    const currentUserId = userStore.currentUser.id
    const currentUserRole = userStore.currentUser.role
    return currentUserRole === 'admin' || article.author_id === currentUserId
  }

  /**
   * 判断是否可以编辑文章
   * @param article 文章对象
   * @returns 是否有编辑权限
   */
  const canEditArticle = (article: any): boolean => {
    // ... 编辑权限逻辑
  }

  return {
    canDeleteArticle,
    canEditArticle
  }
}
```

### 2. 权限常量化

```typescript
// src/config/permissions.ts
export const ARTICLE_PERMISSIONS = {
  DELETE: ['admin', 'author'],
  EDIT: ['admin', 'author', 'authorized_editors'],
  VIEW: ['all']
} as const
```

### 3. 后端权限中间件

建议在后端统一处理文章权限检查：

```python
# backend/app/utils/article_permissions.py
def check_article_delete_permission(article: Article, current_user: User):
    """检查文章删除权限"""
    is_admin = current_user.role == 'admin'
    is_author = article.author_id == current_user.id

    if not (is_admin or is_author):
        raise HTTPException(
            status_code=403,
            detail="只有管理员和文章创建者可以删除文章"
        )
```

---

## 更新日期

- 2025-10-21: 初始版本 - 为所有文章删除功能添加权限控制

## 维护者

- AI Assistant
