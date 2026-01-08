# 权限管理体系说明

## 🎯 权限管理概述

本系统采用 **RBAC（Role-Based Access Control，基于角色的访问控制）** 模型，通过角色来统一管理用户的菜单访问权限和按钮操作权限。

**更新日期**: 2025-10-16  
**版本**: v1.0

---

## 📊 权限架构

### 核心组成部分

```
┌─────────────────────────────────────────────┐
│                   用户 (User)                │
│  - id, username, role (角色编码)             │
└──────────────────┬──────────────────────────┘
                   │
                   │ 1:1 关联
                   ▼
┌─────────────────────────────────────────────┐
│                 角色 (Role)                  │
│  - id, name (角色名称), role (角色编码)       │
│  - permissions (权限JSON)                    │
└──────────────────┬──────────────────────────┘
                   │
                   │ 存储权限列表
                   ▼
┌─────────────────────────────────────────────┐
│          权限标识符 (Permissions)             │
│  菜单权限: ["Dashboard", "Project", ...]     │
│  按钮权限: ["UserManagement", ...]           │
└─────────────────────────────────────────────┘
```

---

## 📋 数据库模型

### 1. **角色表 (`roles`)**

```python
class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True)
    name = Column(String(50), unique=True)       # 角色名称（如：管理员）
    role = Column(String(50), unique=True)       # 角色编码（如：admin）
    description = Column(Text)                   # 角色描述
    is_active = Column(Boolean, default=True)    # 是否启用
    permissions = Column(Text)                   # 权限JSON字符串
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**permissions 字段格式：**

```json
[
  "Dashboard", // 菜单权限
  "Project", // 菜单权限
  "TaskPool", // 菜单权限
  "UserManagement", // 菜单权限
  "RoleManagement" // 菜单权限
]
```

### 2. **用户表 (`users`)**

```python
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True)
    role = Column(String(50))  # 关联到 roles.role（角色编码）
    # ... 其他字段
```

---

## 🔐 权限类型

### 1. **菜单权限**

控制用户可以访问哪些页面。

**权限标识符 = 路由的 `name` 字段**

```javascript
// 示例：菜单配置
{
  "name": "Project",  // ← 这就是菜单权限标识符
  "path": "/project",
  "meta": {"title": "项目管理"}
}
```

**当前系统菜单权限列表：**

| 权限标识符                | 菜单名称     | 说明                 |
| ------------------------- | ------------ | -------------------- |
| `Dashboard`               | 仪表板       | 首页控制台           |
| `Console`                 | 控制台       | 仪表板子页面         |
| `Project`                 | 项目管理     | 项目管理模块         |
| `ProjectDashboard`        | 项目仪表板   | 项目数据可视化       |
| `ProjectManagement`       | 项目列表     | 项目列表管理         |
| `Task`                    | 标注任务     | 任务管理模块         |
| `TaskPool`                | 任务池       | 任务分配             |
| `MyWorkspace`             | 我的工作台   | 个人任务管理         |
| `TaskReview`              | 任务审核     | 任务审核             |
| `WorkLog`                 | 工作日志     | 工作日志模块         |
| `WorkLogManagement`       | 周列表       | 工作周管理           |
| `WorkLogWeekDetail`       | 工作周详情   | 工作周详细信息       |
| `Articles`                | 知识与文章   | 知识管理模块         |
| `MeetingNotes`            | 会议记录     | 会议纪要             |
| `ModelTests`              | 模型测试     | 模型测试文档         |
| `CollaborationManagement` | 团队协作     | 协作文档             |
| `ArticleDetail`           | 文章详情     | 文章查看（隐藏页面） |
| `CollaborationCreate`     | 创建协作文档 | 文档创建（隐藏页面） |
| `CollaborationDocument`   | 协作文档     | 文档编辑（隐藏页面） |
| `Performance`             | 标注绩效     | 绩效管理模块         |
| `PersonalPerformance`     | 个人绩效     | 个人绩效查看         |
| `TeamPerformance`         | 团队绩效     | 团队绩效统计         |
| `System`                  | 系统管理     | 系统管理模块         |
| `UserManagement`          | 用户管理     | 用户管理             |
| `RoleManagement`          | 角色管理     | 角色权限管理         |
| `UserCenter`              | 个人中心     | 个人信息（隐藏页面） |

### 2. **API权限**

控制用户可以调用哪些API接口。

**通过装饰器 `require_permission()` 实现：**

```python
from app.utils.permissions import require_permission

@router.get("/users/")
def get_users(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("UserManagement"))
):
    # 只有拥有 UserManagement 权限的用户才能访问
    pass
```

### 3. **按钮权限（前端控制）**

控制页面中按钮的显示和操作。

```vue
<script setup>
  import { useUserStore } from '@/store/modules/user'

  const userStore = useUserStore()

  // 检查权限
  if (userStore.hasPermission('WorkLogManagement')) {
    // 显示管理按钮
  }
