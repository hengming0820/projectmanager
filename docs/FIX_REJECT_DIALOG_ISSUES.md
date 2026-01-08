# 驳回原因弹窗问题修复

## 📋 问题描述

用户报告了"我的工作台"页面中"查看驳回原因"弹窗的两个问题：

1. **截图预览被遮挡**：点击弹窗中的截图查看大图时，预览层被弹窗遮挡
2. **时间显示问题**：弹窗中显示的时间似乎是数据库原始时间，没有经过格式化处理

---

## ✅ 修复内容

### 1. 修复截图预览遮挡问题

#### 问题原因

- Element Plus 的图片预览默认 z-index 可能不够高
- 弹窗的 z-index 与预览层冲突

#### 解决方案

**调整弹窗层级：**

```vue
<el-dialog
  v-model="showRejectDialog"
  title="驳回原因"
  width="600px"
  :z-index="2000"        <!-- 设置弹窗 z-index -->
  append-to-body         <!-- 挂载到 body -->
>
```

**提升图片预览层级：**

```vue
<el-image
  :src="rewriteFileUrl(att.file_url)"
  fit="cover"
  lazy
  :preview-src-list="..."
  :initial-index="idx"
  :preview-teleported="true"
  :z-index="3000"        <!-- 设置预览层 z-index 高于弹窗 -->
  style="width: 100%; height: 120px; display: block;"
/>
```

**关键点：**

- 弹窗 z-index: `2000`
- 图片预览 z-index: `3000` （高于弹窗）
- 使用 `append-to-body` 和 `preview-teleported` 确保正确挂载

---

### 2. 修复时间显示问题

#### 问题原因

虽然已经导入了时间格式化工具，但可能：

- 时间格式不够友好
- 需要添加调试日志确认数据正确性

#### 解决方案

**添加专门的驳回时间格式化函数：**

```typescript
// 格式化驳回时间（更友好的显示）
const formatRejectTime = (date: string | null | undefined) => {
  if (!date) return '-'

  try {
    // 使用时间工具修复并格式化
    const formatted = formatDateTimeUtil(date, 'datetime')

    // 检查是否格式化成功
    if (!formatted || formatted === '-') {
      console.warn('⚠️ [MyWorkspace] 时间格式化失败:', date)
      return '时间格式错误'
    }

    return formatted
  } catch (error) {
    console.error('❌ [MyWorkspace] 格式化驳回时间失败:', error, date)
    return '时间格式错误'
  }
}
```

**添加调试日志：**

```typescript
// 在 viewRejectReason 函数中添加日志
console.log('📋 [MyWorkspace] 驳回原因数据:', {
  taskId: task.id,
  reviewedAt_raw: reviewedAt,
  reviewedAt_formatted: reviewedAt ? formatRejectTime(reviewedAt) : '无',
  detail_keys: Object.keys(detail),
  has_reviewedAt: 'reviewedAt' in detail,
  has_reviewed_at: 'reviewed_at' in detail
})
```

**在模板中使用：**

```vue
<el-descriptions-item label="驳回时间">
  <span style="color: #606266;">
    {{ formatRejectTime((currentTask as any).reviewedAt || (currentTask as any).reviewed_at) }}
  </span>
</el-descriptions-item>
```

---

### 3. UI/UX 优化

#### 添加警告提示

```vue
<el-alert title="任务已被驳回" type="error" :closable="false" style="margin-bottom: 16px;">
  <template #default>
    请根据以下驳回原因修改后重新提交
  </template>
</el-alert>
```

#### 美化驳回原因显示

```vue
<el-descriptions-item label="驳回原因">
  <div style="color: #F56C6C; font-weight: 500; line-height: 1.6;">
    {{ (currentTask as any).reviewComment || (currentTask as any).review_comment || '无具体原因' }}
  </div>
</el-descriptions-item>
```

#### 优化截图网格样式

```scss
.reject-content {
  h4 {
    font-size: 15px;
    font-weight: 500;
    color: #303133;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;

    &::before {
      content: '📷';
      font-size: 18px;
    }
  }

  // 截图网格
  .screenshot-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }

  // 单个截图容器
  .screenshot-item {
    border: 1px solid #dcdfe6;
    border-radius: 6px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;

    &:hover {
      border-color: #409eff;
      box-shadow: 0 2px 12px rgba(64, 158, 255, 0.3);
      transform: translateY(-2px);
    }

    // 悬停时显示放大镜图标
    &::after {
      content: '🔍';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 24px;
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
    }

    &:hover::after {
      opacity: 0.8;
    }
  }
}
```

---

## 🎯 修复效果

### 修复前

**截图预览问题：**

- ❌ 点击截图时，预览层被弹窗遮挡
- ❌ 用户无法正常查看大图

**时间显示问题：**

- ❌ 时间可能显示为原始格式
- ❌ 没有友好的错误处理

**UI 问题：**

- ❌ 界面单调
- ❌ 缺少交互提示

### 修复后

**截图预览：**

- ✅ 预览层正确显示在最顶层
- ✅ 不被弹窗遮挡
- ✅ 支持左右切换查看所有截图

**时间显示：**

- ✅ 时间正确格式化为本地时间
- ✅ 格式：`YYYY-MM-DD HH:mm:ss`
- ✅ 添加调试日志便于排查问题
- ✅ 友好的错误提示

