<!-- 通用 HTML 内容预览组件 -->
<template>
  <div class="html-preview-container" :style="{ height: height }">
    <div class="html-preview-content" v-html="sanitizedContent"></div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue'

  interface Props {
    content?: string
    height?: string
  }

  const props = withDefaults(defineProps<Props>(), {
    content: '',
    height: '100%'
  })

  // 简单的内容清理（实际项目中应该使用 DOMPurify）
  const sanitizedContent = computed(() => {
    return (
      props.content || '<p style="color: #999; text-align: center; padding: 40px;">暂无内容</p>'
    )
  })
</script>

<style scoped lang="scss">
  .html-preview-container {
    width: 100%;
    overflow-y: auto;
    background: var(--art-main-bg-color);
    border-radius: 8px;
  }

  .html-preview-content {
    padding: 20px;
    color: var(--art-text-gray-900);
    font-size: 15px;
    line-height: 1.8;

    // 标题样式
    :deep(h1) {
      font-size: 32px;
      font-weight: 700;
      margin: 24px 0 16px 0;
      line-height: 1.3;
      color: var(--art-text-gray-900);
      border-bottom: 2px solid var(--art-card-border);
      padding-bottom: 12px;
    }

    :deep(h2) {
      font-size: 28px;
      font-weight: 600;
      margin: 20px 0 14px 0;
      line-height: 1.3;
      color: var(--art-text-gray-900);
    }

    :deep(h3) {
      font-size: 24px;
      font-weight: 600;
      margin: 18px 0 12px 0;
      line-height: 1.4;
      color: var(--art-text-gray-900);
    }

    :deep(h4) {
      font-size: 20px;
      font-weight: 600;
      margin: 16px 0 10px 0;
      line-height: 1.4;
      color: var(--art-text-gray-900);
    }

    :deep(h5) {
      font-size: 18px;
      font-weight: 600;
      margin: 14px 0 8px 0;
      line-height: 1.5;
      color: var(--art-text-gray-900);
    }

    :deep(h6) {
      font-size: 16px;
      font-weight: 600;
      margin: 12px 0 8px 0;
      line-height: 1.5;
      color: var(--art-text-gray-900);
    }

    // 段落样式
    :deep(p) {
      margin: 12px 0;
      line-height: 1.8;
      color: var(--art-text-gray-900);
    }

    // 列表样式
    :deep(ul),
    :deep(ol) {
      margin: 12px 0;
      padding-left: 28px;

      li {
        margin: 6px 0;
        line-height: 1.8;
        color: var(--art-text-gray-900);
      }
    }

    :deep(ul) {
      list-style-type: disc;

      ul {
        list-style-type: circle;

        ul {
          list-style-type: square;
        }
      }
    }

    :deep(ol) {
      list-style-type: decimal;
    }

    // 引用块样式
    :deep(blockquote) {
      margin: 16px 0;
      padding: 12px 16px;
      border-left: 4px solid #3b82f6;
      background: var(--art-bg-color);
      color: var(--art-text-gray-700);
      border-radius: 4px;

      p {
        margin: 6px 0;
      }
    }

    // 代码样式
    :deep(code) {
      padding: 2px 6px;
      background: var(--art-bg-color);
      border: 1px solid var(--art-card-border);
      border-radius: 4px;
      font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
      font-size: 0.9em;
      color: #e74c3c;
    }

    :deep(pre) {
      margin: 16px 0;
      padding: 16px;
      background: var(--art-bg-color);
      border: 1px solid var(--art-card-border);
      border-radius: 8px;
      overflow-x: auto;

      code {
        padding: 0;
        background: transparent;
        border: none;
        color: var(--art-text-gray-900);
        font-size: 14px;
        line-height: 1.6;
      }
    }

    // 表格样式
    :deep(table) {
      width: 100%;
      margin: 16px 0;
      border-collapse: collapse;
      border: 1px solid var(--art-card-border);
      border-radius: 8px;
      overflow: hidden;

      thead {
        background: var(--art-bg-color);

        th {
          padding: 12px;
          text-align: left;
          font-weight: 600;
          color: var(--art-text-gray-900);
          border-bottom: 2px solid var(--art-card-border);
        }
      }

      tbody {
        tr {
          border-bottom: 1px solid var(--art-card-border);

          &:hover {
            background: var(--art-bg-color);
          }

          &:last-child {
            border-bottom: none;
          }
        }

        td {
          padding: 12px;
          color: var(--art-text-gray-900);
        }
      }
    }

    // 图片样式
    :deep(img) {
      max-width: 100%;
      height: auto;
      margin: 16px 0;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    // 分割线样式
    :deep(hr) {
      margin: 24px 0;
      border: none;
      border-top: 2px solid var(--art-card-border);
    }

    // 链接样式
    :deep(a) {
      color: #3b82f6;
      text-decoration: none;
      border-bottom: 1px solid transparent;
      transition: all 0.2s;

      &:hover {
        color: #2563eb;
        border-bottom-color: #2563eb;
      }
    }

    // 强调样式
    :deep(strong) {
      font-weight: 700;
      color: var(--art-text-gray-900);
    }

    :deep(em) {
      font-style: italic;
    }

    :deep(u) {
      text-decoration: underline;
    }

    :deep(s),
    :deep(del) {
      text-decoration: line-through;
      opacity: 0.7;
    }

    // 上标和下标
    :deep(sup) {
      vertical-align: super;
      font-size: 0.75em;
    }

    :deep(sub) {
      vertical-align: sub;
      font-size: 0.75em;
    }

    // 高亮标记
    :deep(mark) {
      background: #fef08a;
      color: #854d0e;
      padding: 2px 4px;
      border-radius: 2px;
    }
  }
</style>
