# CreateDocumentDialog 组件

通用的创建文档对话框组件，支持协作文档、文章、工作日志等多种类型的文档创建。

## 功能特性

- ✅ 统一的 UI 设计和交互体验
- ✅ 支持多种文档类型配置
- ✅ 可配置的字段显示（优先级、角色、部门等）
- ✅ **协作角色筛选**：选择角色后自动添加该角色的所有成员
- ✅ 下拉菜单层级管理（z-index: 99999999）
- ✅ 标签折叠显示（collapse-tags）
- ✅ 表单验证
- ✅ 响应式布局

## Props

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| modelValue | boolean | false | 对话框显示状态（v-model） |
| title | string | '创建协作文档' | 对话框标题 |
| descriptionLabel | string | '文档描述' | 描述字段的标签 |
| collaboratorLabel | string | '协作者' | 协作者字段的标签 |
| documentType | string | '文档' | 文档类型（用于占位符） |
| submitButtonText | string | '创建并编辑' | 提交按钮文本 |
| showPriority | boolean | true | 是否显示优先级字段 |
| showRoles | boolean | false | 是否显示可编辑角色字段 |
| showDepartments | boolean | false | 是否显示所属部门字段 |
| availableTags | string[] | [] | 可用标签列表 |
| userOptions | Option[] | [] | 用户选项列表 |
| roleOptions | Option[] | [] | 角色选项列表 |
| deptOptions | Option[] | [] | 部门选项列表 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| update:modelValue | (value: boolean) | 对话框显示状态变化 |
| submit | (data: FormData) | 提交按钮点击，返回表单数据 |
| cancel | - | 取消按钮点击 |

## 暴露的方法

| 方法名 | 参数 | 说明 |
|--------|------|------|
| setSubmitting | (value: boolean) | 设置提交状态 |
| close | - | 关闭对话框 |

## 使用示例

### 1. 协作文档（含角色筛选）

```vue
<template>
  <CreateDocumentDialog
    v-model="createDialogVisible"
    title="创建协作文档"
    @submit="handleCreate"
    @cancel="handleCancel"
    :available-tags="availableTags"
    :user-options="userOptions"
    :role-options="roleOptions"
    ref="createDialogRef"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CreateDocumentDialog from '@/components/business/CreateDocumentDialog.vue'
import { collaborationApi } from '@/api/collaborationApi'

const createDialogVisible = ref(false)
const createDialogRef = ref()

const handleCreate = async (formData) => {
  createDialogRef.value?.setSubmitting(true)
  
  try {
    // 1. 创建文档
    const data = {
      title: formData.title.trim(),
      description: formData.description.trim(),
      content: '',
      status: 'draft',
      priority: formData.priority,
      tags: formData.tags
    }
    
    const result = await collaborationApi.createDocument(data)
    
    // 2. 添加协作者
    if (formData.editable_user_ids.length > 0) {
      for (const userId of formData.editable_user_ids) {
        await collaborationApi.addCollaborator(result.id, userId, 'editor')
      }
    }
    
    ElMessage.success('文档创建成功！')
    createDialogRef.value?.close()
    
    // 跳转到编辑页面
    router.push(`/articles/collaboration/edit/${result.id}`)
  } catch (error) {
    ElMessage.error('创建文档失败')
  } finally {
    createDialogRef.value?.setSubmitting(false)
  }
}

const handleCancel = () => {
  createDialogVisible.value = false
}
</script>
```

### 2. 协作文档（完整版 - 含角色和部门）

