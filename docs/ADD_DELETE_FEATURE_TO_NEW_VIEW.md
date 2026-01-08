# 为新版项目管理页面添加删除功能

## ✅ 完成的修改

### 1. **ProjectDetailView.vue** - 添加删除按钮和功能

#### 修改位置

**文件：** `src/views/project/management/components/ProjectDetailView.vue`

#### 添加的内容

1. **导入依赖** (第 254-258 行)

```typescript
import { useRouter } from 'vue-router'
import { Delete } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/modules/user'
```

2. **添加删除按钮** (第 17-20 行)

```vue
<el-button v-if="canDeleteProject" type="danger" size="small" @click="handleDelete">
  <el-icon><Delete /></el-icon>
  删除项目
</el-button>
```

3. **权限检查** (第 289-293 行)

```typescript
// 权限检查：是否可以删除项目
const canDeleteProject = computed(() => {
  const role = userStore.currentUser?.role || ''
  return ['admin', 'super'].includes(role.toLowerCase())
})
```

4. **删除处理函数** (第 738-783 行)

```typescript
// 删除项目
const handleDelete = async () => {
  if (!props.project) {
    ElMessage.error('项目信息不存在')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${props.project.name}"吗？
      
⚠️ 警告：此操作将会：
• 删除该项目下的所有任务
• 删除相关的标注数据
• 此操作不可恢复

请确认是否继续？`,
      '确认删除项目',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error',
        dangerouslyUseHTMLString: true
      }
    )

    loading.value = true
    await projectStore.deleteProject(props.project.id)

    ElMessage.success('项目删除成功')

    // 通知父组件刷新项目列表
    emit('deleted')
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除项目失败:', error)
      ElMessage.error('删除项目失败')
    }
  } finally {
    loading.value = false
  }
}
```

5. **添加 deleted 事件** (第 274-277 行)

```typescript
const emit = defineEmits<{
  refresh: []
  deleted: [] // 新增
}>()
```

---

### 2. **index-new.vue** - 处理删除事件

#### 修改位置

**文件：** `src/views/project/management/index-new.vue`

#### 添加的内容

1. **监听 deleted 事件** (第 123 行)

```vue
<ProjectDetailView
  :project="currentSelection.project"
  @refresh="loadProjects"
  @deleted="handleProjectDeleted"
/>
```

2. **删除处理函数** (第 594-600 行)

```typescript
// 项目删除成功
const handleProjectDeleted = () => {
  // 清空当前选中
  currentSelection.value = null
  // 重新加载项目列表
  loadProjects()
}
```

---

## 🎯 功能特点

### 1. **权限控制**

- ✅ 只有 `admin` 和 `super` 角色可以看到删除按钮
- ✅ 其他角色（如 reviewer、annotator）看不到删除按钮
- ✅ 后端也有权限验证（`ProjectManagement` 权限）

### 2. **二次确认**

- ✅ 点击删除按钮会弹出确认对话框
- ✅ 显示详细的警告信息
- ✅ 说明删除的影响（删除所有任务、标注数据）
- ✅ 明确标注"不可恢复"

### 3. **用户体验**

- ✅ 删除成功后自动刷新项目列表
- ✅ 删除成功后清空当前选中，返回欢迎页面
- ✅ 显示加载状态（loading）
- ✅ 显示成功/失败提示消息

### 4. **级联删除**

- ✅ 删除项目时会自动删除该项目下的所有任务
- ✅ 后端配置了级联删除（cascade="all, delete-orphan"）
- ✅ 确保数据一致性

---

## 📍 删除按钮位置

### 在项目详情页面

```
项目信息卡片
├── 标题：📊 项目信息
└── 操作按钮（右上角）
    ├── 导出报告
    ├── 编辑项目
    └── 删除项目 ✅ （仅管理员可见，红色按钮）
