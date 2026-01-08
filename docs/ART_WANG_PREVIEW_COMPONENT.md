# ArtWangPreview 富文本预览组件

## 概述

`ArtWangPreview` 是基于 WangEditor 5.x 的只读预览组件，专门用于展示富文本内容。与编辑器 `ArtWangEditor` 不同，此组件完全禁用了编辑功能，只用于内容展示。

## 创建时间

2025-11-05

## 技术特点

### ✅ 优势

1. **完美的样式一致性**

   - 与 `ArtWangEditor` 编辑器的渲染效果完全一致
   - 无需担心编辑态和预览态的样式差异

2. **只读模式**

   - 使用 WangEditor 的 `readOnly: true` 配置
   - 双重禁用保护（`disable()` + `readOnly`）
   - 移除所有交互事件监听器

3. **优化的预览样式**

   - 隐藏工具栏
   - 增强的滚动条样式
   - 打印友好
   - 响应式设计

4. **支持全屏模式**

   - 可选的全屏预览功能
   - 适合长文档阅读

5. **富媒体支持**
   - 图片、表格、代码块
   - 待办列表、引用块
   - 链接、分割线
   - 所有 WangEditor 支持的格式

---

## 组件位置

```
src/components/core/forms/art-wang-preview/index.vue
```

---

## Props 参数

| 参数             | 类型                    | 默认值      | 说明                         |
| ---------------- | ----------------------- | ----------- | ---------------------------- |
| `content`        | `string`                | -           | **必填**，要预览的 HTML 内容 |
| `height`         | `string`                | `'500px'`   | 预览区域高度                 |
| `mode`           | `'default' \| 'simple'` | `'default'` | 编辑器模式                   |
| `showFullscreen` | `boolean`               | `false`     | 是否显示全屏按钮（保留）     |

---

## 基本使用

### 1. 导入组件

```vue
<script setup>
  import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'
  import { ref } from 'vue'

  const articleContent = ref('<h1>标题</h1><p>这是一段文本内容...</p>')
</script>

<template>
  <ArtWangPreview :content="articleContent" height="600px" />
</template>
```

### 2. 在文章详情页使用

```vue
<template>
  <div class="article-detail">
    <el-card>
      <template #header>
        <h3>{{ article.title }}</h3>
      </template>

      <!-- 使用预览组件 -->
      <ArtWangPreview :content="article.content" height="auto" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'

  interface Article {
    title: string
    content: string
  }

  const article = ref<Article>({
    title: '文章标题',
    content: '<p>文章内容...</p>'
  })
</script>
```

### 3. 动态内容更新

组件会自动响应 `content` 的变化：

```vue
<template>
  <div>
    <el-button @click="changeContent">切换内容</el-button>
    <ArtWangPreview :content="dynamicContent" />
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'

  const dynamicContent = ref('<p>初始内容</p>')

  const changeContent = () => {
    dynamicContent.value = '<h2>新内容</h2><p>已更新</p>'
  }
</script>
```

---

## 高级用法

### 1. 全屏预览（暴露方法）

```vue
<template>
  <div>
    <el-button @click="toggleFullscreen">全屏预览</el-button>
    <ArtWangPreview ref="previewRef" :content="content" />
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'

  const previewRef = ref()
  const content = ref('<h1>标题</h1><p>内容...</p>')

  const toggleFullscreen = () => {
    previewRef.value?.toggleFullscreen()
  }
</script>
```

### 2. 自适应高度

设置 `height="auto"` 让预览区域自适应内容高度：

```vue
<ArtWangPreview :content="content" height="auto" />
```

### 3. 简洁模式

使用 `mode="simple"` 获得更简洁的渲染：

```vue
<ArtWangPreview :content="content" mode="simple" />
```

---

## 在现有页面中使用

### 场景 1：工作记录页面

**文件**: `src/views/work-log/records/index.vue`

**替换前**（使用 v-html）：

```vue
<template v-if="!isEditing">
  <div class="content-html" v-html="currentArticle.content"></div>
</template>
```

**替换后**（使用 ArtWangPreview）：

