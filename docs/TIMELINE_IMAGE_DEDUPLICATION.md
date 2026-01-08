# 时间轴图片去重修复

## 🐛 问题描述

**现象：** 管理员审核时上传了1张截图，但在时间轴详情弹窗中显示了2张相同的截图。

**原因：**

1. 后端可能返回了重复的attachments数据
2. 前端没有对图片列表进行去重处理
3. 每次渲染时重复计算图片列表

---

## ✅ 解决方案

### 1. **添加URL去重逻辑**

使用 `Map` 数据结构，以图片URL为key进行去重：

```typescript
// 根据URL去重（使用Map保证唯一性）
const uniqueImages = Array.from(new Map(images.map((img) => [img.url, img])).values())
```

**原理：**

- Map的key必须唯一
- 相同URL的图片会被自动覆盖
- 只保留最后一个

### 2. **添加重复检测日志**

```typescript
console.log('✅ [Timeline] 找到匹配截图:', uniqueImages.length, '去重前:', images.length)
if (uniqueImages.length !== images.length) {
  console.warn('⚠️ [Timeline] 检测到重复图片！', {
    原始数量: images.length,
    去重后数量: uniqueImages.length,
    重复图片: images.filter((img, idx, arr) => arr.findIndex((i) => i.url === img.url) !== idx)
  })
}
```

**用途：**

- 在控制台明确显示是否有重复
- 显示重复图片的具体信息
- 便于追踪问题根源

### 3. **处理已有images字段的去重**

```typescript
// 对已有images进行去重
const uniqueImages = Array.from(
  new Map(
    (event as any).images.map((img: any) => {
      const url = typeof img === 'string' ? img : img.url || img.file_url
      return [url, img]
    })
  ).values()
)
```

**兼容性：**

- 支持字符串URL格式：`"http://..."`
- 支持对象格式：`{url: "...", name: "..."}`
- 支持附件格式：`{file_url: "...", file_name: "..."}`

### 4. **使用computed缓存图片列表**

```typescript
// 缓存当前详情事件的图片列表
const detailEventImages = computed(() => getEventImages(detailEvent.value))

// 缓存当前详情事件的图片URL列表（用于预览）
const detailEventImageUrls = computed(() => detailEventImages.value.map((img) => getImageUrl(img)))
```

**优势：**

- 只计算一次，避免重复调用
- 响应式更新
- 性能更好

### 5. **优化模板引用**

**之前：**

```vue
<el-image
  v-for="(img, idx) in getEventImages(detailEvent)"
  :key="idx"
  :src="getImageUrl(img)"
  :preview-src-list="getEventImages(detailEvent).map((i) => getImageUrl(i))"
/>
```

- 每张图片都调用 `getEventImages(detailEvent)`
- 每张图片都重新计算 `preview-src-list`
- 重复计算多次

**现在：**

```vue
<el-image
  v-for="(img, idx) in detailEventImages"
  :key="img.id || img.url || idx"
  :src="getImageUrl(img)"
  :preview-src-list="detailEventImageUrls"
/>
```

- 使用缓存的 `detailEventImages`
- 使用缓存的 `detailEventImageUrls`
- 只计算一次
- 使用唯一key（优先使用id或url）

---

## 📊 去重算法

### Map去重原理

```typescript
const images = [
  { url: 'http://example.com/1.jpg', id: 'a', name: 'img1' },
  { url: 'http://example.com/1.jpg', id: 'b', name: 'img1' }, // 重复URL
  { url: 'http://example.com/2.jpg', id: 'c', name: 'img2' }
]

// 使用Map去重
const uniqueImages = Array.from(new Map(images.map((img) => [img.url, img])).values())[
  // 结果：
  ({ url: 'http://example.com/1.jpg', id: 'b', name: 'img1' }, // 保留后者
  { url: 'http://example.com/2.jpg', id: 'c', name: 'img2' })
]
```

### 步骤分解

1. **映射为[key, value]数组**

   ```typescript
   images.map((img) => [img.url, img])
   // [
   //   ["http://example.com/1.jpg", {url: "...", id: "a"}],
   //   ["http://example.com/1.jpg", {url: "...", id: "b"}],
   //   ["http://example.com/2.jpg", {url: "...", id: "c"}]
   // ]
   ```

2. **创建Map（自动去重）**

   ```typescript
   new Map([...])
   // Map {
   //   "http://example.com/1.jpg" => {url: "...", id: "b"},  // 后者覆盖前者
   //   "http://example.com/2.jpg" => {url: "...", id: "c"}
   // }
   ```

3. **提取values**
   ```typescript
   map.values()
   // [{url: "...", id: "b"}, {url: "...", id: "c"}]
   ```

---

## 🔍 诊断流程

### 控制台输出示例

#### 无重复情况：

