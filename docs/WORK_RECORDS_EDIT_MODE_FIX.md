# 工作记录编辑模式修复文档

## 🐛 问题描述

用户反馈点击"编辑"按钮后，跳转到了一个老版本的独立文章详情页面，与会议记录等其他文章页面的编辑方式完全不一致。

### 问题截图分析

- 老页面有独立的导航树和复杂的工具栏
- 样式与会议记录页面不一致
- 跳转到另一个路由，破坏了用户体验

## ✅ 修复方案

采用与会议记录完全一致的**页内编辑模式**，在同一页面内切换查看/编辑状态。

## 📝 核心修改

### 1. 添加编辑状态管理

```typescript
// 编辑模式相关
const isEditing = ref(false)
const saving = ref(false)
const editForm = ref({
  content: ''
})

// Markdown 导入相关
const showMdDialog = ref(false)
const mdFileName = ref('')
```

### 2. 添加编辑相关函数

#### 开始编辑（加锁）

```typescript
const startEdit = async () => {
  if (!currentArticle.value) return

  // 刷新文章状态，检查锁定
  await loadArticles()
  const refreshedArticle = articles.value.find((a) => a.id === currentArticle.value!.id)
  if (refreshedArticle) {
    currentArticle.value = refreshedArticle
  }

  try {
    // 锁定文章，防止多人同时编辑
    await articlesApi.lock(currentArticle.value.id)
    editForm.value = {
      content: currentArticle.value.content
    }
    isEditing.value = true
  } catch (error: any) {
    ElMessage.error('无法开始编辑，请稍后重试')
  }
}
```

#### 保存编辑（解锁）

```typescript
const saveEdit = async () => {
  if (!currentArticle.value || !editForm.value.content.trim()) {
    ElMessage.warning('内容不能为空')
    return
  }

  try {
    saving.value = true

    // 更新内容
    await articlesApi.update(currentArticle.value.id, {
      content: editForm.value.content,
      title: currentArticle.value.title,
      summary: currentArticle.value.summary,
      category: currentArticle.value.category,
      tags: currentArticle.value.tags,
      type: 'work_record'
    })

    // 解锁文章
    await articlesApi.unlock(currentArticle.value.id)

    ElMessage.success('工作记录内容更新成功')
    isEditing.value = false
    await loadArticles()
    currentArticle.value = articles.value.find((a) => a.id === currentArticle.value!.id) || null
  } catch (error) {
    ElMessage.error('保存工作记录失败')
  } finally {
    saving.value = false
  }
}
```

#### 取消编辑（解锁）

```typescript
const cancelEdit = async () => {
  if (!currentArticle.value) return

  try {
    await articlesApi.unlock(currentArticle.value.id)
  } catch (error) {
    console.error('解锁文章失败:', error)
  }

  isEditing.value = false
  editForm.value = { content: '' }
  await loadArticles()
  currentArticle.value = articles.value.find((a) => a.id === currentArticle.value!.id) || null
}
```

#### Markdown 导入

```typescript
const openImportMarkdown = () => {
  showMdDialog.value = true
  mdFileName.value = ''
}

const onMdSelected = async (file: any) => {
  if (!file || !file.raw) return

  const validationError = validateMarkdownFile(file.raw)
  if (validationError) {
    ElMessage.error(validationError)
    return
  }

  mdFileName.value = file.name

  try {
    const content = await readMarkdownFile(file.raw)
    const html = markdownToHtml(content)
    editForm.value.content = html
    showMdDialog.value = false
    ElMessage.success('Markdown 导入成功')
  } catch (error) {
    ElMessage.error('Markdown 导入失败')
  }
}
```

### 3. 修改模板 - 按钮区域

#### 查看模式按钮

```vue
<template v-if="!isEditing">
  <el-button v-if="canEditArticle(currentArticle)" @click="startEdit">
    <el-icon><Document /></el-icon>
    编辑内容
  </el-button>
  <el-button
    v-if="canDeleteArticle(currentArticle)"
    @click="handleDeleteArticle(currentArticle.id)"
    type="danger"
  >
    <el-icon><Delete /></el-icon>
    删除
  </el-button>
</template>
```

#### 编辑模式按钮

```vue
<template v-else>
  <el-button @click="openImportMarkdown">
    <el-icon><Upload /></el-icon>
    导入 Markdown
  </el-button>
  <el-button @click="cancelEdit">取消</el-button>
  <el-button type="primary" @click="saveEdit" :loading="saving">保存内容</el-button>
</template>
```

### 4. 修改模板 - 内容区域

```vue
<div class="article-content">
  <!-- 查看模式 -->
  <template v-if="!isEditing">
    <div class="content-html" v-html="currentArticle.content"></div>
  </template>

  <!-- 编辑模式 -->
  <template v-else>
    <div class="content-editor" :class="{ 'editing-active': isEditing }">
      <ArtWangEditor v-model="editForm.content" height="100%" />
    </div>
  </template>
</div>
```

### 5. 添加 Markdown 导入对话框

```vue
<!-- 导入 Markdown 对话框 -->
<el-dialog v-model="showMdDialog" title="导入 Markdown 文档" width="520px">
  <p style="color:#6b7280;margin-bottom:12px">选择一个 .md/.markdown 文件，第一行作为标题，其余内容将转换为正文。</p>
  <p style="margin-bottom:12px; font-size:13px; color:#6b7280">已选文件: <strong>{{ mdFileName || '未选择' }}</strong></p>
  <el-upload
    :auto-upload="false"
    :show-file-list="false"
    accept=".md,.markdown,text/markdown,text/plain"
    :on-change="onMdSelected"
  >
    <el-button type="primary">选择 Markdown 文件</el-button>
  </el-upload>
</el-dialog>
```