</script>
```

---

## 🔧 权限验证流程

### 1. **后端菜单权限过滤**

```python
# backend/app/api/menu.py

@router.get("/list")
def get_menu_list(current_user: User, db: Session):
    # 1. 获取完整菜单
    menu_list = [...]

    # 2. 判断是否为管理员
    if current_user.role.lower() in ['admin', 'super', 'administrator']:
        return {"menuList": menu_list}  # 管理员返回全部菜单

    # 3. 非管理员：从数据库加载角色权限
    role = db.query(Role).filter(Role.role == current_user.role).first()
    allowed = json.loads(role.permissions)  # ["Project", "TaskPool", ...]

    # 4. 递归过滤菜单
    def filter_menus(items):
        filtered = []
        for item in items:
            # 检查当前项是否有权限
            if item["name"] in allowed:
                filtered.append(item)
            # 递归检查子菜单
            elif item.get("children"):
                kept_children = filter_menus(item["children"])
                if kept_children:
                    item["children"] = kept_children
                    filtered.append(item)
        return filtered

    menu_list = filter_menus(menu_list)
    return {"menuList": menu_list}
```

### 2. **后端API权限验证**

```python
# backend/app/utils/permissions.py

def require_permission(permission_name: str):
    """权限验证装饰器"""
    def _dep(current_user=Depends(get_current_user), db=Depends(get_db)):
        # 1. 加载用户角色的权限列表
        role = db.query(Role).filter(Role.role == current_user.role).first()
        permissions = json.loads(role.permissions) if role else []

        # 2. 检查是否拥有所需权限
        if permission_name in permissions:
            return current_user

        # 3. 无权限，抛出403错误
        raise HTTPException(
            status_code=403,
            detail=f"权限不足，缺少访问权限: {permission_name}"
        )

    return _dep
```

### 3. **前端权限判断**

```typescript
// src/store/modules/user.ts

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null)

  // 权限检查方法
  const hasPermission = (permission: string): boolean => {
    if (!currentUser.value) return false

    // 超级管理员拥有所有权限
    if (currentUser.value.role === 'admin') return true

    // 基于角色的简化权限判断
    const rolePermissions: Record<string, string[]> = {
      admin: ['*'],
      annotator: ['WorkLogView', 'WorkLogEdit'],
      reviewer: ['WorkLogView', 'WorkLogReview', 'WorkLogManagement']
    }

    const userPermissions = rolePermissions[currentUser.value.role] || []
    return userPermissions.includes('*') || userPermissions.includes(permission)
  }

  return { hasPermission }
})
```

---

## 👥 默认角色权限配置

### 1. **管理员 (`admin`)**

```json
{
  "role": "admin",
  "name": "管理员",
  "permissions": "*" // 特殊处理：拥有所有权限
}
```

**权限说明**：

- ✅ 访问所有菜单
- ✅ 调用所有API
- ✅ 管理所有用户和角色

### 2. **标注员 (`annotator`)**

```json
{
  "role": "annotator",
  "name": "标注员",
  "permissions": [
    "Dashboard",
    "Console",
    "Task",
    "TaskPool",
    "MyWorkspace",
    "WorkLog",
    "WorkLogManagement",
    "Articles",
    "MeetingNotes",
    "ModelTests",
    "Performance",
    "PersonalPerformance"
  ]
}
```

**权限说明**：

- ✅ 查看仪表板
- ✅ 领取和完成任务
- ✅ 管理自己的工作台
- ✅ 查看和编辑工作日志
- ✅ 查看知识文章
- ✅ 查看个人绩效
- ❌ 无法审核任务
- ❌ 无法管理项目
- ❌ 无法管理用户

### 3. **审核员 (`reviewer`)**

```json
{
  "role": "reviewer",
  "name": "审核员",
  "permissions": [
    "Dashboard",
    "Console",
    "Task",
    "TaskPool",
    "MyWorkspace",
    "TaskReview",
    "WorkLog",
    "WorkLogManagement",
    "Articles",
    "MeetingNotes",
    "ModelTests",
    "Performance",
    "PersonalPerformance",
    "TeamPerformance"
  ]
}
```

**权限说明**：

- ✅ 标注员的所有权限
- ✅ 审核任务
- ✅ 查看团队绩效
- ✅ 管理工作日志
- ❌ 无法管理项目
- ❌ 无法管理用户

### 4. **项目经理 (`project_manager`)**

```json
{
  "role": "project_manager",
  "name": "项目经理",
  "permissions": [
    "Dashboard",
    "Console",
    "Project",
    "ProjectDashboard",
    "ProjectManagement",
    "Task",
    "TaskPool",
    "MyWorkspace",
    "TaskReview",
    "WorkLog",
    "WorkLogManagement",
    "Articles",
    "MeetingNotes",
    "ModelTests",
    "CollaborationManagement",
    "Performance",
    "PersonalPerformance",
    "TeamPerformance"
  ]
}
```

**权限说明**：

- ✅ 审核员的所有权限
- ✅ 管理项目
- ✅ 查看项目仪表板
- ✅ 管理团队协作文档
- ❌ 无法管理用户和角色

---

## 🛠️ 权限管理操作

### 1. **创建角色并分配权限**

#### 后端API

```bash
# 1. 创建角色
POST /roles/
{
  "name": "数据分析师",
  "role": "analyst",
  "description": "负责数据分析和报表"
}

