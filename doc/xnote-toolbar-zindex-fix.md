# XNote 编辑器工具栏被遮挡问题修复案例

## 问题描述

在集成 XNote 富文本编辑器并启用协作功能后，出现以下问题：

1. **左侧工具栏（LeftToolbar）不可见** - 鼠标悬停在文本行时，左侧的 `+` 按钮被遮挡
2. **行内工具栏（InlineToolbar）不可见** - 选中文本时，弹出的格式化工具栏被遮挡
3. **协作光标标签遮挡工具栏** - 多人编辑时，其他用户的光标名称标签覆盖了工具栏

## 根本原因分析

### 1. **CSS 层级问题（z-index）**

- **XNote 源码中工具栏的 z-index 太低**：
  - `LeftToolbar`: `z-index: 10`（源码 `left-toolbar.scoped.scss` 第 5 行）
  - `InlineToolbar`: `z-index: 3`（源码 `inline-toolbar.scoped.scss` 第 3 行）
  
- **协作光标的 z-index 被错误设置为 999999**，导致覆盖了工具栏

### 2. **容器 overflow 属性导致裁剪**

- **`.xnote-editor-wrapper`** 设置了 `overflow: hidden`，裁剪了所有溢出内容
- **`.xnote-editor`** 设置了 `overflow-x: hidden`，裁剪了左侧工具栏
- **XNote 内部容器**（VIEW_CONTAINER 等）的 overflow 属性未被覆盖

### 3. **工具栏动态插入导致 CSS 无法覆盖**

工具栏通过 `LeftToolbarPlugin.setup()` 动态插入到 DOM 中：
```typescript
const viewDocument = injector.get(VIEW_CONTAINER)
const host = document.createElement('div')
viewDocument.appendChild(host)  // 动态插入，CSS 优先级可能不够
```

## 解决方案

### 核心思路

**CSS 静态修复 + JavaScript 动态修复**的组合方案：

1. **CSS 设置基础层级和 overflow**
2. **JavaScript 在运行时强制修复所有父容器的 overflow**

### 实施步骤

#### 步骤 1: 调整 CSS 层级关系

**文件**: `src/components/core/forms/art-textbus-editor/index.vue`

**新的层级关系**：
```
999999 - 工具栏（最顶层）
50000  - 协作光标标签（在工具栏之下）
1      - 编辑器内容（最底层）
```

**关键 CSS 代码**：

```scss
// 1. 修复容器的 overflow
.xnote-editor-wrapper {
  overflow: visible; // ✅ 从 hidden 改为 visible
}

.xnote-editor {
  overflow-x: visible; // ✅ 从 hidden 改为 visible
  overflow-y: auto;    // 保持垂直滚动
}

// 2. 提升工具栏 z-index（scoped 样式）
:deep(.left-toolbar),
:deep(.toolbar),
:deep(.inline-toolbar) {
  z-index: 999999 !important;
}

// 3. 降低协作光标 z-index（scoped 样式）
:deep(.remote-caret),
:deep(.remote-cursor),
:deep(.yRemoteSelection) {
  z-index: 50000 !important;
}
```

**全局 CSS 覆盖**（非 scoped）：

```scss
<style lang="scss">
/* 使用更高特异性确保覆盖 XNote 源码 */

/* 左侧工具栏 */
.xnote-editor .left-toolbar,
.xnote-editor-wrapper .left-toolbar,
div.left-toolbar,
.left-toolbar {
  z-index: 999999 !important;
}

/* 行内工具栏 */
.xnote-editor .toolbar,
.toolbar,
.inline-toolbar {
  z-index: 999999 !important;
}

/* 工具栏的下拉菜单 */
.left-toolbar [class*='dropdown'],
.toolbar [class*='dropdown'] {
  z-index: 999999 !important;
}

/* 协作光标 */
.remote-caret,
.yRemoteSelection {
  z-index: 50000 !important;
}
</style>
```

#### 步骤 2: JavaScript 动态修复父容器

**关键函数**：

```typescript
// 🔥 修复工具栏容器的 overflow - 确保工具栏不被裁剪
const fixToolbarContainerOverflow = () => {
  if (!editorRef.value) return

  console.log('🔧 [XNote] 开始修复工具栏容器的 overflow...')

  // 查找所有工具栏元素
  const toolbarSelectors = [
    '.left-toolbar',
    '.toolbar',
    '.inline-toolbar',
    '[class*="toolbar"]'
  ]

  toolbarSelectors.forEach((selector) => {
    const toolbars = editorRef.value?.querySelectorAll(selector)
    if (!toolbars || toolbars.length === 0) return

    toolbars.forEach((toolbar) => {
      console.log('✅ [XNote] 找到工具栏:', toolbar.className)
      
      // 向上遍历所有父容器，设置 overflow: visible
      let parent = toolbar.parentElement
      let level = 0
      while (parent && level < 10) {
        const currentOverflow = window.getComputedStyle(parent).overflow
        if (currentOverflow !== 'visible') {
          console.log(`  📦 修复父容器 (level ${level}):`, parent.className || parent.tagName, `overflow: ${currentOverflow} -> visible`)
          ;(parent as HTMLElement).style.setProperty('overflow', 'visible', 'important')
          ;(parent as HTMLElement).style.setProperty('overflow-x', 'visible', 'important')
          ;(parent as HTMLElement).style.setProperty('overflow-y', 'visible', 'important')
        }
        parent = parent.parentElement
        level++
      }
    })
  })

  console.log('✅ [XNote] 工具栏容器 overflow 修复完成')
}
```