```vue
<script setup>
  import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'
</script>

<template v-if="!isEditing">
  <ArtWangPreview :content="currentArticle.content" height="100%" />
</template>
```

---

### 场景 2：会议记录页面

**文件**: `src/views/project/articles/meeting/index.vue`

```vue
<script setup>
  import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'
</script>

<template>
  <div class="article-content">
    <!-- 查看模式 -->
    <template v-if="!isEditing">
      <div v-if="currentArticle.summary" class="article-description">
        <h4>📝 简介</h4>
        <p>{{ currentArticle.summary }}</p>
      </div>

      <!-- 使用预览组件 -->
      <div class="article-body">
        <ArtWangPreview :content="currentArticle.content" height="100%" />
      </div>
    </template>

    <!-- 编辑模式 -->
    <template v-else>
      <div class="content-editor">
        <ArtWangEditor v-model="editForm.content" height="100%" />
      </div>
    </template>
  </div>
</template>
```

---

### 场景 3：项目文档页面

**文件**: `src/views/project/management/components/ArticleDetailView.vue`

```vue
<script setup>
  import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'
</script>

<template>
  <div class="article-content">
    <!-- 查看模式 -->
    <template v-if="!isEditing">
      <div v-if="article.summary" class="article-description">
        <h4>📝 简介</h4>
        <p>{{ article.summary }}</p>
      </div>

      <div class="article-body">
        <ArtWangPreview :content="article.content" height="100%" />
      </div>

      <div v-if="article.tags && article.tags.length" class="article-tags">
        <h4>🏷️ 标签</h4>
        <div class="tags-list">
          <el-tag v-for="tag in article.tags" :key="tag">{{ tag }}</el-tag>
        </div>
      </div>
    </template>

    <!-- 编辑模式 -->
    <template v-else>
      <div class="content-editor">
        <ArtWangEditor v-model="editForm.content" height="100%" />
      </div>
    </template>
  </div>
</template>
```

---

## 样式定制

### 自定义边框和背景

```vue
<ArtWangPreview :content="content" class="custom-preview" />

<style scoped>
  .custom-preview {
    border: 2px solid var(--el-color-primary);
    background: #f9f9f9;
  }
</style>
```

### 调整内边距

```vue
<ArtWangPreview :content="content" class="compact-preview" />

<style scoped>
  .compact-preview :deep(.w-e-scroll) {
    padding: 12px 16px !important;
  }
</style>
```

---

## 对比：v-html vs ArtWangPreview

| 特性           | v-html            | ArtWangPreview      |
| -------------- | ----------------- | ------------------- |
| **样式一致性** | ❌ 需手动调整     | ✅ 与编辑器完全一致 |
| **代码高亮**   | ❌ 需额外配置     | ✅ 自动支持         |
| **表格样式**   | ❌ 需手动样式     | ✅ 自动支持         |
| **待办列表**   | ❌ 需手动样式     | ✅ 自动支持         |
| **性能**       | ✅ 最快           | ⚠️ 需加载编辑器     |
| **体积**       | ✅ 0 KB           | ⚠️ ~300 KB          |
| **维护成本**   | ⚠️ 样式需手动同步 | ✅ 自动同步         |
| **打印友好**   | ⚠️ 需手动优化     | ✅ 自动优化         |

---

## 性能优化建议

### 1. 懒加载

对于非首屏的预览组件，使用异步导入：

```vue
<script setup>
  import { defineAsyncComponent } from 'vue'

  const ArtWangPreview = defineAsyncComponent(
    () => import('@/components/core/forms/art-wang-preview/index.vue')
  )
</script>
```

### 2. 条件渲染

只在需要预览时才渲染组件：

```vue
<template>
  <div>
    <el-button @click="showPreview = true">查看预览</el-button>

    <ArtWangPreview v-if="showPreview" :content="content" />
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  const showPreview = ref(false)
</script>
```

### 3. 复用编辑器实例

在同一页面多次预览时，考虑使用一个实例：

```vue
<ArtWangPreview :key="currentArticleId" :content="currentArticle.content" />
```