# 2. 分配权限
PUT /roles/{role_id}/permissions
{
  "permissions": [
    "Dashboard",
    "Console",
    "Performance",
    "PersonalPerformance",
    "TeamPerformance"
  ]
}
```

#### 前端界面

1. 进入 **系统管理 > 角色管理**
2. 点击"创建角色"
3. 填写角色信息
4. 在权限配置中勾选需要的菜单和功能
5. 保存

### 2. **给用户分配角色**

```bash
# 更新用户角色
PUT /users/{user_id}
{
  "role": "analyst"
}
```

### 3. **修改角色权限**

```bash
# 更新角色权限
PUT /roles/{role_id}/permissions
{
  "permissions": [
    "Dashboard",
    "Project",
    "TaskPool"
  ]
}
```

**注意**：修改角色权限后，该角色的所有用户在下次登录时会自动生效。

---

## 🔍 权限验证示例

### 示例 1：API权限验证

```python
from app.utils.permissions import require_permission

# 场景：只有拥有 UserManagement 权限的用户才能删除用户
@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("UserManagement"))
):
    # 权限验证通过，执行删除逻辑
    # ...
    pass
```

### 示例 2：前端按钮权限控制

```vue
<template>
  <div>
    <!-- 只有拥有 WorkLogManagement 权限的用户才能看到此按钮 -->
    <el-button v-if="userStore.hasPermission('WorkLogManagement')" @click="manageWorkLog">
      管理工作日志
    </el-button>
  </div>
</template>

<script setup>
  import { useUserStore } from '@/store/modules/user'

  const userStore = useUserStore()
</script>
```

### 示例 3：文档权限验证

```python
def check_document_permission(document, current_user, action="view"):
    """检查用户对文档的权限"""

    # 1. 管理员拥有所有权限
    if current_user.role == 'admin':
        return True

    # 2. 文档所有者拥有所有权限
    if document.owner_id == current_user.id:
        return True

    # 3. 检查协作者权限
    collaborator = get_collaborator(document, current_user)
    if collaborator:
        if action == "view":
            return True
        elif action == "edit" and collaborator.role == "editor":
            return True

    # 4. 无权限
    return False
```

---

## ⚠️ 注意事项

### 1. **权限标识符命名规范**

- **菜单权限**：使用路由的 `name` 字段（PascalCase）
  - 例如：`ProjectManagement`, `TaskPool`
- **按钮权限**：使用"模块名\_操作"格式
  - 例如：`Project_btn_add`, `User_btn_delete`

### 2. **管理员角色特殊处理**

管理员角色无需在 `permissions` 中配置权限，代码中会自动判断：

```python
if current_user.role.lower() in ['admin', 'super', 'administrator']:
    # 管理员拥有所有权限
    return True
```

### 3. **隐藏页面的权限**

隐藏页面（如详情页）通常继承父菜单的权限：

- 用户拥有 `Articles` 权限 → 自动拥有 `ArticleDetail` 权限
- 用户拥有 `Project` 权限 → 自动拥有项目相关隐藏页面权限

### 4. **权限缓存**

- 用户权限在登录时加载
- 修改角色权限后，用户需要重新登录才能生效
- **建议**：重要权限修改后通知用户重新登录

### 5. **前后端权限一致性**

- 前端权限控制主要用于UI显示
- **必须**在后端API也做权限验证，防止绕过前端直接调用API

---

## 📚 相关文件

### 后端

- `backend/app/models/role.py` - 角色模型
- `backend/app/api/roles.py` - 角色管理API
- `backend/app/api/menu.py` - 菜单权限过滤
- `backend/app/utils/permissions.py` - 权限验证工具

### 前端

- `src/store/modules/user.ts` - 用户权限状态管理
- `src/router/index.ts` - 路由权限守卫
- `src/views/system/role/index.vue` - 角色管理页面

---

## 🎯 最佳实践

### 1. **最小权限原则**

给用户分配完成工作所需的最小权限集合。

### 2. **权限分组**

将相关的权限组合成角色，方便管理：

- 标注相关：`TaskPool`, `MyWorkspace`, `WorkLog`
- 审核相关：`TaskReview`, `TeamPerformance`
- 管理相关：`UserManagement`, `RoleManagement`

### 3. **定期审查**

定期审查用户权限，确保符合实际需求。

### 4. **权限文档**

维护权限矩阵文档，记录每个角色的权限范围。

---

**最后更新**: 2025-10-16  
**作者**: AI Assistant  
**版本**: v1.0（权限管理体系说明）
