# 项目删除功能说明

## ✅ 当前状态

**好消息：项目删除功能是存在的！**

前端和后端都已经实现了项目删除功能。

---

## 📍 功能位置

### 前端（项目管理页面）

**文件：** `src/views/project/management/index.vue`

**位置：** 第 163-170 行

**访问路径：**

```
菜单: 项目管理 → 项目列表 → 操作列
```

**删除按钮代码：**

```vue
<el-button type="danger" size="small" text @click="deleteProject(row)">
  删除
</el-button>
```

**删除处理函数：** 第 580-607 行

```typescript
const deleteProject = async (project: Project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${project.name}"吗？
      
⚠️ 警告：此操作将会：
• 删除该项目下的所有任务
• 删除相关的标注数据
• 此操作不可恢复

请确认是否继续？`,
      '确认删除项目',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )

    await projectStore.deleteProject(project.id)
    ElMessage.success('删除成功')
    refreshAllData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
```

---

### 后端 API

**文件：** `backend/app/api/projects.py`

**位置：** 第 172-185 行

**API 端点：** `DELETE /api/projects/{project_id}`

**权限要求：** `ProjectManagement`（需要管理员权限）

```python
@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("ProjectManagement"))
):
    """删除项目（仅管理员）"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    db.delete(project)
    db.commit()
    return {"message": "项目删除成功"}
```

---

## 🔍 查看删除按钮

### 方法 1：直接访问项目管理页面

1. 登录系统
2. 点击左侧菜单 **"项目管理"**
3. 在项目列表的 **"操作"** 列中
4. 查看最右侧的 **"删除"** 按钮（红色文字按钮）

### 方法 2：检查权限

删除按钮目前**没有权限控制**（任何能访问项目管理页面的用户都能看到删除按钮）

但后端 API 有权限控制：

- ✅ **Admin** - 可以删除
- ❌ **Reviewer** - 默认没有 `ProjectManagement` 权限，无法删除
- ❌ **Annotator** - 没有权限，无法删除

---

## ⚠️ 可能遇到的问题

### 问题 1：看到删除按钮但点击后报 403

**原因：** 前端没有权限控制，但后端有

**解决方案：** 添加前端权限控制

### 问题 2：找不到删除按钮

**可能原因：**

1. 没有访问项目管理页面（而是访问了其他页面）
2. 按钮被遮挡或滚动到视野外
3. 浏览器缓存问题

---

## 🔧 改进建议：添加前端权限控制

目前删除按钮对所有用户可见，但只有管理员有权限执行删除。建议添加前端权限控制，让没有权限的用户看不到删除按钮。

### 修改方案

**文件：** `src/views/project/management/index.vue`

#### 步骤 1：添加权限检查

在 `<script setup>` 部分添加：

```typescript
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()

// 检查是否有项目管理权限
const canManageProject = computed(() => {
  const role = userStore.currentUser?.role || ''
  return ['admin', 'super'].includes(role.toLowerCase())
})
```

#### 步骤 2：修改删除按钮

**修改前：** 第 163-170 行

```vue
<el-button type="danger" size="small" text @click="deleteProject(row)">
  删除
</el-button>
```

**修改后：** ✅

```vue
<el-button v-if="canManageProject" type="danger" size="small" text @click="deleteProject(row)">
  删除
</el-button>
```

#### 步骤 3：同样修改编辑按钮（可选）

```vue
<el-button v-if="canManageProject" type="warning" size="small" text @click="editProject(row)">
  编辑
</el-button>
```

#### 步骤 4：同样修改新建按钮（可选）

第 16-19 行：

```vue
<el-button v-if="canManageProject" type="primary" @click="showCreateDialog = true">
  <el-icon><Plus /></el-icon>
  新建项目
</el-button>
```

---

## 🗑️ 删除功能的级联删除

### 当前删除策略

根据后端模型配置，删除项目时会**自动级联删除**：

**文件：** `backend/app/models/project.py`

```python
class Project(Base):
    # ... 其他字段 ...

    # 级联删除配置
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    stats = relationship("ProjectStats", back_populates="project", uselist=False, cascade="all, delete-orphan")
```

**会被自动删除的数据：**

- ✅ 项目下的所有任务（`Task`）
- ✅ 项目统计信息（`ProjectStats`）
- ⚠️ **可能不会删除：** 任务的附件、标注数据（取决于配置）

### 数据库级联删除配置

**文件：** `backend/migrations/add_article_cascade_delete.sql`

该迁移脚本配置了级联删除规则，确保删除项目时相关数据也被清理。

---

## 📊 权限配置表

### 当前权限配置

| 操作         | 前端控制  | 后端控制 | Admin | Reviewer | Annotator |
| ------------ | --------- | -------- | ----- | -------- | --------- |
| 查看项目列表 | ✅        | ✅       | ✅    | ✅       | ✅        |
| 新建项目     | ❌ 无控制 | ✅       | ✅    | ❌       | ❌        |
| 编辑项目     | ❌ 无控制 | ✅       | ✅    | ❌       | ❌        |
| 删除项目     | ❌ 无控制 | ✅       | ✅    | ❌       | ❌        |
| 查看项目详情 | ❌ 无控制 | ✅       | ✅    | ✅       | ✅        |

### 建议的权限配置

| 操作         | 前端控制                     | 后端控制 | Admin | Reviewer | Annotator |
| ------------ | ---------------------------- | -------- | ----- | -------- | --------- |
| 查看项目列表 | ✅                           | ✅       | ✅    | ✅       | ✅        |
| 新建项目     | ✅ `v-if="canManageProject"` | ✅       | ✅    | ❌       | ❌        |
| 编辑项目     | ✅ `v-if="canManageProject"` | ✅       | ✅    | ❌       | ❌        |
| 删除项目     | ✅ `v-if="canManageProject"` | ✅       | ✅    | ❌       | ❌        |
| 查看项目详情 | ❌ 无控制                    | ✅       | ✅    | ✅       | ✅        |

---

## 🧪 测试删除功能

### 测试步骤

1. **以管理员身份登录**
2. **进入项目管理页面**
   ```
   菜单: 项目管理
   ```
3. **找到要删除的项目**
4. **点击"删除"按钮**
5. **确认删除对话框**
   - 会显示警告信息
   - 说明会删除项目下的所有任务和数据
6. **点击"确定删除"**
7. **验证删除结果**
   - 项目从列表中消失
   - 提示"删除成功"

### 测试 API（可选）

```bash
# 获取管理员 token
TOKEN="your-admin-token"

# 测试删除项目
curl -X DELETE http://localhost:8000/api/projects/{project_id} \
  -H "Authorization: Bearer $TOKEN"

# 成功返回：
# {"message": "项目删除成功"}

# 如果无权限，返回：
# {"detail": "权限不足，缺少访问权限: ProjectManagement"}
```

---

## ❓ 常见问题

### Q1: 为什么我看不到删除按钮？

**A:** 可能的原因：

1. 你访问的不是"项目管理"页面（可能是"项目看板"或其他页面）
2. 操作列被遮挡或需要横向滚动
3. 浏览器缓存问题，尝试刷新（Ctrl+F5）

### Q2: 我看到删除按钮，但点击后提示权限不足？

**A:**

- 你的账号没有 `ProjectManagement` 权限
- 只有 `admin` 和 `super` 角色有权限删除项目
- 建议添加前端权限控制（参考上面的改进方案）

### Q3: 删除项目会删除什么数据？

**A:** 会级联删除：

- ✅ 项目下的所有任务
- ✅ 项目统计信息
- ⚠️ 任务的附件和标注数据（取决于配置）
- ⚠️ 此操作**不可恢复**

### Q4: 如何恢复误删除的项目？

**A:**

- ❌ 前端和后端都**没有软删除机制**
- ❌ 删除后无法从系统中恢复
- ✅ 只能从数据库备份中恢复
- 建议：实施软删除（添加 `deleted_at` 字段）

### Q5: 可以批量删除项目吗？

**A:**

- ❌ 当前没有批量删除功能
- ✅ 可以参考"批量删除任务"的实现来添加

---

## 🔒 安全建议

### 1. 实施软删除

**当前问题：** 硬删除，数据无法恢复

**建议：** 添加软删除机制

```python
# backend/app/models/project.py
class Project(Base):
    # ... 其他字段 ...
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String(36), ForeignKey('users.id'), nullable=True)
```

```python
# 删除项目改为软删除
@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("ProjectManagement"))
):
    """删除项目（软删除）"""
    from app.utils.datetime_utils import utc_now

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 软删除
    project.deleted_at = utc_now()
    project.deleted_by = current_user.id

    db.commit()
    return {"message": "项目删除成功"}
```

### 2. 添加删除日志

记录谁在什么时间删除了什么项目

```python
# 记录操作日志
logger.info(f"🗑️ [ProjectAPI] 用户 {current_user.username} 删除了项目 {project.name} (ID: {project.id})")
```

### 3. 二次确认

前端已经实施了二次确认，显示警告信息

### 4. 限制删除条件

例如：

- 有未完成任务的项目不能删除
- 有关联数据的项目不能删除
- 需要输入项目名称才能删除

---

## 📝 快速修改代码（添加前端权限控制）

### 完整修改代码

**文件：** `src/views/project/management/index.vue`

**在 `<script setup>` 顶部添加：**

```typescript
// 在导入部分添加
import { useUserStore } from '@/store/modules/user'

// 在变量声明部分添加
const userStore = useUserStore()

// 添加权限检查
const canManageProject = computed(() => {
  const role = userStore.currentUser?.role || ''
  return ['admin', 'super'].includes(role.toLowerCase())
})
```

**修改操作列（第 145-172 行）：**

```vue
<el-table-column label="操作" width="200" fixed="right">
  <template #default="{ row }">
    <el-button 
      type="primary" 
      size="small" 
      text
      @click="viewProject(row)"
    >
      查看
    </el-button>
    <el-button 
      v-if="canManageProject"
      type="warning" 
      size="small" 
      text
      @click="editProject(row)"
    >
      编辑
    </el-button>
    <el-button 
      v-if="canManageProject"
      type="danger" 
      size="small" 
      text
      @click="deleteProject(row)"
    >
      删除
    </el-button>
  </template>
</el-table-column>
```

---

## ✅ 总结

- ✅ **项目删除功能存在**（前端+后端）
- ✅ **后端有权限控制**（仅管理员）
- ⚠️ **前端缺少权限控制**（建议添加）
- ⚠️ **硬删除，不可恢复**（建议改为软删除）
- ✅ **有级联删除配置**（自动删除关联数据）
- ✅ **有二次确认机制**（防止误删除）

---

**功能是完整的，建议添加前端权限控制以提升用户体验！** 🎯