```vue
<template>
  <CreateDocumentDialog
    v-model="createDialogVisible"
    title="创建协作文档"
    description-label="文档描述"
    collaborator-label="协作者"
    document-type="文档"
    submit-button-text="创建并编辑"
    :show-priority="true"
    :show-roles="true"
    :show-departments="true"
    :available-tags="availableTags"
    :user-options="userOptions"
    :role-options="roleOptions"
    :dept-options="deptOptions"
    @submit="handleCreate"
    ref="createDialogRef"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CreateDocumentDialog from '@/components/business/CreateDocumentDialog.vue'

const createDialogVisible = ref(false)
const createDialogRef = ref()

const availableTags = ref(['重要', '紧急', '待办'])
const userOptions = ref([
  { label: '张三 (zhangsan)', value: 'user-1' },
  { label: '李四 (lisi)', value: 'user-2' }
])
const roleOptions = ref([
  { label: '标注员', value: 'annotator' },
  { label: '审核员', value: 'reviewer' }
])
const deptOptions = ref([
  { label: '研发部', value: '研发部' },
  { label: '产品部', value: '产品部' }
])

const handleCreate = async (formData) => {
  createDialogRef.value?.setSubmitting(true)
  
  try {
    const data = {
      ...formData,
      title: formData.title.trim(),
      description: formData.description.trim()
    }
    
    await api.createDocument(data)
    ElMessage.success('创建成功')
    createDialogRef.value?.close()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    createDialogRef.value?.setSubmitting(false)
  }
}
</script>
```

### 3. 文章创建

```vue
<template>
  <CreateDocumentDialog
    v-model="createDialogVisible"
    title="创建文章"
    description-label="文章摘要"
    collaborator-label="可编辑成员"
    document-type="文章"
    submit-button-text="创建文章"
    :show-priority="false"
    :show-roles="true"
    :show-departments="true"
    :available-tags="['技术', 'Vue', 'TypeScript']"
    :user-options="userOptions"
    :role-options="roleOptions"
    :dept-options="deptOptions"
    @submit="handleCreateArticle"
    ref="createDialogRef"
  />
</template>

<script setup lang="ts">
const handleCreateArticle = async (formData) => {
  createDialogRef.value?.setSubmitting(true)
  
  try {
    await articlesApi.create({
      title: formData.title,
      summary: formData.description,
      content: '',
      category: '未分类',
      tags: formData.tags,
      editable_roles: formData.editable_roles,
      editable_user_ids: formData.editable_user_ids,
      departments: formData.departments
    })
    
    ElMessage.success('文章创建成功')
    createDialogRef.value?.close()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    createDialogRef.value?.setSubmitting(false)
  }
}
</script>
```

### 4. 工作日志创建

```vue
<template>
  <CreateDocumentDialog
    v-model="createDialogVisible"
    title="创建工作日志"
    description-label="日志摘要"
    collaborator-label="可查看成员"
    document-type="日志"
    submit-button-text="创建日志"
    :show-priority="true"
    :show-roles="false"
    :show-departments="true"
    :available-tags="['日报', '周报', '月报']"
    :user-options="userOptions"
    :dept-options="deptOptions"
    @submit="handleCreateLog"
    ref="createDialogRef"
  />
</template>
```

## 协作角色筛选功能

### 工作原理

1. **选择协作角色**：用户首先选择一个或多个角色（如"标注员"、"审核员"）
2. **自动筛选成员**：系统自动筛选出属于这些角色的所有用户
3. **自动选择**：自动将筛选出的用户添加到协作者列表
4. **手动调整**：用户可以在自动选择的基础上手动添加或移除协作者

### 使用示例

```vue
<template>
  <CreateDocumentDialog
    v-model="createDialogVisible"
    :user-options="userOptions"
    :role-options="roleOptions"
    @submit="handleCreate"
    ref="createDialogRef"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 用户选项必须包含 role 字段
const userOptions = ref([
  { label: '张三 (zhangsan)', value: 'user-1', role: 'annotator' },
  { label: '李四 (lisi)', value: 'user-2', role: 'annotator' },
  { label: '王五 (wangwu)', value: 'user-3', role: 'reviewer' }
])

const roleOptions = ref([
  { label: '标注员', value: 'annotator' },
  { label: '审核员', value: 'reviewer' }
])

// 当用户选择"标注员"角色时，张三和李四会被自动添加到协作者列表
</script>
```

