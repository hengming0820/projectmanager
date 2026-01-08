# 文章简介移至抽屉与布局优化

## 修改时间

2025-11-06

## 用户需求

1. ✅ 将文章简介移至文章信息抽屉，让更多空间显示文章内容
2. ✅ 项目列表文章区域对齐优化
3. ✅ 移除文章内容区域的分类标题，将其移至文章信息抽屉
4. ✅ 增强导航栏选中项的视觉效果

---

## 修改内容

### 1. 文章简介移至抽屉

#### 修改的页面

| 页面             | 文件                                                            | 状态 |
| ---------------- | --------------------------------------------------------------- | ---- |
| **项目列表文章** | `src/views/project/management/components/ArticleDetailView.vue` | ✅   |
| **会议记录**     | `src/views/project/articles/meeting/index.vue`                  | ✅   |
| **模型测试**     | `src/views/project/articles/model-test/index.vue`               | ✅   |

#### 修改前

**主内容区域显示简介**：

```vue
<template v-if="!isEditing">
  <div v-if="article.summary" class="article-description">
    <h4>📝 简介</h4>
    <p>{{ article.summary }}</p>
  </div>

  <div class="article-body">
    <ArtWangPreview :content="article.content" height="100%" />
  </div>
</template>
```

#### 修改后

**主内容区域只显示内容**：

```vue
<template v-if="!isEditing">
  <div class="article-body">
    <ArtWangPreview :content="article.content" height="100%" />
  </div>
</template>
```

**抽屉中显示简介（放在首位）**：

```vue
<div class="meta-content">
  <!-- 文章简介 -->
  <div v-if="article.summary" class="meta-item summary-item">
    <div class="meta-label">
      <el-icon><Document /></el-icon>
      <span>简介</span>
    </div>
    <div class="meta-value summary-text">
      {{ article.summary }}
    </div>
  </div>

  <!-- 可编辑成员 -->
  <div v-if="article.editable_user_ids?.length" class="meta-item">
    <!-- ... -->
  </div>
</div>
```

#### 新增CSS样式

```scss
// 简介特殊样式
&.summary-item {
  .summary-text {
    display: block;
    padding: 12px 16px;
    padding-left: 22px;
    background: var(--art-bg-color);
    border-radius: 6px;
    font-size: 14px;
    line-height: 1.6;
    color: var(--art-text-gray-700);
    border-left: 3px solid #667eea;
    white-space: pre-wrap;
    word-break: break-word;
  }
}
```

---

### 2. 项目列表：移除分类标题

#### 修改前

**主内容区域显示分类标签**：

```vue
<div class="header-info">
  <h3>{{ article.title }}</h3>
  <span class="meta-info">
    <el-tag v-if="article.category" size="small">
      {{ article.category }}
    </el-tag>
    <span class="author-info">...</span>
  </span>
</div>
```

#### 修改后

**主内容区域不显示分类**：

```vue
<div class="header-info">
  <h3>{{ article.title }}</h3>
  <span class="meta-info">
    <span class="author-info">
      <el-icon><User /></el-icon>
      {{ article.author_name }}
    </span>
    <span class="date-info">...</span>
  </span>
</div>
```

**抽屉中显示分类（放在首位）**：

```vue
<div class="meta-content">
  <!-- 文章分类 -->
  <div v-if="article.category" class="meta-item">
    <div class="meta-label">
      <el-icon><FolderOpened /></el-icon>
      <span>分类</span>
    </div>
    <div class="meta-value">
      <el-tag
        size="small"
        :color="getCategoryColor(article.category)"
        effect="light"
        class="meta-tag"
      >
        {{ article.category }}
      </el-tag>
    </div>
  </div>

  <!-- 文章简介 -->
  <div v-if="article.summary" class="meta-item summary-item">
    <!-- ... -->
  </div>
</div>
```

---

### 3. 增强导航栏选中效果

#### 文件

`src/views/project/management/index-new.vue`

#### 修改前

**简单的背景色高亮**：

```scss
&.active {
  background: rgba(var(--art-primary-rgb), 0.12);
  color: var(--art-primary-color);
  font-weight: 500;
}
```

#### 修改后

**更明显的渐变背景 + 左侧边框 + 阴影**：

```scss
&.active {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.08) 100%);
  color: var(--art-primary-color);
  font-weight: 600;
  border-left: 3px solid #667eea;
  padding-left: 5px !important;
  box-shadow: 0 1px 3px rgba(102, 126, 234, 0.1);

  .node-icon {
    color: #667eea;
    transform: scale(1.1);
  }

  .node-label {
    color: #667eea;
  }
}
```

---

### 4. 布局对齐优化

#### 文件

`src/views/project/management/components/ArticleDetailView.vue`

#### CSS调整

**1. 卡片头部padding增加**：

