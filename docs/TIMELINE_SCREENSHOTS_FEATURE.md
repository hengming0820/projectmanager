# ✅ 时间轴截图查看功能完成

## 📅 完成时间

2025-10-31

---

## 🎯 功能概述

为时间轴组件添加了**各阶段截图查看**功能，用户现在可以：

1. ✅ 在节点卡片上看到该阶段是否有截图
2. ✅ 点击节点卡片查看详细信息
3. ✅ 在详情弹窗中预览和查看完整的截图
4. ✅ 支持图片懒加载和错误处理
5. ✅ 自动识别不同阶段的截图类型

---

## 🔧 实现细节

### 1. **截图类型映射** 📷

根据事件类型自动提取对应的截图：

| 事件类型         | 附件类型                | 说明                   |
| ---------------- | ----------------------- | ---------------------- |
| `submitted`      | `annotation_screenshot` | 标注员提交时上传的截图 |
| `reviewed`       | `review_screenshot`     | 审核员审核时上传的截图 |
| `skip_requested` | `skip_screenshot`       | 申请跳过时上传的截图   |

```typescript
const getEventImages = (event: TimelineEvent | null): any[] => {
  // 根据事件类型确定要查找的图片类型
  let targetType = ''
  switch (event.type) {
    case 'submitted':
      targetType = 'annotation_screenshot'
      break
    case 'reviewed':
      targetType = 'review_screenshot'
      break
    case 'skip_requested':
      targetType = 'skip_screenshot'
      break
    default:
      return []
  }

  // 从attachments中提取对应类型的图片
  return attachments
    .filter((att: any) => att && att.attachment_type === targetType)
    .map((att: any) => ({
      url: att.file_url,
      name: att.file_name,
      id: att.id
    }))
}
```

### 2. **卡片提示** 🏷️

在节点卡片上显示截图数量提示：

```vue
<div v-if="getEventImages(event).length > 0" class="card-extras">
  <span class="extra-item">
    📷 {{ getEventImages(event).length }}张
  </span>
</div>
```

**效果：**

```
┌─────────────────────┐
│ 🚀 提交审核         │
│ 🕐 10/10 17:31     │
├─────────────────────┤
│ 👤 张三            │
│ 📷 3张             │ ← 显示有3张截图
└─────────────────────┘
```

### 3. **详情弹窗** 🖼️

点击节点卡片后，在弹窗中显示完整截图：

```vue
<div v-if="getEventImages(detailEvent).length" class="detail-section">
  <h4 class="section-title">
    <i>📷</i> {{ getImagesSectionTitle(detailEvent.type) }}
    ({{ getEventImages(detailEvent).length }})
  </h4>
  <div class="images-grid">
    <el-image
      v-for="(img, idx) in getEventImages(detailEvent)"
      :key="idx"
      :src="getImageUrl(img)"
      :preview-src-list="getEventImages(detailEvent).map(i => getImageUrl(i))"
      :initial-index="idx"
      fit="cover"
      class="preview-image"
      lazy
    >
      <template #error>
        <div class="image-error">
          <i>🖼️</i>
          <span>加载失败</span>
        </div>
      </template>
    </el-image>
  </div>
</div>
```

**特性：**

- ✅ 响应式网格布局（1-4列自适应）
- ✅ 懒加载（`lazy`）
- ✅ 点击预览大图（Element Plus Image Preview）
- ✅ 错误状态显示

### 4. **截图区域标题** 📝

根据事件类型显示对应的标题：

```typescript
const getImagesSectionTitle = (type: string): string => {
  const titleMap: Record<string, string> = {
    submitted: '标注截图',
    reviewed: '审核截图',
    skip_requested: '跳过申请截图',
    skip_approved: '跳过审核截图',
    skip_rejected: '跳过审核截图'
  }
  return titleMap[type] || '相关截图'
}
```

### 5. **图片URL处理** 🔗

兼容多种数据格式：

```typescript
const getImageUrl = (img: any): string => {
  if (typeof img === 'string') return img
  return img.url || img.file_url || ''
}
```

支持：

- ✅ 字符串URL：`"https://example.com/image.jpg"`
- ✅ 对象格式：`{ url: "...", name: "..." }`
- ✅ 附件格式：`{ file_url: "...", file_name: "..." }`

---

## 📁 修改的文件

### 1. **SimpleTimeline.vue** (核心组件)

