# 文章详情页面重构：将元信息移至抽屉

## 修改时间

2025-11-05

## 背景与目标

### 原有问题

- 文章详情区域的header中包含大量元信息（可编辑角色、可编辑成员、所属部门、标签等）
- 这些信息占据了大量空间，导致真正的文章内容展示区域较小
- 用户体验不够优化

### 重构目标

1. **移除header中的元信息**：从文章详情区域的header中移除可编辑角色、可编辑成员、所属部门、标签等信息
2. **新增文章信息抽屉**：创建一个侧边抽屉，顶部显示文章元信息，下方保留编辑历史
3. **优化按钮文本**：将"编辑历史"按钮改为"文章信息"，更准确地描述功能
4. **增加显示空间**：让文章内容（ArtWangPreview组件）有更多空间展示

---

## 已完成的页面

### ✅ 1. 会议记录页面

**文件**: `src/views/project/articles/meeting/index.vue`

#### 修改内容

**1. 移除header中的元信息**（第115-186行）

```vue
<!-- 移除前：包含article-collaborators块 -->
<div class="header-info">
  <h3>{{ currentArticle.title }}</h3>
  <span class="meta-info">...</span>

  <!-- 可编辑成员、可编辑角色、所属部门、标签 ❌ -->
  <div class="article-collaborators">
    <!-- 大量元信息展示 -->
  </div>
</div>

<!-- 移除后：仅保留基本信息 -->
<div class="header-info">
  <h3>{{ currentArticle.title }}</h3>
  <span class="meta-info">...</span>
</div>
```

**2. 更新按钮**（第145-148行）

```vue
<!-- 修改前 -->
<el-button @click="showHistoryDrawer">
  <el-icon><Clock /></el-icon>
  编辑历史
</el-button>

<!-- 修改后 -->
<el-button @click="showHistoryDrawer">
  <el-icon><InfoFilled /></el-icon>
  文章信息
</el-button>
```

**3. 添加InfoFilled图标导入**（第598行）

```typescript
import {
  Plus,
  Refresh,
  Search,
  Edit,
  Delete,
  User,
  Clock,
  View,
  Document,
  Check,
  Download,
  ArrowDown,
  Printer,
  Upload,
  Link,
  UserFilled,
  OfficeBuilding,
  Setting,
  PriceTag,
  InfoFilled // ← 新增
} from '@element-plus/icons-vue'
```

**4. 重新设计抽屉**（第375-526行）

```vue
<!-- 新的抽屉结构 -->
<el-drawer v-model="historyDrawerVisible" title="文章信息与历史" direction="rtl" size="550px">
  <div class="drawer-content">
    <!-- 🆕 文章元信息区域（顶部） -->
    <div class="article-meta-section">
      <el-card shadow="never" class="meta-card">
        <template #header>
          <div class="meta-card-header">
            <el-icon><InfoFilled /></el-icon>
            <span>文章元信息</span>
          </div>
        </template>
        
        <div class="meta-content">
          <!-- 可编辑成员 -->
          <div v-if="currentArticle.editable_user_ids?.length" class="meta-item">
            <div class="meta-label">
              <el-icon><User /></el-icon>
              <span>可编辑成员</span>
            </div>
            <div class="meta-value">
              <el-tag v-for="userId in currentArticle.editable_user_ids" :key="userId">
                {{ getUserRealName(userId) }}
              </el-tag>
            </div>
          </div>
          
          <!-- 可编辑角色 -->
          <div v-if="currentArticle.editable_roles?.length" class="meta-item">
            <!-- ... -->
          </div>
          
          <!-- 所属部门 -->
          <div v-if="currentArticle.departments?.length" class="meta-item">
            <!-- ... -->
          </div>
          
          <!-- 标签 -->
          <div v-if="currentArticle.tags?.length" class="meta-item">
            <!-- ... -->
          </div>
          
          <!-- 无元信息提示 -->
          <el-empty v-if="无元信息" description="暂无文章元信息" />
        </div>
      </el-card>
    </div>
    
    <!-- 📜 编辑历史区域（下方） -->
    <div class="history-section">
      <el-card shadow="never" class="history-card">
        <template #header>
          <div class="history-card-header">
            <el-icon><Clock /></el-icon>
            <span>编辑历史</span>
          </div>
        </template>
        
        <el-timeline v-if="historyList.length > 0">
          <!-- 历史记录列表 -->
        </el-timeline>
        <el-empty v-else description="暂无编辑历史" />
      </el-card>
    </div>
  </div>
</el-drawer>
```