### 6. 优化样式 - 支持编辑器

```scss
.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--art-text-gray-800);
  overflow: hidden;
  padding: 0;

  .content-html {
    padding: 32px 24px;
    // ... 内容样式
  }

  // 编辑模式的编辑器样式
  .content-editor {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: var(--art-main-bg-color);
    min-height: 500px;
    overflow: hidden;

    :deep(.w-e-toolbar) {
      flex-shrink: 0;
      background: var(--art-main-bg-color);
      border-bottom: 1px solid var(--art-card-border);
    }

    :deep(.w-e-text-container) {
      flex: 1;
      overflow-y: auto !important;
      overflow-x: hidden !important;

      [data-slate-editor] {
        color: var(--art-text-gray-900);
        min-height: 100%;
      }
    }
  }

  // 当存在编辑器时，禁用article-content的padding
  &:has(.content-editor.editing-active) {
    padding: 0;
    overflow: hidden;
  }
}
```

### 7. 添加必要的 import

```typescript
import ArtWangEditor from '@/components/core/forms/art-wang-editor/index.vue'
import { markdownToHtml, validateMarkdownFile, readMarkdownFile } from '@/utils/markdown'
import { Document, Upload } from '@element-plus/icons-vue'
```

## 🎯 与会议记录的一致性

| 特性              | 会议记录      | 工作记录（修复后） |
| ----------------- | ------------- | ------------------ |
| **编辑方式**      | 页内编辑      | ✅ 页内编辑        |
| **文章锁定**      | 支持          | ✅ 支持            |
| **富文本编辑器**  | ArtWangEditor | ✅ ArtWangEditor   |
| **Markdown导入**  | 支持          | ✅ 支持            |
| **查看/编辑切换** | 按钮切换      | ✅ 按钮切换        |
| **布局对齐**      | 左右对齐      | ✅ 左右对齐        |
| **样式风格**      | 专业简洁      | ✅ 专业简洁        |

## 🗑️ 可以删除的老页面

以下文件/路由是老版本的独立文章详情页面，现在可以安全删除：

### 1. 路由配置

**文件**: `src/router/routes/projectRoutes.ts`

```typescript
// 可以删除这个路由（如果存在）
{
  path: 'article/:articleId',
  name: 'ArticleDetail',
  component: () => import('@/views/project/articles/detail/index.vue'),
  meta: {
    title: '文章详情',
    keepAlive: false,
    isHide: true
  }
}
```

**注意**: 如果其他地方还在使用这个路由，请先确认后再删除。

### 2. 组件文件

**可能的老页面文件** (需要确认后删除):

- `src/views/project/articles/detail/index.vue` - 独立的文章详情页面（如果存在）
- 相关的样式文件和组件

### 3. 删除前检查清单

```bash
# 1. 搜索所有引用 ArticleDetail 路由的地方
grep -r "ArticleDetail" src/

# 2. 搜索所有跳转到文章详情的地方
grep -r "article/:articleId" src/
grep -r "articles/detail" src/

# 3. 确认会议记录、模型测试、团队协作等页面都使用页内编辑
# 如果它们都不使用 ArticleDetail 路由，则可以安全删除
```

## ✅ 验证步骤

### 1. 测试查看模式

1. 刷新页面并进入"工作记录"
2. 点击左侧任意工作记录
3. 右侧显示文章内容
4. 确认有"编辑内容"和"删除"按钮

### 2. 测试编辑模式

1. 点击"编辑内容"按钮
2. 页面切换到编辑模式（不跳转）
3. 显示富文本编辑器
4. 显示"导入 Markdown"、"取消"、"保存内容"按钮

### 3. 测试编辑功能

1. 在编辑器中修改内容
2. 点击"保存内容"
3. 成功保存并自动切换回查看模式
4. 内容已更新

### 4. 测试 Markdown 导入

1. 进入编辑模式
2. 点击"导入 Markdown"
3. 选择 .md 文件
4. 内容自动转换为 HTML 并填入编辑器

### 5. 测试取消编辑

1. 进入编辑模式
2. 修改一些内容（不保存）
3. 点击"取消"
4. 回到查看模式，内容未改变

### 6. 测试文章锁定

1. 用户A进入编辑模式
2. 用户B尝试编辑同一篇文章
3. 用户B应该看到"文章正被 xxx 编辑中"的提示

## 🎉 修复效果

### 修复前 ❌

- 点击"编辑"跳转到独立页面
- 老版本样式，与其他页面不一致
- 用户体验差

### 修复后 ✅

- 页内编辑，无需跳转
- 与会议记录页面完全一致
- 支持文章锁定，防止冲突
- 支持 Markdown 导入
- 专业简洁的界面

## 📊 技术亮点

1. **文章锁定机制**：使用 `articlesApi.lock()` 和 `articlesApi.unlock()` 防止多人同时编辑
2. **状态管理**：`isEditing` 控制查看/编辑模式切换
3. **富文本编辑器**：使用 `ArtWangEditor` 组件，功能强大
4. **Markdown 支持**：使用 `marked.js` 和 `dompurify` 安全地转换 Markdown
5. **样式一致性**：完全参考会议记录页面的布局和样式

---

**修复时间**: 2025-11-05  
**状态**: ✅ 已完成  
**版本**: v1.0.2