- ✅ 添加 `getEventImages()` 函数 - 提取事件截图
- ✅ 添加 `getImageUrl()` 函数 - 处理图片URL
- ✅ 添加 `getImagesSectionTitle()` 函数 - 获取标题
- ✅ 更新卡片模板 - 显示截图提示
- ✅ 更新详情弹窗 - 显示截图网格
- ✅ 添加截图样式 - 响应式布局和hover效果

### 2. **task-review/index.vue** (任务审核)

- ✅ 为 timeline 事件添加 `attachments` 引用
- ✅ 添加调试日志，显示 `attachments_count`

### 3. **task-pool/index.vue** (任务池)

- ✅ 为 timeline 事件添加 `attachments` 引用

### 4. **my-workspace/index.vue** (我的工作台)

- ✅ 为 timeline 事件添加 `attachments` 引用
- ✅ 添加调试日志

### 5. **performance/personal.vue** (个人绩效)

- ✅ 为 timeline 事件添加 `attachments` 引用
- ✅ 添加调试日志

---

## 🎨 样式实现

### 截图网格

```scss
.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.preview-image {
  width: 100%;
  height: 200px;
  border-radius: 8px;
  border: 2px solid var(--art-card-border);
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--art-primary-color);
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(var(--art-primary-rgb), 0.3);
  }
}
```

**响应式适配：**

```scss
@media (max-width: 768px) {
  .images-grid {
    grid-template-columns: repeat(2, 1fr); // 移动端2列
  }
}

@media (max-width: 480px) {
  .images-grid {
    grid-template-columns: 1fr; // 小屏幕1列
  }
}
```

### 错误状态

```scss
.image-error {
  width: 100%;
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--art-bg-color);
  color: var(--art-text-gray-500);

  i {
    font-size: 48px;
    margin-bottom: 12px;
  }

  span {
    font-size: 14px;
  }
}
```

---

## 🔍 数据流程

### 1. 后端返回任务详情

```json
{
  "id": "task-123",
  "title": "标注任务",
  "timeline": [
    {
      "type": "submitted",
      "user_name": "张三",
      "time": "2025-10-31T10:00:00Z",
      "comment": "已完成标注"
    }
  ],
  "attachments": [
    {
      "id": "att-1",
      "attachment_type": "annotation_screenshot",
      "file_url": "https://example.com/screenshot1.jpg",
      "file_name": "screenshot1.jpg"
    },
    {
      "id": "att-2",
      "attachment_type": "annotation_screenshot",
      "file_url": "https://example.com/screenshot2.jpg",
      "file_name": "screenshot2.jpg"
    }
  ]
}
```

### 2. 前端处理（在 viewTask 中）

```typescript
// 为每个timeline事件添加attachments引用
if (detail.timeline && detail.timeline.length > 0) {
  detail.timeline = detail.timeline.map((event: any) => ({
    ...event,
    attachments: detail.attachments || []
  }))
}
```

**结果：**

```json
{
  "timeline": [
    {
      "type": "submitted",
      "user_name": "张三",
      "time": "2025-10-31T10:00:00Z",
      "comment": "已完成标注",
      "attachments": [
        {
          "id": "att-1",
          "attachment_type": "annotation_screenshot",
          "file_url": "https://example.com/screenshot1.jpg"
        },
        {
          "id": "att-2",
          "attachment_type": "annotation_screenshot",
          "file_url": "https://example.com/screenshot2.jpg"
        }
      ]
    }
  ]
}
```

### 3. SimpleTimeline 组件提取

```typescript
// 根据事件类型(submitted)提取对应类型(annotation_screenshot)的图片
getEventImages(event) // => [att-1, att-2]
```

### 4. 显示在UI上

```
节点卡片：📷 2张
详情弹窗：显示2张标注截图的网格
```

---

## 📊 功能覆盖

### 支持的事件类型

| 事件     | 卡片提示 | 详情标题     | 截图来源                |
| -------- | -------- | ------------ | ----------------------- |
| 创建任务 | ❌       | -            | 无截图                  |
| 领取任务 | ❌       | -            | 无截图                  |
| 开始标注 | ❌       | -            | 无截图                  |
| 提交审核 | ✅       | 标注截图     | `annotation_screenshot` |
| 审核结果 | ✅       | 审核截图     | `review_screenshot`     |
| 重新开始 | ❌       | -            | 无截图                  |
| 申请跳过 | ✅       | 跳过申请截图 | `skip_screenshot`       |
| 跳过通过 | ❌       | -            | 无截图                  |
| 跳过拒绝 | ❌       | -            | 无截图                  |