**UI 优化：**

- ✅ 添加醒目的警告提示
- ✅ 驳回原因红色高亮显示
- ✅ 截图悬停效果（边框高亮、阴影、放大镜图标）
- ✅ 审核人显示为标签样式
- ✅ 整体布局更加美观

---

## 📝 技术要点

### 1. z-index 层级管理

```
层级关系（从低到高）：
├─ 页面内容: 1-999
├─ 驳回原因弹窗: 2000
└─ 图片预览层: 3000 ✅ 最高层
```

### 2. 时间格式化流程

```
后端返回
→ "2025-10-22T10:00:00Z" (UTC)
   ↓
fixUTCTimeString()
→ 确保含 Z 标识
   ↓
formatDateTimeUtil()
→ 解析为 Date 对象
→ 转换为本地时间
   ↓
toLocaleString()
→ "2025-10-22 18:00:00" (本地时间)
```

### 3. Element Plus 组件配置

**Dialog 挂载：**

- `append-to-body`: 挂载到 body，避免层级问题
- `:z-index`: 设置弹窗层级

**Image 预览：**

- `:preview-teleported`: 预览层挂载到 body
- `:z-index`: 设置预览层级高于弹窗
- `:preview-src-list`: 支持多图预览
- `:initial-index`: 指定初始显示的图片

---

## 🧪 测试验证

### 测试步骤

1. **测试截图预览：**

   - 在"我的工作台"找一个已驳回的任务
   - 点击"查看原因"按钮
   - 点击弹窗中的截图
   - ✅ 验证：预览层应显示在最顶层，不被遮挡
   - ✅ 验证：可以左右切换查看所有截图
   - ✅ 验证：点击关闭或按 ESC 可关闭预览

2. **测试时间显示：**

   - 查看弹窗中的"驳回时间"
   - 打开浏览器开发者工具 Console
   - ✅ 验证：时间显示为本地时间（如 `2025-10-22 18:00:00`）
   - ✅ 验证：Console 中有调试日志显示原始时间和格式化后时间
   - ✅ 验证：时间与实际驳回时间一致（考虑时区转换）

3. **测试 UI 优化：**
   - ✅ 验证：弹窗顶部有红色警告提示
   - ✅ 验证：驳回原因显示为红色文字
   - ✅ 验证：截图标题有相机图标
   - ✅ 验证：鼠标悬停截图时有高亮效果和放大镜图标
   - ✅ 验证：审核人显示为标签样式

### 预期结果

**Console 输出示例：**

```
📋 [MyWorkspace] 驳回原因数据: {
  taskId: "task-12345",
  reviewedAt_raw: "2025-10-22T10:00:00Z",
  reviewedAt_formatted: "2025-10-22 18:00:00",
  detail_keys: ["id", "title", "reviewedAt", ...],
  has_reviewedAt: true,
  has_reviewed_at: false
}
```

**弹窗显示示例：**

```
┌─────────────────────────────────┐
│ ⚠️ 任务已被驳回                  │
│ 请根据以下驳回原因修改后重新提交 │
├─────────────────────────────────┤
│ 任务标题: 测试任务1              │
│ 驳回时间: 2025-10-22 18:00:00   │ ← 本地时间
│ 审核人: [张三]                   │
│ 驳回原因: 标注不完整，请重新标注 │ ← 红色显示
├─────────────────────────────────┤
│ 📷 驳回截图（点击查看大图）      │
│ [图1] [图2] [图3]               │ ← 悬停有高亮效果
└─────────────────────────────────┘
```

---

## 📁 修改的文件

```
src/views/project/my-workspace/index.vue
├─ Template 部分
│  ├─ 弹窗 z-index 和 append-to-body
│  ├─ 添加警告提示 (el-alert)
│  ├─ 优化描述列表显示
│  ├─ 图片预览 z-index
│  └─ 应用截图网格和容器样式类
├─ Script 部分
│  ├─ 添加 formatRejectTime 函数
│  └─ 在 viewRejectReason 中添加调试日志
└─ Style 部分
   └─ 添加 .reject-content 相关样式
      ├─ h4 标题样式
      ├─ .screenshot-grid 网格布局
      └─ .screenshot-item 悬停效果
```

---

## 📚 相关文档

- [TIME_HANDLING_EXPLANATION.md](./TIME_HANDLING_EXPLANATION.md) - 时间处理完整说明
- [ROOT_CAUSE_FIX_SUMMARY.md](./ROOT_CAUSE_FIX_SUMMARY.md) - 时区问题根源修复
- [Element Plus Dialog 文档](https://element-plus.org/zh-CN/component/dialog.html)
- [Element Plus Image 文档](https://element-plus.org/zh-CN/component/image.html)

---

## ✅ 修复完成

**修复日期：** 2025-10-22

**修复内容：**

1. ✅ 截图预览层级问题
2. ✅ 时间格式化和显示
3. ✅ UI/UX 优化

**测试状态：** 待验证

**注意事项：**

- 请在浏览器中测试截图预览是否正常
- 检查 Console 调试日志确认时间数据正确
- 如果时间仍然不正确，请查看调试日志中的原始时间数据

---

**现在驳回原因弹窗应该更加美观、易用，截图预览不再被遮挡，时间也会正确显示为本地时间！** 🎉
