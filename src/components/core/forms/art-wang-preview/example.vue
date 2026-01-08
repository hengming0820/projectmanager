<!-- ArtWangPreview 使用示例 -->
<template>
  <div class="preview-example-page">
    <el-card class="demo-card">
      <template #header>
        <div class="card-header">
          <span>ArtWangPreview 组件示例</span>
          <el-button-group>
            <el-button
              :type="currentTab === 'simple' ? 'primary' : 'default'"
              @click="currentTab = 'simple'"
            >
              简单示例
            </el-button>
            <el-button
              :type="currentTab === 'complex' ? 'primary' : 'default'"
              @click="currentTab = 'complex'"
            >
              复杂内容
            </el-button>
            <el-button
              :type="currentTab === 'comparison' ? 'primary' : 'default'"
              @click="currentTab = 'comparison'"
            >
              对比 v-html
            </el-button>
          </el-button-group>
        </div>
      </template>

      <!-- 简单示例 -->
      <div v-if="currentTab === 'simple'" class="demo-section">
        <h3>📝 简单示例</h3>
        <p>展示基本的富文本内容</p>

        <ArtWangPreview :content="simpleContent" height="400px" />
      </div>

      <!-- 复杂内容 -->
      <div v-if="currentTab === 'complex'" class="demo-section">
        <h3>🎨 复杂内容示例</h3>
        <p>包含标题、图片、代码块、表格、列表等</p>

        <ArtWangPreview :content="complexContent" height="600px" />
      </div>

      <!-- 对比 v-html -->
      <div v-if="currentTab === 'comparison'" class="demo-section">
        <h3>⚖️ v-html vs ArtWangPreview 对比</h3>

        <el-row :gutter="20">
          <el-col :span="12">
            <div class="comparison-box">
              <h4>使用 v-html（原方式）</h4>
              <div class="content-html" v-html="comparisonContent"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="comparison-box">
              <h4>使用 ArtWangPreview（新方式）</h4>
              <ArtWangPreview :content="comparisonContent" height="400px" />
            </div>
          </el-col>
        </el-row>

        <el-alert type="success" title="观察差异" :closable="false" style="margin-top: 20px">
          <p>注意观察：</p>
          <ul>
            <li>✅ ArtWangPreview 的代码块有语法高亮和更好的样式</li>
            <li>✅ 表格样式更加统一和美观</li>
            <li>✅ 整体排版更加专业</li>
            <li>✅ 与编辑器的样式完全一致</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- 代码示例 -->
    <el-card class="demo-card" style="margin-top: 20px">
      <template #header>
        <span>💻 代码示例</span>
      </template>

      <el-tabs v-model="codeTab">
        <el-tab-pane label="基本用法" name="basic">
          <pre class="code-block">{{ basicUsageCode }}</pre>
        </el-tab-pane>

        <el-tab-pane label="替换 v-html" name="replace">
          <pre class="code-block">{{ replaceVHtmlCode }}</pre>
        </el-tab-pane>

        <el-tab-pane label="动态内容" name="dynamic">
          <pre class="code-block">{{ dynamicContentCode }}</pre>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import ArtWangPreview from './index.vue'

  defineOptions({ name: 'ArtWangPreviewExample' })

  const currentTab = ref('simple')
  const codeTab = ref('basic')

  // 简单示例内容
  const simpleContent = ref(`
<h1>欢迎使用 ArtWangPreview</h1>
<p>这是一个<strong>富文本预览组件</strong>，基于 WangEditor 5.x 的只读模式。</p>
<p>它支持：</p>
<ul>
  <li>各种文本格式：<strong>加粗</strong>、<em>斜体</em>、<u>下划线</u></li>
  <li>标题层级（H1-H6）</li>
  <li>有序列表和无序列表</li>
  <li>引用块、代码块</li>
  <li>图片、表格、链接</li>
</ul>
<blockquote>
  <p>💡 提示：这是一个引用块示例</p>
</blockquote>
<p>访问 <a href="https://www.wangeditor.com/" target="_blank">WangEditor 官网</a> 了解更多</p>
`)

  // 复杂内容示例
  const complexContent = ref(`
<h1>📚 技术文档示例</h1>
<p>本文档展示了 ArtWangPreview 组件对各种富文本格式的支持能力。</p>

<h2>1. 代码块示例</h2>
<p>支持语法高亮的代码块：</p>
<pre><code class="language-javascript">// JavaScript 示例
function greet(name) {
  console.log(\`Hello, \${name}!\`)
  return { success: true, message: 'Welcome!' }
}

// 调用函数
greet('ArtWangPreview')
</code></pre>

<pre><code class="language-python"># Python 示例
def calculate_sum(numbers):
    """计算列表中所有数字的总和"""
    return sum(numbers)

# 使用示例
result = calculate_sum([1, 2, 3, 4, 5])
print(f"总和: {result}")
</code></pre>

<h2>2. 表格示例</h2>
<p>支持复杂的表格格式：</p>
<table>
  <thead>
    <tr>
      <th>功能</th>
      <th>v-html</th>
      <th>ArtWangPreview</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>样式一致性</td>
      <td>❌ 需手动调整</td>
      <td>✅ 完全一致</td>
    </tr>
    <tr>
      <td>代码高亮</td>
      <td>❌ 需额外配置</td>
      <td>✅ 自动支持</td>
    </tr>
    <tr>
      <td>性能</td>
      <td>✅ 最快</td>
      <td>⚠️ 需加载编辑器</td>
    </tr>
    <tr>
      <td>维护成本</td>
      <td>⚠️ 需手动同步</td>
      <td>✅ 自动同步</td>
    </tr>
  </tbody>
</table>

<h2>3. 列表示例</h2>

<h3>有序列表</h3>
<ol>
  <li>第一步：导入组件</li>
  <li>第二步：传入内容
    <ol>
      <li>准备 HTML 内容</li>
      <li>绑定到 content 属性</li>
    </ol>
  </li>
  <li>第三步：配置高度和模式</li>
  <li>第四步：完成！</li>
</ol>

<h3>无序列表</h3>
<ul>
  <li>支持文本格式
    <ul>
      <li>加粗、斜体、下划线</li>
      <li>删除线、上标、下标</li>
    </ul>
  </li>
  <li>支持富媒体
    <ul>
      <li>图片上传和显示</li>
      <li>视频嵌入</li>
    </ul>
  </li>
  <li>支持交互元素
    <ul>
      <li>超链接</li>
      <li>待办列表（只读）</li>
    </ul>
  </li>
</ul>

<h2>4. 引用块示例</h2>
<blockquote>
  <p>💡 <strong>专业提示</strong></p>
  <p>使用 ArtWangPreview 可以确保预览效果与编辑器完全一致，避免样式差异带来的困扰。</p>
</blockquote>

<blockquote>
  <p>⚠️ <strong>注意事项</strong></p>
  <p>由于需要加载 WangEditor，组件体积约 300KB。如果对性能要求极高，可以考虑使用优化的 v-html 方案。</p>
</blockquote>

<h2>5. 行内样式示例</h2>
<p>支持多种行内样式：</p>
<p>
  <strong>加粗文本</strong> | 
  <em>斜体文本</em> | 
  <u>下划线文本</u> | 
  <s>删除线文本</s> | 
  <code>行内代码</code> | 
  <span style="color: #f56c6c;">红色文本</span> | 
  <span style="background-color: #fef0f0; padding: 2px 4px;">高亮背景</span>
</p>

<h2>6. 分割线</h2>
<p>使用分割线分隔不同部分：</p>
<hr>
<p>这是分割线后的内容</p>

<h2>7. 链接示例</h2>
<p>访问以下链接了解更多：</p>
<ul>
  <li><a href="https://www.wangeditor.com/" target="_blank">WangEditor 官网</a></li>
  <li><a href="https://element-plus.org/" target="_blank">Element Plus 官网</a></li>
  <li><a href="https://cn.vuejs.org/" target="_blank">Vue.js 官网</a></li>
</ul>
`)

  // 对比内容
  const comparisonContent = ref(`
<h2>代码块对比</h2>
<pre><code class="language-typescript">interface Article {
  id: string
  title: string
  content: string
  author: string
  createdAt: Date
}

const article: Article = {
  id: '123',
  title: '示例文章',
  content: '<p>内容...</p>',
  author: 'admin',
  createdAt: new Date()
}
</code></pre>

<h2>表格对比</h2>
<table>
  <thead>
    <tr>
      <th>姓名</th>
      <th>角色</th>
      <th>部门</th>
      <th>状态</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>张三</td>
      <td>管理员</td>
      <td>研发部</td>
      <td>✅ 在线</td>
    </tr>
    <tr>
      <td>李四</td>
      <td>审核员</td>
      <td>算法组</td>
      <td>✅ 在线</td>
    </tr>
    <tr>
      <td>王五</td>
      <td>标注员</td>
      <td>标注组</td>
      <td>⚠️ 离线</td>
    </tr>
  </tbody>
</table>
`)

  // 代码示例（使用 String.raw 避免解析器混淆）
  const basicUsageCode = String.raw`<script setup>
import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'
import { ref } from 'vue'

const content = ref('<h1>标题</h1><p>内容...</p>')
<\/script>

<template>
  <ArtWangPreview :content="content" height="600px" />
<\/template>`

  const replaceVHtmlCode = String.raw`<!-- 替换前：使用 v-html -->
<template v-if="!isEditing">
  <div class="content-html" v-html="article.content"></div>
<\/template>

<!-- 替换后：使用 ArtWangPreview -->
<script setup>
import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'
<\/script>

<template v-if="!isEditing">
  <ArtWangPreview 
    :content="article.content" 
    height="100%"
  />
<\/template>`

  const dynamicContentCode = String.raw`<script setup>
import { ref } from 'vue'
import ArtWangPreview from '@/components/core/forms/art-wang-preview/index.vue'

const content = ref('<p>初始内容</p>')

// 内容会自动更新
const updateContent = () => {
  content.value = '<h2>新内容</h2><p>已更新！</p>'
}
<\/script>

<template>
  <div>
    <el-button @click="updateContent">更新内容</el-button>
    <ArtWangPreview :content="content" height="400px" />
  </div>
<\/template>`
</script>