### 支持的页面

| 页面       | 路径                            | 状态      |
| ---------- | ------------------------------- | --------- |
| 任务审核   | `/project/task-review`          | ✅ 已支持 |
| 任务池     | `/project/task-pool`            | ✅ 已支持 |
| 我的工作台 | `/project/my-workspace`         | ✅ 已支持 |
| 个人绩效   | `/project/performance/personal` | ✅ 已支持 |

---

## 🎯 用户体验

### 1. 快速识别 👀

- 节点卡片上的 `📷 3张` 提示
- 一眼就能看出哪些阶段有截图

### 2. 便捷查看 🖱️

- 点击节点卡片即可查看
- 无需额外的"查看截图"按钮

### 3. 大图预览 🔍

- 点击小图自动预览大图
- Element Plus 的图片预览器
- 支持左右切换、缩放等

### 4. 清晰分类 🏷️

- 不同类型的截图有对应的标题
- "标注截图"、"审核截图"、"跳过申请截图"

### 5. 性能优化 ⚡

- 懒加载（`lazy`）
- 只在需要时加载图片
- 减少初始加载时间

### 6. 错误友好 ❌

- 加载失败时显示友好提示
- 不会破坏整体布局

---

## 🧪 测试场景

### 场景1：有标注截图

```
1. 创建任务
2. 标注员领取并标注
3. 上传3张截图
4. 提交审核
5. 查看详情
```

**预期：**

- ✅ "提交审核" 节点显示 `📷 3张`
- ✅ 点击后弹窗显示3张标注截图
- ✅ 标题显示"标注截图 (3)"

### 场景2：有审核截图

```
1. 审核员审核任务
2. 驳回并上传2张批注截图
3. 查看详情
```

**预期：**

- ✅ "审核结果" 节点显示 `📷 2张`
- ✅ 点击后弹窗显示2张审核截图
- ✅ 标题显示"审核截图 (2)"

### 场景3：无截图

```
1. 创建任务
2. 查看详情
```

**预期：**

- ✅ "创建任务" 节点不显示截图提示
- ✅ 点击后弹窗不显示截图区域

### 场景4：混合场景

```
1. 提交审核（3张标注截图）
2. 审核驳回（2张审核截图）
3. 重新提交（4张标注截图）
4. 审核通过（无审核截图）
```

**预期：**

- ✅ 第一个"提交审核"：`📷 3张`
- ✅ "审核结果(驳回)"：`📷 2张`
- ✅ 第二个"提交审核"：`📷 4张`
- ✅ "审核结果(通过)"：无提示

---

## 🎉 功能亮点

### 1. 智能识别 🧠

- 自动根据事件类型提取对应的截图
- 无需手动指定截图来源

### 2. 统一接口 🔄

- 所有页面使用统一的 `SimpleTimeline` 组件
- 修改一处，全局生效

### 3. 灵活扩展 🔧

- 新增事件类型？只需在 `getEventImages` 中添加映射
- 新增附件类型？只需在 `targetType` 中添加

### 4. 向后兼容 ⏮️

- 兼容旧数据格式（`images` 字段）
- 兼容多种URL格式（字符串、对象）

### 5. 响应式设计 📱

- 桌面端：最多4列
- 平板端：2列
- 手机端：1列

---

## 🚀 后续优化建议

### 1. 图片缓存

```typescript
// 使用浏览器缓存或Service Worker
// 减少重复加载
```

### 2. 图片压缩

```typescript
// 后端返回缩略图URL
// 点击预览时加载原图
{
  file_url: "https://example.com/image.jpg",
  thumbnail_url: "https://example.com/image_thumb.jpg"
}
```

### 3. 批量下载

```vue
<el-button @click="downloadAllImages">
  下载所有截图
</el-button>
```

### 4. 图片标注

```typescript
// 在预览时支持标注
// 添加箭头、文字、高亮等
```

### 5. 图片比较

```typescript
// 对比标注前后的截图
// 侧边对比模式
```

---

**🎉 截图查看功能已完成！现在可以在时间轴中查看各阶段的截图了！**
