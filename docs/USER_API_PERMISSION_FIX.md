# 用户API权限修复文档

## 📋 问题描述

### 问题1：获取用户列表403错误

- **现象**：非管理员用户（如算法工程师）在访问项目管理页面下的文章时，出现403 Forbidden错误
- **原因**：`ArticleDetailView.vue` 加载时调用 `/users/` API获取用户列表，该API要求 `UserManagement` 权限
- **影响**：导致非管理员用户无法正常查看文章详情

### 问题2：按钮权限控制缺失

- **现象**：所有用户都能看到"新建项目"和项目设置按钮
- **期望**：只有管理员才能看到这些管理功能按钮

---

## ✅ 解决方案

### 1. 新增简化用户列表API

**文件**: `backend/app/api/users.py`

新增 `/users/simple` 端点，提供基础用户信息查询：

```python
@router.get("/simple")
def get_simple_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # 所有登录用户都可以访问
):
    """获取简化的用户列表（所有登录用户可访问，仅返回基本信息）"""
    users = db.query(User).filter(User.status == "active").all()
    return {
        "code": 200,
        "msg": "成功",
        "data": [
            {
                "id": u.id,
                "username": u.username,
                "real_name": u.real_name,
                "department": u.department
            }
            for u in users
        ]
    }
```

**特点**：

- ✅ 所有登录用户都可以访问
- ✅ 只返回基本信息（id, username, real_name, department）
- ✅ 只返回活跃用户
- ✅ 不暴露敏感信息（密码、角色、权限等）

---

### 2. 前端API封装

**文件**: `src/api/userApi.ts`

```typescript
// 获取简化的用户列表（所有登录用户可访问）
getSimpleUsers: () => backendApi.get('/users/simple'),
```

---

### 3. 修改所有非管理界面的用户查询

将以下文件中的 `userApi.getUsers()` 调用改为 `userApi.getUsersBasic()` 或 `userApi.getSimpleUsers()`：

#### 3.1 文章相关页面

| 文件 | 修改位置 | 说明 |
| --- | --- | --- |
| `src/views/project/management/components/ArticleDetailView.vue` | `loadUsers()` | 文章详情页加载用户列表 |
| `src/views/project/articles/create/index.vue` | `loadUsersAndDepts()` | 创建文章页选择作者 |
| `src/views/project/articles/detail/index.vue` | `loadUsersAndDepts()` | 文章详情页选择编辑者 |

#### 3.2 协作文档页面

| 文件                                       | 修改位置              | 说明                   |
| ------------------------------------------ | --------------------- | ---------------------- |
| `src/views/collaboration/create/index.vue` | `loadUsersAndDepts()` | 创建协作文档选择协作者 |
| `src/views/collaboration/index.vue`        | `loadUsersAndDepts()` | 协作文档列表页         |

#### 3.3 工作日志页面

| 文件                               | 修改位置            | 说明               |
| ---------------------------------- | ------------------- | ------------------ |
| `src/views/work-log/index.vue`     | `loadUsers()`       | 工作日志页加载用户 |
| `src/views/work-log/index.vue`     | `loadActiveUsers()` | 加载活跃用户       |
| `src/views/work-log/index-new.vue` | `loadUsers()`       | 新工作日志页       |

#### 3.4 Store模块

| 文件                           | 修改位置       | 说明                 |
| ------------------------------ | -------------- | -------------------- |
| `src/store/modules/project.ts` | 加载项目数据时 | 项目统计需要用户信息 |

**注意**：`src/store/modules/user.ts` 中的 `fetchUsers()` 方法保持不变，因为它专门用于用户管理界面，需要管理员权限。

---

### 4. 添加按钮权限控制

**文件**: `src/views/project/management/index-new.vue`

#### 4.1 引入用户Store

```typescript
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()

// 权限判断：是否为管理员
const isAdmin = computed(() => {
  return userStore.currentUser?.role === 'admin'
})
```