```

---

## 🔍 使用流程

### 1. 查看项目详情

1. 登录系统（使用 admin 或 super 账号）
2. 进入"项目管理"页面
3. 点击左侧项目列表中的项目
4. 展开后点击"项目详情"

### 2. 删除项目

1. 在项目详情页面，点击右上角的"删除项目"按钮（红色）
2. 阅读警告信息
3. 点击"确定删除"
4. 等待删除完成
5. 自动返回项目列表

---

## ⚠️ 注意事项

### 1. **权限要求**

- 必须是 `admin` 或 `super` 角色
- 其他角色看不到删除按钮
- 后端会验证权限，无权限会返回 403

### 2. **删除影响**

- ❌ **不可恢复** - 删除后无法从系统恢复
- ✅ 会删除项目下的所有任务
- ✅ 会删除项目统计信息
- ⚠️ 可能会删除任务的附件和标注数据

### 3. **数据备份**

建议在删除重要项目前：

- 导出项目报告（点击"导出报告"按钮）
- 备份数据库
- 确认项目确实不再需要

---

## 🧪 测试步骤

### 测试 1：管理员可以看到删除按钮

1. 以 `admin` 身份登录
2. 进入"项目管理"
3. 选择一个项目查看详情
4. ✅ 确认右上角有"删除项目"按钮

### 测试 2：非管理员看不到删除按钮

1. 以 `reviewer` 或 `annotator` 身份登录
2. 进入"项目管理"
3. 选择一个项目查看详情
4. ✅ 确认右上角**没有**"删除项目"按钮

### 测试 3：删除功能正常工作

1. 以 `admin` 身份登录
2. 创建一个测试项目
3. 查看该项目详情
4. 点击"删除项目"
5. ✅ 弹出确认对话框
6. 点击"确定删除"
7. ✅ 显示"项目删除成功"
8. ✅ 自动返回项目列表
9. ✅ 项目从列表中消失

### 测试 4：取消删除

1. 点击"删除项目"
2. 在确认对话框中点击"取消"
3. ✅ 对话框关闭
4. ✅ 项目未被删除

---

## 🔄 与旧版页面的对比

| 特性         | index.vue (旧版) | index-new.vue (新版) |
| ------------ | ---------------- | -------------------- |
| 删除按钮位置 | 表格操作列       | 项目详情页右上角     |
| 权限控制     | ❌ 无前端控制    | ✅ 有前端控制        |
| 删除后行为   | 刷新表格         | 清空选中 + 刷新列表  |
| UI 风格      | 表格文字按钮     | 卡片头部按钮         |
| 页面布局     | 单页表格         | 左右分栏             |

---

## 📚 相关文件

### 前端文件

- `src/views/project/management/index-new.vue` - 主页面
- `src/views/project/management/components/ProjectDetailView.vue` - 项目详情组件
- `src/store/modules/project.ts` - 项目 Store（包含 deleteProject 方法）
- `src/api/projectApi.ts` - 项目 API（包含 deleteProject 接口）

### 后端文件

- `backend/app/api/projects.py` - 删除项目 API（第 172-185 行）
- `backend/app/models/project.py` - 项目模型（级联删除配置）

---

## 🎨 UI 预览

### 删除按钮样式

```
┌─────────────────────────────────────────────┐
│ 📊 项目信息        [导出报告] [编辑项目] [删除项目] │
│                                  (蓝色)  (红色) │
├─────────────────────────────────────────────┤
│ 项目名称： XXX项目                           │
│ 项目状态： 进行中                            │
│ ...                                         │
└─────────────────────────────────────────────┘
```

### 确认对话框

```
┌─────────────────────────────────────────┐
│ 确认删除项目                     ⚠️     │
├─────────────────────────────────────────┤
│ 确定要删除项目"XXX项目"吗？              │
│                                         │
│ ⚠️ 警告：此操作将会：                    │
│ • 删除该项目下的所有任务                 │
│ • 删除相关的标注数据                    │
│ • 此操作不可恢复                        │
│                                         │
│ 请确认是否继续？                        │
│                                         │
│         [取消]     [确定删除]            │
└─────────────────────────────────────────┘
```

---

## ✅ 总结

**删除功能已成功添加到新版项目管理页面！**

- ✅ 功能完整（权限控制、二次确认、级联删除）
- ✅ 用户体验良好（自动刷新、清空选中）
- ✅ 安全可靠（仅管理员可见、后端权限验证）
- ✅ 与旧版功能一致（共用相同的 API）

**现在 `index-new.vue` 也支持删除项目了！** 🎉