```scss
.article-card :deep(.el-card__header) {
  padding: 20px 24px; // 从 10px 增加到 20px 24px
  border-bottom: 1px solid #f0f0f0;
  background: var(--art-bg-color);
  flex-shrink: 0;
}
```

**2. 内容区域padding优化**：

```scss
.article-content {
  padding: 0 24px 24px 24px; // 顶部无padding，左右下有padding
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
}
```

**3. 文章主体顶部间距**：

```scss
.article-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  margin-top: 20px; // 添加顶部间距，与标题区域分离
}
```

---

## 效果对比

### 简介显示位置

| 位置             | 修改前      | 修改后             |
| ---------------- | ----------- | ------------------ |
| **主内容区**     | ✅ 显示简介 | ❌ 不显示          |
| **文章信息抽屉** | ❌ 不显示   | ✅ 显示（首位）    |
| **内容空间**     | 少          | **多了约80-120px** |

### 分类显示位置（项目列表）

| 位置             | 修改前          | 修改后          |
| ---------------- | --------------- | --------------- |
| **主内容标题**   | ✅ 显示分类标签 | ❌ 不显示       |
| **文章信息抽屉** | ❌ 不显示       | ✅ 显示（首位） |
| **视觉清爽度**   | 中等            | **更清爽**      |

### 导航栏选中效果

| 特性         | 修改前   | 修改后           |
| ------------ | -------- | ---------------- |
| **背景**     | 浅色纯色 | 渐变色           |
| **边框**     | 无       | 3px左侧蓝色边框  |
| **字体粗细** | 500      | 600（更粗）      |
| **阴影**     | 无       | 有（淡淡的阴影） |
| **图标**     | 无变化   | 放大1.1倍 + 蓝色 |
| **可见性**   | ⭐⭐⭐   | ⭐⭐⭐⭐⭐       |

### 内容对齐

| 项目         | 修改前           | 修改后            |
| ------------ | ---------------- | ----------------- |
| **卡片头部** | 10px padding     | 20px 24px padding |
| **内容区域** | 24px 四周padding | 0 24px 24px 24px  |
| **主体顶部** | 无间距           | 20px间距          |
| **视觉对齐** | 中等             | **更好**          |

---

## 布局原理

### 抽屉内容顺序

```
文章信息与历史抽屉
├─ 文章元信息卡片
│  ├─ 📁 分类（新增，项目列表独有）
│  ├─ 📝 简介（新增，所有页面）
│  ├─ 👤 可编辑成员
│  ├─ 👥 可编辑角色
│  ├─ 🏢 所属部门
│  └─ 🏷️ 标签
└─ 编辑历史卡片
   └─ 历史记录列表
```

**优势**：

- ✅ 分类和简介放在最前面，易于查看
- ✅ 逻辑顺序清晰：内容摘要 → 权限 → 历史
- ✅ 主内容区域更清爽，专注于文章正文

### 内容区域布局

```
article-card
├─ card-header (padding: 20px 24px)
│  └─ article-header
│     ├─ header-info
│     │  ├─ h3 (标题)
│     │  └─ meta-info (作者、日期等)
│     └─ header-actions (按钮)
└─ card-body (padding: 0)
   └─ article-content (padding: 0 24px 24px 24px)
      └─ article-body (margin-top: 20px)
         └─ ArtWangPreview (flex: 1)
```

**关键点**：

1. 卡片头部有合适的padding (20px 24px)
2. 卡片主体无padding（由子元素控制）
3. 内容区域左右下有padding (24px)
4. 文章主体顶部有margin (20px)，与标题区分离

---

## 修改的文件总结

| 文件 | 修改内容 | 行数变化 |
| --- | --- | --- |
| `src/views/project/management/components/ArticleDetailView.vue` | 1. 简介移至抽屉<br>2. 分类移至抽屉<br>3. 布局padding调整<br>4. 删除旧CSS | ~50行 |
| `src/views/project/articles/meeting/index.vue` | 1. 简介移至抽屉<br>2. 删除旧CSS<br>3. 新增简介样式 | ~40行 |
| `src/views/project/articles/model-test/index.vue` | 1. 简介移至抽屉<br>2. 删除旧CSS<br>3. 新增简介样式 | ~40行 |
| `src/views/project/management/index-new.vue` | 增强导航栏active样式 | ~15行 |

---

## 关键CSS改进

### 1. 简介样式（抽屉中）

```scss
&.summary-item {
  .summary-text {
    display: block;
    padding: 12px 16px;
    padding-left: 22px;
    background: var(--art-bg-color);
    border-radius: 6px;
    font-size: 14px;
    line-height: 1.6;
    color: var(--art-text-gray-700);
    border-left: 3px solid #667eea; // 蓝色左边框
    white-space: pre-wrap; // 保留换行
    word-break: break-word; // 长词换行
  }
}
```

### 2. 导航栏选中样式

