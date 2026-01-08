# ArtXnotePreview 组件

基于 XNote (TextBus) 编辑器的预览组件，使用编辑器本身的**只读模式**来实现预览。

## 🎯 核心优势

与手动编写的 HTML 预览组件相比：

✅ **渲染效果完全一致** - 使用编辑器本身渲染，预览效果 100% 与编辑时相同  
✅ **自动支持所有功能** - 编辑器支持的所有元素（表格、代码、公式等）都能正确显示  
✅ **无需维护样式** - 编辑器更新时自动同步样式  
✅ **完美主题适配** - 继承编辑器的主题系统

## 📝 用途

- ✅ 预览 **XNote (TextBus)** 编辑器内容
- ✅ 协作文档的只读查看模式
- ✅ 文档导出预览
- ✅ 文档历史版本查看

## 🚀 使用方法

### 基础使用

```vue
<template>
  <ArtXnotePreview :content="htmlContent" height="600px" />
</template>

<script setup>
  import { ref } from 'vue'

  const htmlContent = ref('<h1>Hello World</h1><p>这是一段示例文本</p>')
</script>
```

### 在协作文档中使用

```vue
<template>
  <div class="document-viewer">
    <ArtXnotePreview :content="document.content" height="100%" />
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import ArtXnotePreview from '@/components/core/forms/art-xnote-preview/index.vue'

  const document = ref({
    content: '<h1>文档标题</h1><p>文档内容...</p>'
  })
</script>
```

### 动态更新内容

```vue
<template>
  <div>
    <el-input v-model="content" type="textarea" :rows="5" placeholder="输入 HTML 内容" />

    <ArtXnotePreview :content="content" height="400px" />
  </div>
</template>

<script setup>
  import { ref } from 'vue'

  const content = ref('<p>实时预览</p>')
  // 内容变化时自动更新预览
</script>
```

## 📦 Props

| 属性           | 类型    | 默认值  | 说明                                      |
| -------------- | ------- | ------- | ----------------------------------------- |
| content        | string  | ''      | 要预览的 HTML 内容（由 XNote 编辑器生成） |
| height         | string  | '500px' | 组件高度                                  |
| showFullscreen | boolean | false   | 是否显示全屏按钮（暂未实现）              |

## 🎨 支持的功能

### 文本格式

- 标题 (H1-H6)
- 段落、粗体、斜体、下划线、删除线
- 上标、下标、高亮标记
- 文字颜色、背景色

### 结构化内容

- 有序/无序列表（支持嵌套）
- 任务列表
- 引用块
- 代码（内联和代码块）
- 表格（支持合并单元格）

### 媒体元素

- 图片（响应式，带圆角和阴影）
- 视频
- 链接（带 hover 效果）

### 高级功能

- 数学公式 (KaTeX)
- 语法高亮代码块
- 分割线

## 🔑 核心特性

### 1. 只读模式

```typescript
// 编辑器配置
editorInstance = new Editor({
  content: props.content,
  readonly: true, // ⭐ 关键：只读模式
  placeholder: '暂无内容'
})
```

### 2. 隐藏工具栏

```scss
// 隐藏所有工具栏
:deep(.textbus-toolbar),
:deep(.xnote-toolbar),
:deep([class*='toolbar']) {
  display: none !important;
}
```

### 3. 禁用交互

```scss
// 禁用编辑交互
:deep(*) {
  pointer-events: auto !important;
  cursor: default !important;
}

// 但允许文本选择
:deep(p),
:deep(span),
:deep(li) {
  user-select: text !important;
}
```

### 4. 自动更新

```typescript
// 监听 props.content 变化
watch(
  () => props.content,
  (newContent) => {
    editorInstance.setContent(newContent || '<p></p>')
  }
)
```

## 🆚 与其他预览组件的对比

| 特性       | ArtXnotePreview | ArtHtmlPreview | ArtWangPreview |
| ---------- | --------------- | -------------- | -------------- |
| 适用编辑器 | XNote           | 通用 HTML      | Wang Editor    |
| 渲染方式   | 编辑器自身      | 手动 HTML      | 编辑器自身     |
| 效果一致性 | ⭐⭐⭐⭐⭐      | ⭐⭐⭐         | ⭐⭐⭐⭐⭐     |
| 维护成本   | 低              | 高             | 低             |
| 性能       | 良好            | 优秀           | 良好           |
| 主题适配   | ✅ 完整         | ✅ 完整        | ✅ 完整        |

## 🌗 主题适配

组件自动适配项目的亮色/暗色主题，使用 CSS 变量：

- `--art-main-bg-color` - 背景色
- `--art-text-gray-900` - 主要文字颜色
- `--art-text-gray-700` - 次要文字颜色
- `--art-card-border` - 边框颜色
- `--art-bg-color` - 次级背景色

## 📋 暴露的方法

```typescript
// 通过 ref 访问组件方法
const previewRef = ref()

// 切换全屏（待实现）
previewRef.value?.toggleFullscreen()

// 获取编辑器实例
const editor = previewRef.value?.editorInstance
```

## ⚠️ 注意事项

1. **内容格式**：必须是由 XNote 编辑器生成的 HTML
2. **性能**：大文档建议使用虚拟滚动
3. **兼容性**：需要确保已安装 `@textbus/xnote` 依赖
4. **内容更新**：使用 `watch` 自动响应 `content` 变化

## 🔄 迁移指南

从 `ArtHtmlPreview` 迁移：

```diff
- import ArtHtmlPreview from '@/components/core/forms/art-html-preview/index.vue'
+ import ArtXnotePreview from '@/components/core/forms/art-xnote-preview/index.vue'

- <ArtHtmlPreview :content="document.content" height="600px" />
+ <ArtXnotePreview :content="document.content" height="600px" />
```

**优势**：

- 🎯 预览效果与编辑时完全一致
- 🚀 自动支持所有 XNote 功能
- 🎨 无需手动维护样式

## 📚 参考

- [XNote 官方文档](https://textbus.io/xnote)
- [TextBus 框架文档](https://textbus.io)
- [只读模式配置](https://textbus.io/api/editor#readonly)