### 视觉提示

- **未选择角色**：显示黄色提示框 "💡 请先选择协作角色，系统将自动添加该角色的所有成员"
- **已选择角色**：显示蓝色提示框 "✅ 已自动选择 N 位成员（可手动调整）"
- **协作者下拉框**：在未选择角色时禁用，选择角色后启用

## 数据结构

### FormData

```typescript
interface FormData {
  title: string                    // 标题（必填）
  description: string              // 描述
  priority?: 'low' | 'normal' | 'high' | 'urgent'  // 优先级
  tags: string[]                   // 标签
  collaborator_roles?: string[]    // 协作角色（用于筛选）
  editable_roles?: string[]        // 可编辑角色（用于权限控制）
  editable_user_ids: string[]      // 可编辑成员ID
  departments?: string[]           // 所属部门
}
```

### UserOption

```typescript
interface UserOption {
  label: string    // 显示名称
  value: string    // 用户ID
  role?: string    // 用户角色（必需，用于筛选）
}
```

## 表单验证

组件内置了以下验证规则：

- **标题**：必填，长度 2-100 个字符
- **描述**：可选，最多 500 个字符

如需自定义验证，请在父组件的 `submit` 事件中处理。

## 样式定制

组件使用了 scoped 样式，如需自定义样式，可以通过以下方式：

```vue
<style>
/* 自定义对话框样式 */
.create-document-dialog {
  /* 你的自定义样式 */
}
</style>
```

## 注意事项

1. **z-index 管理**：组件内部使用了 `ElConfigProvider` 设置 z-index 为 10000100，确保下拉菜单在对话框之上。

2. **标签折叠**：所有多选下拉框都启用了 `collapse-tags`，最多显示 2 个标签，其余折叠为 "+N"。

3. **表单重置**：对话框关闭后会自动重置表单数据。

4. **提交状态**：使用 `ref` 获取组件实例，调用 `setSubmitting(true/false)` 来控制提交按钮的 loading 状态。

5. **关闭对话框**：可以通过 `close()` 方法手动关闭对话框，或者设置 `v-model` 为 `false`。

## 与旧组件的区别

### 旧组件（`src/views/collaboration/components/CreateDocumentDialog.vue`）

- ❌ 只适用于协作文档
- ❌ 硬编码了业务逻辑（创建文档 + 添加协作者）
- ❌ 下拉菜单可能被遮挡
- ❌ 没有标签折叠

### 新组件（`src/components/business/CreateDocumentDialog.vue`）

- ✅ 通用组件，适用于多种文档类型
- ✅ 只负责表单展示和验证，业务逻辑由父组件处理
- ✅ 完美的 z-index 管理
- ✅ 标签折叠显示
- ✅ 更好的可配置性

## 迁移指南

### 从旧的创建对话框迁移

1. **导入新组件**：
```typescript
import CreateDocumentDialog from '@/components/business/CreateDocumentDialog.vue'
```

2. **替换模板**：
```vue
<!-- 旧的 -->
<CreateDocumentDialog v-model="visible" @success="handleSuccess" />

<!-- 新的 -->
<CreateDocumentDialog
  v-model="visible"
  @submit="handleCreate"
  ref="dialogRef"
/>
```

3. **更新业务逻辑**：
```typescript
// 旧的（业务逻辑在组件内部）
const handleSuccess = (documentId) => {
  router.push(`/edit/${documentId}`)
}

// 新的（业务逻辑在父组件）
const handleCreate = async (formData) => {
  dialogRef.value?.setSubmitting(true)
  try {
    const result = await api.create(formData)
    dialogRef.value?.close()
    router.push(`/edit/${result.id}`)
  } finally {
    dialogRef.value?.setSubmitting(false)
  }
}
```

## 相关组件

- `ArticleMetaDialog` - 编辑文档信息对话框
- `ArtTextbusEditor` - 富文本编辑器

