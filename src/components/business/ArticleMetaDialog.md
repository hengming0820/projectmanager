# ArticleMetaDialog 组件

通用的文章/文档信息编辑对话框组件，支持协作文档、会议记录、模型测试、工作日志等多种类型的元数据编辑。

## 功能特性

- ✅ 统一的 UI 设计和交互体验
- ✅ 支持多种文档类型（协作文档、文章、工作日志等）
- ✅ 可配置的字段显示（封面、分类、状态、优先级等）
- ✅ 下拉菜单层级管理（z-index: 99999999）
- ✅ 标签折叠显示（collapse-tags）
- ✅ 响应式布局
- ✅ 表单验证

## Props

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| modelValue | boolean | false | 对话框显示状态（v-model） |
| data | MetaFormData | - | 表单数据 |
| title | string | '编辑信息' | 对话框标题 |
| subtitle | string | '修改文档的标题、描述、状态等元数据' | 对话框副标题 |
| descriptionLabel | string | '描述' | 描述字段的标签 |
| showCover | boolean | false | 是否显示封面上传 |
| showCategory | boolean | false | 是否显示分类字段 |
| showStatus | boolean | true | 是否显示状态字段 |
| showPriority | boolean | true | 是否显示优先级字段 |
| showVisibility | boolean | false | 是否显示可见性开关 |
| statusOptions | StatusOption[] | 默认状态选项 | 状态选项列表 |
| availableTags | string[] | [] | 可用标签列表 |
| userOptions | Option[] | [] | 用户选项列表 |
| roleOptions | Option[] | [] | 角色选项列表 |
| deptOptions | Option[] | [] | 部门选项列表 |
| uploadUrl | string | '' | 封面上传地址 |
| uploadHeaders | object | {} | 封面上传请求头 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| update:modelValue | (value: boolean) | 对话框显示状态变化 |
| save | (data: MetaFormData) | 保存按钮点击 |
| cancel | - | 取消按钮点击 |

## 暴露的方法

| 方法名 | 参数 | 说明 |
|--------|------|------|
| setSaving | (value: boolean) | 设置保存状态 |

## 使用示例

### 1. 协作文档（Collaboration）

```vue
<template>
  <ArticleMetaDialog
    v-model="showMetaDialog"
    :data="metaForm"
    title="编辑文档信息"
    subtitle="修改文档的标题、描述、状态等元数据"
    description-label="描述"
    :show-cover="false"
    :show-category="false"
    :show-status="true"
    :show-priority="true"
    :show-visibility="false"
    :available-tags="availableTags"
    :user-options="userOptions"
    :role-options="roleOptions"
    :dept-options="deptOptions"
    @save="handleSave"
    @cancel="handleCancel"
    ref="metaDialogRef"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ArticleMetaDialog from '@/components/business/ArticleMetaDialog.vue'

const showMetaDialog = ref(false)
const metaDialogRef = ref()

const metaForm = ref({
  title: '协作文档标题',
  description: '文档描述',
  status: 'active',
  priority: 'normal',
  tags: ['标签1', '标签2'],
  editable_roles: ['annotator'],
  editable_user_ids: ['user-id-1'],
  departments: ['研发部']
})

const handleSave = async (data) => {
  metaDialogRef.value?.setSaving(true)
  try {
    await collaborationApi.updateDocument(currentDocument.value.id, data)
    ElMessage.success('保存成功')
    showMetaDialog.value = false
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    metaDialogRef.value?.setSaving(false)
  }
}

const handleCancel = () => {
  showMetaDialog.value = false
}
</script>
```

### 2. 文章（Articles）