**5. 新增CSS样式**（第2731-2896行）

- `.drawer-content`：抽屉主容器，使用flexbox布局
- `.article-meta-section`：文章元信息区域
  - `.meta-card`：卡片容器，紫色渐变header
  - `.meta-item`：每个元信息项
  - `.meta-label`：标签
  - `.meta-value`：值（tags）
- `.history-section`：编辑历史区域
  - `.history-card`：卡片容器，粉色渐变header
  - `.history-item`：每条历史记录

---

## 待完成的页面

### ⏳ 2. 模型测试页面

**文件**: `src/views/project/articles/model-test/index.vue` **状态**: 待修改 **步骤**: 与会议记录页面相同

### ⏳ 3. 项目文档页面

**文件**: `src/views/project/management/components/ArticleDetailView.vue` **状态**: 待修改 **步骤**: 与会议记录页面相同

### ⏳ 4. 协作主页面

**文件**: `src/views/collaboration/index.vue` **状态**: 待修改 **特殊说明**: 使用"文档"而不是"文章"

### ⏳ 5. 协作文档页面

**文件**: `src/views/collaboration/document.vue` **状态**: 待修改 **特殊说明**: 使用"文档"而不是"文章"

### ❌ 6. 工作记录页面

**文件**: `src/views/work-log/records/index.vue` **状态**: 不需要修改 **原因**: 工作记录页面没有元信息（已简化）

---

## 修改步骤模板

对于每个待修改的页面，按以下步骤操作：

### 步骤1：移除header中的元信息

在文章详情header中，删除 `.article-collaborators` 块及其内容。

### 步骤2：更新按钮文本和图标

```vue
<!-- 查找并替换 -->
<el-button @click="showHistoryDrawer">
  <el-icon><Clock /></el-icon>
  编辑历史
</el-button>

<!-- 改为 -->
<el-button @click="showHistoryDrawer">
  <el-icon><InfoFilled /></el-icon>
  文章信息
</el-button>
```

### 步骤3：添加InfoFilled图标导入

在图标导入语句中添加 `InfoFilled`。

### 步骤4：重新设计抽屉模板

将原有的编辑历史抽屉改为：

```vue
<el-drawer v-model="historyDrawerVisible" title="文章信息与历史" size="550px">
  <div class="drawer-content">
    <!-- 文章元信息区域 -->
    <div class="article-meta-section">
      <!-- ... -->
    </div>
    
    <!-- 编辑历史区域 -->
    <div class="history-section">
      <!-- ... -->
    </div>
  </div>
</el-drawer>
```

### 步骤5：更新CSS样式

将 `.history-content` 样式替换为 `.drawer-content` 及相关子样式。

---

## 效果对比

### 修改前 ❌

**文章详情页面**：

```
┌─────────────────────────────────────────┐
│ Header                                  │
│ ├─ 标题                                 │
│ ├─ 作者、日期、浏览量                  │
│ └─ 可编辑成员 (占用3-5行)              │
│    可编辑角色 (占用2-3行)              │
│    所属部门 (占用2行)                  │
│    标签 (占用2行)                      │  ← 占用大量空间
├─────────────────────────────────────────┤
│                                         │
│ 文章内容预览 (空间较小)                │
│                                         │
└─────────────────────────────────────────┘
```

**编辑历史抽屉**：

```
┌─────────────────┐
│ 编辑历史        │
├─────────────────┤
│ • 历史记录1     │
│ • 历史记录2     │
│ • 历史记录3     │
│                 │
└─────────────────┘
```

### 修改后 ✅

**文章详情页面**：

