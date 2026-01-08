<!-- ArtHtmlPreview 使用示例 -->
<template>
  <div class="html-preview-example">
    <h2>ArtHtmlPreview 组件使用示例</h2>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>基础使用</span>
        </div>
      </template>

      <ArtHtmlPreview :content="sampleContent" height="400px" />
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>示例 HTML 内容</span>
        </div>
      </template>

      <el-input v-model="sampleContent" type="textarea" :rows="10" placeholder="输入 HTML 内容" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import ArtHtmlPreview from './index.vue'

  const sampleContent = ref(`
<h1>欢迎使用 ArtHtmlPreview 组件</h1>

<p>这是一个通用的 HTML 内容预览组件，适用于：</p>

<ul>
  <li><strong>XNote 编辑器</strong> - 基于 TextBus 的富文本编辑器</li>
  <li><strong>Wang Editor</strong> - 传统的富文本编辑器</li>
  <li><strong>任何 HTML 内容</strong> - 支持标准 HTML 标签</li>
</ul>

<h2>主要特性</h2>

<blockquote>
  <p>支持响应式设计，自动适配亮色/暗色主题</p>
</blockquote>

<h3>1. 丰富的样式支持</h3>
<p>支持标题、段落、列表、引用、代码、表格、图片等各种元素。</p>

<h3>2. 代码高亮</h3>
<p>内联代码：<code>const hello = "world"</code></p>

<pre><code>// 代码块示例
function greet(name) {
  return \`Hello, \${name}!\`;
}
</code></pre>

<h3>3. 表格支持</h3>
<table>
  <thead>
    <tr>
      <th>功能</th>
      <th>状态</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>标题</td>
      <td>✅</td>
      <td>支持 H1-H6</td>
    </tr>
    <tr>
      <td>列表</td>
      <td>✅</td>
      <td>有序和无序列表</td>
    </tr>
    <tr>
      <td>代码</td>
      <td>✅</td>
      <td>内联和代码块</td>
    </tr>
  </tbody>
</table>

<hr>

<p><strong>粗体文字</strong> | <em>斜体文字</em> | <u>下划线</u> | <s>删除线</s></p>

<p>上标: E=mc<sup>2</sup> | 下标: H<sub>2</sub>O</p>

<p>链接: <a href="https://github.com">GitHub</a></p>
`)
</script>

<style scoped lang="scss">
  .html-preview-example {
    padding: 20px;

    h2 {
      margin-bottom: 20px;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      span {
        font-weight: 600;
        font-size: 16px;
      }
    }
  }
</style>
