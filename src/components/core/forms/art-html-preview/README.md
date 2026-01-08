# ArtHtmlPreview 组件

通用的 HTML 内容预览组件，用于显示富文本编辑器生成的 HTML 内容。

## 📝 用途

- ✅ 预览 **XNote (TextBus)** 编辑器内容
- ✅ 预览 **Wang Editor** 编辑器内容
- ✅ 预览任何标准 HTML 内容
- ✅ 自动适配亮色/暗色主题

## 🚀 使用方法

### 基础使用

```vue
<template>
  <ArtHtmlPreview :content="htmlContent" height="600px" />
</template>

<script setup>
  import { ref } from 'vue'

  const htmlContent = ref('<h1>Hello World</h1><p>这是一段示例文本</p>')
</script>
```

### 在协作文档中使用

```vue
<template>
  <ArtHtmlPreview :content="document.content" height="100%" />
</template>
```

## 📦 Props

| 属性    | 类型   | 默认值 | 说明               |
| ------- | ------ | ------ | ------------------ |
| content | string | ''     | 要预览的 HTML 内容 |
| height  | string | '100%' | 组件高度           |

## 🎨 支持的 HTML 元素

### 标题

- `<h1>` ~ `<h6>`

### 文本格式

- `<p>` - 段落
- `<strong>` / `<b>` - 粗体
- `<em>` / `<i>` - 斜体
- `<u>` - 下划线
- `<s>` / `<del>` - 删除线
- `<mark>` - 高亮
- `<sup>` - 上标
- `<sub>` - 下标

### 列表

- `<ul>` - 无序列表
- `<ol>` - 有序列表
- `<li>` - 列表项

### 引用和代码

- `<blockquote>` - 引用块
- `<code>` - 内联代码
- `<pre><code>` - 代码块

### 表格

- `<table>` + `<thead>` + `<tbody>` + `<tr>` + `<th>` + `<td>`

### 媒体

- `<img>` - 图片（自动响应式）
- `<a>` - 链接

### 其他

- `<hr>` - 分割线

## 🌗 主题适配

组件自动适配项目的亮色/暗色主题，使用 CSS 变量：

- `--art-main-bg-color` - 背景色
- `--art-text-gray-900` - 主要文字颜色
- `--art-text-gray-700` - 次要文字颜色
- `--art-card-border` - 边框颜色
- `--art-bg-color` - 次级背景色

## 🔒 安全性

> ⚠️ 注意：当前版本使用 `v-html` 渲染内容，在生产环境中建议使用 DOMPurify 等库进行内容清理，防止 XSS 攻击。

## 📋 示例

查看 [example.vue](./example.vue) 了解完整的使用示例。

## 🆚 与 ArtWangPreview 的区别

| 特性        | ArtHtmlPreview                 | ArtWangPreview       |
| ----------- | ------------------------------ | -------------------- |
| 适用编辑器  | 通用（XNote/Wang Editor/任何） | 仅 Wang Editor       |
| HTML 兼容性 | 标准 HTML                      | Wang Editor 专用格式 |
| 主题适配    | ✅ 完整支持                    | ✅ 完整支持          |
| 样式丰富度  | ⭐⭐⭐⭐⭐                     | ⭐⭐⭐⭐             |

## 🔄 迁移指南

如果你之前使用 `ArtWangPreview`，现在想切换到 `ArtHtmlPreview`：

```diff
- import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'
+ import ArtHtmlPreview from '@/components/core/forms/art-html-preview/index.vue'

- <ArtWangPreview :content="document.content" height="600px" />
+ <ArtHtmlPreview :content="document.content" height="600px" />
```

**注意**：如果你的内容是由 Wang Editor 生成的，可以继续使用 `ArtWangPreview`。只有当使用 XNote 或其他编辑器时，才需要使用 `ArtHtmlPreview`。