**调用时机**：

```typescript
onMounted(() => {
  initEditor()
  
  // 1. 延迟启动 MutationObserver（实时监听 DOM 变化）
  setTimeout(startCursorObserver, 2000)
  
  // 2. 多次尝试修复（因为工具栏可能延迟插入）
  setTimeout(fixToolbarContainerOverflow, 1000)
  setTimeout(fixToolbarContainerOverflow, 3000)
  setTimeout(fixToolbarContainerOverflow, 5000)
})

// 3. 在 MutationObserver 中也调用（实时修复）
const startCursorObserver = () => {
  cursorObserver = new MutationObserver(() => {
    fixCursorLabelPositions()
    fixToolbarContainerOverflow() // ✅ 每次 DOM 变化都修复
  })
  
  cursorObserver.observe(editorRef.value, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['style', 'class']
  })
  
  // 初始调整
  fixCursorLabelPositions()
  fixToolbarContainerOverflow() // ✅ 初始修复
}
```

## 修改文件清单

- **主要文件**: `src/components/core/forms/art-textbus-editor/index.vue`
  - 修改容器 CSS：`overflow: hidden` → `overflow: visible`
  - 调整 z-index：工具栏 999999，协作光标 50000
  - 新增函数：`fixToolbarContainerOverflow()`
  - 修改函数：`startCursorObserver()` 增加工具栏修复调用
  - 修改生命周期：`onMounted()` 增加多次延迟调用

## 测试验证

### 测试步骤

1. 刷新浏览器，打开开发者工具（F12）
2. 进入协作文档编辑页面
3. 移动鼠标到任意文本行，观察左侧是否出现 `+` 按钮
4. 选中一段文本，观察上方是否弹出格式化工具栏
5. 查看控制台日志，确认工具栏和父容器被正确修复

### 预期控制台日志

```
🔧 [XNote] 开始修复工具栏容器的 overflow...
✅ [XNote] 找到工具栏: left-toolbar
  📦 修复父容器 (level 0): DIV overflow: hidden -> visible
  📦 修复父容器 (level 1): xnote-root overflow: auto -> visible
  📦 修复父容器 (level 2): xnote-editor overflow: auto -> visible
✅ [XNote] 工具栏容器 overflow 修复完成
```

## 关键技术要点

### 1. CSS 特异性规则

- 使用多重选择器提高优先级：`.xnote-editor .left-toolbar`
- 使用元素+类选择器：`div.left-toolbar`
- 使用 `!important` 强制覆盖

### 2. z-index 层级管理

- 工具栏层级 > 光标标签层级 > 内容层级
- 避免使用过高的 z-index（如 999999），但在本例中是必要的

### 3. JavaScript 与 CSS 结合

- CSS 负责基础样式和层级
- JavaScript 负责动态修复运行时问题
- MutationObserver 实时监听 DOM 变化

### 4. 调试技巧

- 使用 `console.log` 追踪修复过程
- 使用 `window.getComputedStyle()` 获取实际生效的样式
- 使用浏览器开发者工具检查元素层级和样式

## 经验总结

### 问题排查方法

1. **确认问题范围**：是 z-index 问题还是 overflow 裁剪问题
2. **检查源码**：查看第三方库（XNote）的默认样式
3. **验证 CSS 优先级**：使用开发者工具查看哪些样式生效
4. **尝试 JavaScript 修复**：当 CSS 无法覆盖时，使用 JavaScript 强制修改

### 最佳实践

1. **分层处理**：
   - CSS 负责静态样式
   - JavaScript 负责动态修复
   - 两者结合，确保所有情况都能覆盖

2. **多次尝试**：
   - 异步插入的元素可能需要延迟处理
   - 使用多个 `setTimeout` 确保修复生效

3. **实时监听**：
   - 使用 `MutationObserver` 监听 DOM 变化
   - 在回调中重新应用修复逻辑

4. **详细日志**：
   - 添加 `console.log` 便于调试
   - 记录修复前后的状态对比

### 避免的坑

1. ❌ 只依赖 CSS `!important` - 可能被内联样式覆盖
2. ❌ 只在 `onMounted` 中修复一次 - 动态插入的元素无法覆盖
3. ❌ 使用 `:deep(*)` 选择器 - 性能差，且可能影响其他元素
4. ❌ 过度使用 z-index - 应该建立清晰的层级体系

## 参考资料

- XNote 官方文档：[GitHub - textbus/xnote](https://github.com/textbus/xnote)
- XNote API 文档：`xnoteapi.md`
- CSS z-index 规范：[MDN - z-index](https://developer.mozilla.org/en-US/docs/Web/CSS/z-index)
- MutationObserver API：[MDN - MutationObserver](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)

## 版本信息

- **修复日期**: 2025-11-18
- **XNote 版本**: 最新版（基于源码 `xnote/` 目录）
- **影响范围**: 协作文档编辑器组件 `src/components/core/forms/art-textbus-editor/index.vue`

---

**备注**: 本文档记录了一次成功的第三方富文本编辑器集成问题修复案例，涉及 CSS 层级管理、容器裁剪处理、以及动态 DOM 修复等技术要点，可作为类似问题的参考方案。