```vue
<template>
  <ArticleMetaDialog
    v-model="showMetaDialog"
    :data="metaForm"
    title="编辑文章信息"
    subtitle="修改文章的标题、摘要、封面等信息"
    description-label="摘要"
    :show-cover="true"
    :show-category="true"
    :show-status="false"
    :show-priority="false"
    :show-visibility="true"
    :upload-url="uploadUrl"
    :upload-headers="uploadHeaders"
    :available-tags="availableTags"
    :user-options="userOptions"
    :role-options="roleOptions"
    :dept-options="deptOptions"
    @save="handleSave"
    @cancel="handleCancel"
    ref="metaDialogRef"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ArticleMetaDialog from '@/components/business/ArticleMetaDialog.vue'

const showMetaDialog = ref(false)
const metaDialogRef = ref()

const metaForm = ref({
  title: '文章标题',
  summary: '文章摘要',
  cover_url: 'https://example.com/cover.jpg',
  category: '技术',
  is_public: true,
  tags: ['Vue', 'TypeScript'],
  editable_roles: ['annotator'],
  editable_user_ids: ['user-id-1'],
  departments: ['研发部']
})

const uploadUrl = computed(() => `${import.meta.env.VITE_API_BASE_URL}/upload/image`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const handleSave = async (data) => {
  metaDialogRef.value?.setSaving(true)
  try {
    await articlesApi.update(article.value.id, data)
    ElMessage.success('保存成功')
    showMetaDialog.value = false
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    metaDialogRef.value?.setSaving(false)
  }
}
</script>
```

### 3. 自定义状态选项

```vue
<template>
  <ArticleMetaDialog
    v-model="showMetaDialog"
    :data="metaForm"
    :status-options="customStatusOptions"
    @save="handleSave"
  />
</template>

<script setup lang="ts">
const customStatusOptions = [
  { label: '🆕 新建', value: 'new', emoji: '🆕', text: '新建' },
  { label: '🔄 处理中', value: 'processing', emoji: '🔄', text: '处理中' },
  { label: '✅ 完成', value: 'done', emoji: '✅', text: '完成' },
  { label: '❌ 取消', value: 'cancelled', emoji: '❌', text: '取消' }
]
</script>
```

## 数据结构

### MetaFormData

```typescript
interface MetaFormData {
  title: string                    // 标题（必填）
  description?: string             // 描述
  summary?: string                 // 摘要
  cover_url?: string              // 封面URL
  category?: string               // 分类
  status?: string                 // 状态
  priority?: string               // 优先级
  is_public?: boolean             // 是否公开
  tags?: string[]                 // 标签
  editable_roles?: string[]       // 可编辑角色
  editable_user_ids?: string[]    // 可编辑成员ID
  departments?: string[]          // 所属部门
}
```

### StatusOption

```typescript
interface StatusOption {
  label: string    // 显示标签（含emoji）
  value: string    // 值
  emoji: string    // emoji图标
  text: string     // 纯文本
}
```

## 样式定制

组件使用了 scoped 样式，如需自定义样式，可以通过以下方式：

```vue
<style>
/* 自定义对话框样式 */
.article-meta-dialog {
  /* 你的自定义样式 */
}

/* 自定义表单样式 */
.article-meta-dialog .meta-form {
  /* 你的自定义样式 */
}
</style>
```

## 注意事项

1. **z-index 管理**：组件内部使用了 `ElConfigProvider` 设置 z-index 为 10000100，确保下拉菜单在对话框之上。

2. **标签折叠**：所有多选下拉框都启用了 `collapse-tags`，最多显示 2 个标签，其余折叠为 "+N"。

3. **表单验证**：组件内部只做了基础的标题非空验证，如需更复杂的验证，请在父组件的 `save` 事件中处理。

4. **保存状态**：使用 `ref` 获取组件实例，调用 `setSaving(true/false)` 来控制保存按钮的 loading 状态。

5. **封面上传**：需要提供 `uploadUrl` 和 `uploadHeaders`，上传成功后会自动更新 `cover_url`。

## 迁移指南

### 从旧的编辑对话框迁移

1. **导入组件**：
```typescript
import ArticleMetaDialog from '@/components/business/ArticleMetaDialog.vue'
```

2. **替换模板**：
```vue
<!-- 旧的 -->
<el-dialog v-model="showMetaDialog">
  <el-form>...</el-form>
</el-dialog>

<!-- 新的 -->
<ArticleMetaDialog
  v-model="showMetaDialog"
  :data="metaForm"
  @save="handleSave"
  ref="metaDialogRef"
/>
```

3. **更新保存逻辑**：
```typescript
// 旧的
const saveMeta = async () => {
  saving.value = true
  try {
    await api.update(data)
  } finally {
    saving.value = false
  }
}

// 新的
const handleSave = async (data) => {
  metaDialogRef.value?.setSaving(true)
  try {
    await api.update(data)
    showMetaDialog.value = false
  } finally {
    metaDialogRef.value?.setSaving(false)
  }
}
```

## 相关组件

- `ArtTextbusEditor` - 富文本编辑器
- `ArtXnotePreview` - 文档预览组件