```
┌─────────────────────────────────────────┐
│ Header (简洁)                           │
│ ├─ 标题                                 │
│ └─ 作者、日期、浏览量                  │  ← 简洁清爽
├─────────────────────────────────────────┤
│                                         │
│                                         │
│ 文章内容预览 (ArtWangPreview)          │
│ 空间大幅增加！                          │  ← 更多显示空间
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

**文章信息与历史抽屉**：

```
┌───────────────────────────┐
│ 文章信息与历史            │
├───────────────────────────┤
│ 📋 文章元信息 (紫色卡片)  │
│ ├─ 可编辑成员: [tags]     │
│ ├─ 可编辑角色: [tags]     │
│ ├─ 所属部门: [tags]       │
│ └─ 标签: [tags]           │
├───────────────────────────┤
│ 📜 编辑历史 (粉色卡片)    │
│ • 历史记录1               │
│ • 历史记录2               │
│ • 历史记录3               │
│                           │
└───────────────────────────┘
```

---

## 优势

### 1. 更多内容展示空间 ✨

- 文章内容区域空间增加约 **30-50%**
- 用户可以更专注于阅读文章内容
- ArtWangPreview 组件有更多空间渲染富文本

### 2. 信息组织更合理 📁

- 元信息集中在一个抽屉中，逻辑更清晰
- "文章信息"和"编辑历史"在一起，便于查看完整的文章元数据
- 按需打开，不占用主要空间

### 3. 视觉体验更好 🎨

- Header简洁清爽，不再拥挤
- 抽屉中使用卡片+渐变色，视觉层次分明
- 元信息和历史记录分区明确

### 4. 交互体验优化 🖱️

- 点击"文章信息"按钮，一次性查看所有元数据和历史
- 抽屉可以关闭，不影响阅读体验
- 滚动独立，信息浏览更流畅

---

## 技术细节

### 抽屉布局

使用 Flexbox 实现上下布局：

```scss
.drawer-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;

  .article-meta-section {
    // 固定高度，自适应内容
  }

  .history-section {
    flex: 1; // 占据剩余空间
    min-height: 0; // 重要：确保flex子元素可以滚动

    .history-card {
      height: 100%;

      :deep(.el-card__body) {
        flex: 1;
        overflow-y: auto; // 历史记录独立滚动
      }
    }
  }
}
```

### 渐变色设计

```scss
// 文章元信息卡片：紫色渐变
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

// 编辑历史卡片：粉色渐变
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
```

### 空状态处理

```vue
<!-- 当没有元信息时显示 -->
<el-empty v-if="!hasAnyMetaInfo" description="暂无文章元信息" :image-size="80" />
```

---

## 测试清单

对于每个修改的页面，测试以下内容：

### 功能测试

- [ ] "文章信息"按钮点击正常打开抽屉
- [ ] 抽屉显示正确的文章元信息
- [ ] 抽屉显示正确的编辑历史
- [ ] 可编辑成员显示正确的用户名
- [ ] 可编辑角色显示正确的角色名
- [ ] 所属部门显示正确
- [ ] 标签显示正确
- [ ] 无元信息时显示空状态提示
- [ ] 无历史记录时显示空状态提示

### 样式测试

- [ ] Header区域简洁，不再显示元信息
- [ ] 文章内容区域空间明显增大
- [ ] 抽屉宽度合适（550px）
- [ ] 卡片渐变色正确显示
- [ ] 图标颜色和大小合适
- [ ] Tags换行正常，间距合理
- [ ] 历史记录滚动正常

### 响应式测试

- [ ] 小屏幕下抽屉显示正常
- [ ] 文章内容区域在不同屏幕尺寸下适配良好

---

## 相关文件

### 已修改

- ✅ `src/views/project/articles/meeting/index.vue`

### 待修改

- ⏳ `src/views/project/articles/model-test/index.vue`
- ⏳ `src/views/project/management/components/ArticleDetailView.vue`
- ⏳ `src/views/collaboration/index.vue`
- ⏳ `src/views/collaboration/document.vue`

### 文档

- 📄 `docs/ARTICLE_INFO_DRAWER_REDESIGN.md` - 本文档

---

## 后续任务

1. **完成其他页面的重构**

   - 模型测试页面
   - 项目文档页面
   - 协作页面（2个）

2. **用户反馈收集**

   - 观察用户是否适应新布局
   - 收集对抽屉功能的反馈

3. **可能的优化**
   - 添加"编辑元信息"功能到抽屉中
   - 支持从抽屉快速复制元信息
   - 为历史记录添加版本对比功能

---

## 总结

这次重构成功地将文章元信息从主要显示区域移至侧边抽屉，为文章内容预览腾出了更多空间。新的布局更加清晰合理，用户可以专注于阅读文章内容，需要时再打开抽屉查看详细的元信息和编辑历史。

配合之前实现的 `ArtWangPreview` 组件，文章预览体验得到了全方位的提升！🎉