<style lang="scss" scoped>
  .preview-example-page {
    padding: 20px;
    background: var(--art-bg-color);
    min-height: 100vh;
  }

  .demo-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .demo-section {
    h3 {
      margin-top: 0;
      margin-bottom: 8px;
      color: var(--art-text-gray-900);
    }

    > p {
      margin-bottom: 16px;
      color: var(--art-text-gray-600);
    }
  }

  .comparison-box {
    border: 1px solid var(--el-border-color);
    border-radius: 8px;
    padding: 16px;
    background: white;

    h4 {
      margin-top: 0;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 2px solid var(--el-border-color);
    }

    .content-html {
      padding: 12px;
      max-height: 400px;
      overflow-y: auto;
      font-size: 15px;
      line-height: 1.8;

      // 基础 v-html 样式
      :deep(h2) {
        font-size: 20px;
        margin: 16px 0 12px;
      }

      :deep(p) {
        margin: 8px 0;
      }

      :deep(pre) {
        background: #282c34;
        color: #abb2bf;
        padding: 12px;
        border-radius: 4px;
        overflow-x: auto;
      }

      :deep(table) {
        border-collapse: collapse;
        width: 100%;

        th,
        td {
          border: 1px solid #ddd;
          padding: 8px;
        }
      }
    }
  }

  .code-block {
    background: #282c34;
    color: #abb2bf;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
  }

  :deep(.el-alert) {
    ul {
      margin: 8px 0 0;
      padding-left: 20px;

      li {
        margin: 4px 0;
      }
    }
  }
</style>
