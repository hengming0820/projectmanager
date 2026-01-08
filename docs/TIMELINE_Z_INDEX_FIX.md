# 时间轴弹窗层级修复方案

## 🎯 问题描述

1. **时间轴事件详情弹窗被外层任务详情弹窗遮盖**
2. **图片预览器闪烁，时而显示时而消失**

## 🔧 解决方案

### 1. 使用 Teleport 传送组件

```vue
<teleport to="body">
  <el-dialog
    v-model="showDetailDialog"
    :z-index="9999"
    :modal="false"
  >
  </el-dialog>
</teleport>
```

**原因**：确保弹窗挂载到 body 根节点，避免被父级容器的 z-index 影响。

### 2. 设置极高的 z-index

```
z-index: 10000  ← 图片预览器（最上层）
z-index: 10001  ← 预览器工具栏和关闭按钮
z-index: 9999   ← 时间轴事件详情弹窗
z-index: 2000+  ← 外层任务详情弹窗（Element Plus 默认）
```

### 3. 禁用遮罩层

```vue
:modal="false"
```

**原因**：避免多层遮罩层叠加导致闪烁。

### 4. 使用 MutationObserver 动态监控

```typescript
watch(showDetailDialog, (newVal) => {
  if (newVal) {
    nextTick(() => {
      // 监听图片预览器的出现
      const observer = new MutationObserver(() => {
        const viewer = document.querySelector('.el-image-viewer__wrapper') as HTMLElement
        if (viewer) {
          viewer.style.zIndex = '10000'
        }
      })

      observer.observe(document.body, {
        childList: true,
        subtree: true
      })
    })
  }
})
```

**原因**：Element Plus 的图片预览器是动态创建的，需要在创建后立即强制设置 z-index。

### 5. 强制设置内联样式

```scss
/* CSS 样式 */
.el-image-viewer__wrapper {
  z-index: 10000 !important;
}

/* JavaScript 强制设置 */
viewer.style.zIndex = '10000'
```

**原因**：内联样式优先级最高，确保不会被覆盖。

## 📋 完整实现

### Template

```vue
<teleport to="body">
  <el-dialog
    v-model="showDetailDialog"
    :title="detailEvent ? getEventTitle(detailEvent.type) : '事件详情'"
    width="600px"
    :close-on-click-modal="true"
    :z-index="9999"
    class="art-timeline-detail-dialog"
    :modal="false"
    destroy-on-close
  >
    <!-- 内容 -->
  </el-dialog>
</teleport>
```

### Script

```typescript
// 显示事件详情
const showEventDetail = (event: TimelineEvent) => {
  detailEvent.value = event
  showDetailDialog.value = true

  // 确保弹窗打开后，强制设置正确的z-index
  nextTick(() => {
    const dialogWrapper = document.querySelector('.art-timeline-detail-dialog') as HTMLElement
    if (dialogWrapper) {
      dialogWrapper.style.zIndex = '9999'
    }
  })
}

// 监听图片预览器的出现
watch(showDetailDialog, (newVal) => {
  if (newVal) {
    nextTick(() => {
      const observer = new MutationObserver(() => {
        const viewer = document.querySelector('.el-image-viewer__wrapper') as HTMLElement
        if (viewer) {
          viewer.style.zIndex = '10000'

          const closeBtn = document.querySelector('.el-image-viewer__close') as HTMLElement
          const actions = document.querySelector('.el-image-viewer__actions') as HTMLElement
          if (closeBtn) closeBtn.style.zIndex = '10001'
          if (actions) actions.style.zIndex = '10001'
        }
      })

      observer.observe(document.body, {
        childList: true,
        subtree: true
      })

      setTimeout(() => observer.disconnect(), 10000)
    })
  }
})
```

### Style

```scss
/* 图片预览器 */
.el-image-viewer__wrapper {
  z-index: 10000 !important;
}

.el-image-viewer__close {
  z-index: 10001 !important;
}

.el-image-viewer__actions {
  z-index: 10001 !important;
}

/* 时间轴详情弹窗 */
.art-timeline-detail-dialog {
  z-index: 9999 !important;

  .el-dialog__wrapper {
    z-index: 9999 !important;
  }

  .el-overlay {
    display: none !important;
  }
}

.el-dialog__wrapper.art-timeline-detail-dialog {
  z-index: 9999 !important;
}
```

## ✅ 预期效果

1. ✅ 时间轴事件详情弹窗始终在外层任务详情弹窗之上
2. ✅ 图片预览器始终在所有弹窗之上
3. ✅ 不会闪烁
4. ✅ 层级稳定
5. ✅ 无遮罩层干扰

## 🎉 测试步骤

1. 打开任务详情弹窗
2. 点击时间轴节点卡片
3. 观察事件详情弹窗是否在最上层
4. 点击截图
5. 观察图片预览器是否稳定显示且不闪烁

---

**修复完成时间：** 2025-10-31