```
📦 [Timeline] 事件attachments总数: 5 事件类型: reviewed
🎯 [Timeline] 查找截图类型: review_screenshot
🔍 [Timeline] 检查attachment: {id: "att-1", type: "review_screenshot", url: "...", matches: true}
✅ [Timeline] 找到匹配截图: 1 去重前: 1
```

#### 有重复情况：

```
📦 [Timeline] 事件attachments总数: 5 事件类型: reviewed
🎯 [Timeline] 查找截图类型: review_screenshot
🔍 [Timeline] 检查attachment: {id: "att-1", type: "review_screenshot", url: "/api/files/xxx.jpg", matches: true}
🔍 [Timeline] 检查attachment: {id: "att-2", type: "review_screenshot", url: "/api/files/xxx.jpg", matches: true}
✅ [Timeline] 找到匹配截图: 1 去重前: 2
⚠️ [Timeline] 检测到重复图片！
  原始数量: 2
  去重后数量: 1
  重复图片: [{url: "/api/files/xxx.jpg", id: "att-2", name: "xxx.jpg"}]
```

### 如何诊断

1. **打开浏览器控制台**（F12）
2. **点击时间轴节点卡片**
3. **查看控制台输出**：

   - 看到 `去重前: X 去重后: Y`
   - 如果 X > Y，说明有重复
   - 查看 `重复图片` 列表，确认重复的URL

4. **进一步排查**：
   - 如果重复图片的 `id` 不同但 `url` 相同 → 后端返回了重复数据
   - 如果重复图片的 `id` 和 `url` 都相同 → 前端处理有问题

---

## 🎯 性能优化

### 优化前

```vue
<!-- 模板中多次调用 -->
<div v-if="getEventImages(detailEvent).length">  <!-- 调用1次 -->
  <span>{{ getEventImages(detailEvent).length }}</span>  <!-- 调用2次 -->
  <el-image
    v-for="img in getEventImages(detailEvent)"  <!-- 调用3次 -->
    :preview-src-list="getEventImages(detailEvent).map(...)"  <!-- 每个图片都调用1次 -->
  />
</div>
```

**问题：**

- 假设有3张图片
- `getEventImages` 被调用 3 + 3 = 6次
- 每次都重新过滤和映射attachments

### 优化后

```vue
<!-- 使用computed缓存 -->
<div v-if="detailEventImages.length">  <!-- 使用缓存 -->
  <span>{{ detailEventImages.length }}</span>  <!-- 使用缓存 -->
  <el-image
    v-for="img in detailEventImages"  <!-- 使用缓存 -->
    :preview-src-list="detailEventImageUrls"  <!-- 使用缓存 -->
  />
</div>
```

**改进：**

- `getEventImages` 只被调用1次
- `map(img => getImageUrl(img))` 只被调用1次
- 后续访问都使用缓存值

### 性能对比

| 操作               | 优化前      | 优化后  |
| ------------------ | ----------- | ------- |
| getEventImages调用 | 6次+        | 1次     |
| map映射操作        | 每个图片1次 | 总共1次 |
| 重复计算           | 是          | 否      |
| 响应速度           | 慢          | 快      |

---

## ✅ 测试步骤

1. **找一个有审核截图的任务**
2. **打开控制台（F12）**
3. **点击时间轴的"审核结果"节点**
4. **检查控制台输出**：
   - 看 `去重前` 和 `去重后` 的数量
   - 如果有差异，说明成功去重
5. **查看弹窗中的截图数量**
6. **点击截图预览**，确认预览列表正确

### 预期结果

- ✅ 弹窗显示的截图数量 = 实际上传的数量
- ✅ 没有重复的图片
- ✅ 控制台有清晰的日志
- ✅ 如果检测到重复，会显示警告

---

## 📝 修改的代码

### 文件：`src/components/custom/SimpleTimeline.vue`

#### 1. 添加computed缓存

```typescript
const detailEventImages = computed(() => getEventImages(detailEvent.value))
const detailEventImageUrls = computed(() => detailEventImages.value.map((img) => getImageUrl(img)))
```

#### 2. 修改getEventImages函数

- ✅ 添加URL去重逻辑
- ✅ 添加重复检测和警告日志
- ✅ 处理已有images字段的去重

#### 3. 优化模板

- ✅ 使用computed值替代函数调用
- ✅ 使用唯一key（id或url）
- ✅ 缓存preview-src-list

---

## 🎉 修复完成

### 解决的问题

1. ✅ 图片重复显示
2. ✅ 性能问题（重复计算）
3. ✅ 诊断困难（缺少日志）

### 新增功能

1. ✅ 自动去重
2. ✅ 详细日志
3. ✅ 性能优化
4. ✅ 兼容多种数据格式

---

**修复时间：** 2025-10-31