---

## 技术实现细节

### 1. 只读模式配置

```typescript
const editorConfig: Partial<IEditorConfig> = {
  readOnly: true, // WangEditor 只读配置
  scroll: true, // 允许滚动
  placeholder: '暂无内容',
  MENU_CONF: {} // 禁用所有菜单
}
```

### 2. 双重禁用保护

```typescript
const onCreateEditor = (editor: IDomEditor) => {
  editorRef.value = editor

  // 1. 调用 disable() 方法
  editor.disable()

  // 2. 移除所有事件监听
  editor.off('change')
  editor.off('focus')
  editor.off('blur')
}
```

### 3. 隐藏工具栏

```scss
:deep(.w-e-toolbar) {
  display: none !important;
}
```

### 4. 响应式内容更新

```typescript
// 监听 content 变化，同步到编辑器
watch(
  () => props.content,
  (newContent) => {
    contentModel.value = newContent
  }
)
```

---

## 故障排除

### 问题 1：内容不更新

**原因**：`content` 没有响应式更新

**解决**：

```vue
// ❌ 错误 const content = '
<p>内容</p>
' // ✅ 正确 const content = ref('
<p>内容</p>
')
```

### 问题 2：样式不一致

**原因**：CSS 变量未定义

**解决**：确保项目中定义了以下 CSS 变量：

- `--art-main-bg-color`
- `--art-text-gray-700`
- `--art-text-gray-900`
- `--el-border-color`
- `--el-color-primary`

### 问题 3：高度显示异常

**原因**：父容器没有明确高度

**解决**：

```vue
<!-- 给父容器设置明确高度 -->
<div style="height: 600px;">
  <ArtWangPreview :content="content" height="100%" />
</div>
```

---

## 浏览器兼容性

| 浏览器  | 版本要求 |
| ------- | -------- |
| Chrome  | ✅ 90+   |
| Firefox | ✅ 88+   |
| Safari  | ✅ 14+   |
| Edge    | ✅ 90+   |

---

## 未来优化计划

### 1. 图片点击放大

```typescript
// 添加图片查看器功能
const handleImageClick = (img: HTMLImageElement) => {
  // 使用 el-image-viewer 预览
}
```

### 2. 代码复制按钮

```typescript
// 为代码块添加复制按钮
const addCopyButton = (pre: HTMLPreElement) => {
  // 添加复制功能
}
```

### 3. 目录导航

```typescript
// 自动生成文章目录
const generateTOC = () => {
  // 提取标题生成目录
}
```

### 4. 导出功能

```typescript
// 导出为 PDF/Word
const exportToPDF = () => {
  // 使用 jsPDF 导出
}
```

---

## 相关文件

### 组件文件

- `src/components/core/forms/art-wang-preview/index.vue` - 预览组件
- `src/components/core/forms/art-wang-editor/index.vue` - 编辑器组件

### 使用页面

- `src/views/work-log/records/index.vue` - 工作记录页面
- `src/views/project/articles/meeting/index.vue` - 会议记录页面
- `src/views/project/management/components/ArticleDetailView.vue` - 项目文档页面

### 文档

- `docs/ART_WANG_PREVIEW_COMPONENT.md` - 本文档

---

## 总结

`ArtWangPreview` 组件提供了一个专业的、与编辑器样式完全一致的富文本预览解决方案。它特别适合以下场景：

✅ **推荐使用**：

- 需要与编辑器样式完全一致
- 内容包含复杂格式（表格、代码块、待办列表等）
- 对预览质量要求高
- 不担心额外的体积开销

❌ **不推荐使用**：

- 简单的纯文本展示
- 对性能要求极高的场景
- 对打包体积非常敏感

如果你的项目对性能和体积更敏感，可以考虑使用优化的 `v-html` 方案。

---

## 示例代码库

完整的使用示例可以在以下文件中找到：

- 基本用法：本文档的"基本使用"章节
- 实际应用：本文档的"在现有页面中使用"章节

开始使用 `ArtWangPreview`，让你的富文本预览体验更上一层楼！🎉