#### 4.2 控制"新建项目"按钮

```vue
<el-button v-if="isAdmin" type="primary" @click="showCreateProjectDialog = true">
  <el-icon><FolderAdd /></el-icon>
  新建项目
</el-button>
```

#### 4.3 控制项目"设置"按钮

```vue
<div
  v-if="data.type === 'project' && isAdmin"
  class="node-manage-btn-wrapper"
  @click.stop.prevent
  @mousedown.stop
  @mouseup.stop
>
  <el-button
    @click.stop="openCategoryManage(data.project)"
    type="primary"
    text
    size="small"
    class="node-manage-btn"
  >
    <el-icon><Setting /></el-icon>
  </el-button>
</div>
```

---

## 📊 API权限对比

| API端点 | 权限要求 | 返回字段 | 使用场景 |
| --- | --- | --- | --- |
| `GET /users/` | `UserManagement` | 完整用户信息 | 用户管理页面 |
| `GET /users/basic` | 登录用户 | id, username, real_name, department, role, status | 工作日志、部门管理 |
| `GET /users/simple` | 登录用户 | id, username, real_name, department | 文章作者、协作者选择 |

---

## 🔄 修改文件列表

### 后端文件（1个）

- `backend/app/api/users.py` - 新增 `/users/simple` 端点

### 前端文件（11个）

- `src/api/userApi.ts` - 新增 `getSimpleUsers` 方法
- `src/views/project/management/index-new.vue` - 添加按钮权限控制
- `src/views/project/management/components/ArticleDetailView.vue` - 改用 `getSimpleUsers`
- `src/views/project/articles/create/index.vue` - 改用 `getUsersBasic`
- `src/views/project/articles/detail/index.vue` - 改用 `getUsersBasic`
- `src/views/collaboration/create/index.vue` - 改用 `getUsersBasic`
- `src/views/collaboration/index.vue` - 改用 `getUsersBasic`
- `src/views/work-log/index.vue` - 改用 `getUsersBasic`（2处）
- `src/views/work-log/index-new.vue` - 改用 `getUsersBasic`
- `src/store/modules/project.ts` - 改用 `getUsersBasic`

---

## ✨ 修复效果

### 修复前

- ❌ 算法工程师访问项目文章时出现403错误
- ❌ 所有用户都能看到"新建项目"和"设置"按钮（但点击后可能失败）

### 修复后

- ✅ 所有登录用户都能正常访问项目文章
- ✅ 只有管理员才能看到管理功能按钮
- ✅ 非管理员用户体验更加流畅
- ✅ 安全性更高，敏感信息不会暴露给普通用户

---

## 🚀 部署说明

1. **重启后端服务**（必须）

   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **刷新前端页面**（可选）

   - 前端代码已自动热更新
   - 建议清除浏览器缓存后刷新

3. **验证修复**
   - 使用非管理员账号登录
   - 访问项目管理页面
   - 点击项目下的文章，确认不再出现403错误
   - 确认"新建项目"和"设置"按钮不可见

---

## 📝 注意事项

1. **向后兼容**：

   - 原有的 `/users/` API保持不变，用户管理页面仍然使用此API
   - 新增的 `/users/simple` API不影响现有功能

2. **安全性**：

   - `/users/simple` 只返回基本信息，不暴露敏感数据
   - 按钮权限控制在前端进行，后端API仍然有权限验证

3. **性能**：
   - `/users/simple` 查询更快，因为只查询活跃用户且返回字段更少
   - 建议在不需要完整用户信息的场景下使用此API

---

## 🐛 已知问题

无

---

## 📚 相关文档

- [权限管理系统](./PERMISSION_MANAGEMENT.md)
- [角色权限使用指南](./ROLE_PERMISSION_USAGE_GUIDE.md)

---

**版本**: v1.0  
**更新时间**: 2025-10-16  
**修复人员**: AI Assistant