```scss
&.active {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.08) 100%);
  color: var(--art-primary-color);
  font-weight: 600;
  border-left: 3px solid #667eea;
  padding-left: 5px !important;
  box-shadow: 0 1px 3px rgba(102, 126, 234, 0.1);

  .node-icon {
    color: #667eea;
    transform: scale(1.1);
  }

  .node-label {
    color: #667eea;
  }
}
```

### 3. 内容区域对齐

```scss
.article-card :deep(.el-card__header) {
  padding: 20px 24px; // 增加padding
}

.article-content {
  padding: 0 24px 24px 24px; // 顶部无padding
}

.article-body {
  margin-top: 20px; // 与标题分离
}
```

---

## 用户体验改进

### ✅ 优势

1. **更多内容空间**

   - 移除简介后，文章正文可见区域增加约80-120px
   - 用户可以看到更多文章内容，减少滚动

2. **信息架构更清晰**

   - 主内容区专注于文章正文
   - 元数据（分类、简介、权限）统一在抽屉中
   - 信息层次分明

3. **导航更明确**

   - 选中项有明显的视觉反馈
   - 渐变背景 + 左侧边框 + 阴影
   - 图标放大 + 颜色变化
   - 一眼就能看出当前位置

4. **布局更协调**
   - 标题和内容正确对齐
   - 适当的间距和留白
   - 视觉平衡感更好

### 🎯 适用场景

| 场景           | 改进                       |
| -------------- | -------------------------- |
| **阅读长文章** | 可见内容更多，阅读体验更好 |
| **快速浏览**   | 主界面更清爽，重点更突出   |
| **查看元信息** | 打开抽屉，信息集中显示     |
| **切换文章**   | 导航高亮明显，知道当前位置 |

---

## 测试检查清单

### 功能测试

- [x] 项目列表：简介移至抽屉
- [x] 项目列表：分类移至抽屉
- [x] 项目列表：主内容区不显示简介和分类
- [x] 会议记录：简介移至抽屉
- [x] 会议记录：主内容区不显示简介
- [x] 模型测试：简介移至抽屉
- [x] 模型测试：主内容区不显示简介
- [x] 导航栏：选中项高亮明显
- [x] 布局：标题和内容对齐

### 视觉测试

- [x] 抽屉中简介样式美观
- [x] 抽屉中分类标签正确显示
- [x] 导航栏active状态明显
- [x] 内容区域padding合适
- [x] 文章主体与标题间距适当

### 响应式测试

- [x] 窗口缩放时布局正常
- [x] 抽屉打开关闭正常
- [x] 长简介文本换行正常
- [x] 导航栏滚动时选中效果保持

---

## 技术要点

### 1. 保持简介格式

```scss
.summary-text {
  white-space: pre-wrap; // 保留原有换行
  word-break: break-word; // 长词自动换行
}
```

### 2. 视觉层次

```
主内容区：白色背景，干净清爽
  ↓
抽屉：浅灰色背景，信息密集
  ↓
简介：浅色背景框 + 蓝色左边框，突出显示
```

### 3. 选中反馈

```
正常状态 → hover状态 → active状态
   ↓          ↓            ↓
 无背景    浅灰背景     渐变蓝紫背景 + 边框 + 阴影
```

---

## 最佳实践

### ✅ DO - 推荐做法

1. **元数据集中管理**

   - 将所有元数据放在抽屉中
   - 主内容区只显示核心内容

2. **视觉层次分明**

   - 使用不同的背景色区分区域
   - 重要信息用边框突出

3. **选中状态明显**

   - 多种视觉元素组合（颜色 + 边框 + 阴影）
   - 图标也要有反馈

4. **合理的间距**
   - 标题和内容之间有适当间距
   - 内容区域有呼吸空间

### ❌ DON'T - 避免的做法

1. **不要在主内容区堆砌元信息**

   ```vue
   <!-- ❌ 不好 -->
   <div class="article-content">
     <div>分类: {{ category }}</div>
     <div>简介: {{ summary }}</div>
     <div>标签: {{ tags }}</div>
     <div>文章内容...</div>
   </div>
   ```

2. **不要选中状态不明显**

   ```scss
   /* ❌ 不好 - 颜色太淡 */
   &.active {
     background: rgba(0, 0, 0, 0.05);
   }
   ```

3. **不要内容与标题贴太紧**
   ```scss
   /* ❌ 不好 - 没有间距 */
   .article-body {
     margin-top: 0;
   }
   ```

---

## 总结

✅ **已完成的改进**

1. **空间优化**

   - 简介移至抽屉，释放主内容空间
   - 文章可见区域增加约80-120px

2. **信息架构**

   - 分类移至抽屉（项目列表）
   - 元数据集中管理，逻辑更清晰

3. **视觉优化**

   - 导航栏选中效果明显
   - 内容区域对齐优化
   - 布局更协调美观

4. **用户体验**
   - 阅读体验更好
   - 信息查找更方便
   - 导航更清晰

🎉 **文章页面现在更清爽、更专注于内容展示，同时元数据管理更规范！**
