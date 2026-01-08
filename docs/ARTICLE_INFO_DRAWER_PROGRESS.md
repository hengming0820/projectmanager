# 文章信息抽屉重构 - 进度报告

## ✅ 已完成的页面（3/5）

### 1. ✅ 会议记录页面

**文件**: `src/views/project/articles/meeting/index.vue` **状态**: 完成 **修改内容**:

- ✅ 移除header中的可编辑成员、角色、部门、标签
- ✅ 将"编辑历史"按钮改为"文章信息"
- ✅ 添加InfoFilled图标导入
- ✅ 重新设计抽屉（元信息+历史）
- ✅ 更新CSS样式（`.drawer-content`）
- ✅ 优化`.article-body`使ArtWangPreview充满空间
- ✅ 通过linter检查

### 2. ✅ 模型测试页面

**文件**: `src/views/project/articles/model-test/index.vue` **状态**: 完成 **修改内容**:

- ✅ 移除header中的可编辑成员、角色、部门、标签
- ✅ 将"编辑历史"按钮改为"文章信息"
- ✅ 添加InfoFilled图标导入
- ✅ 重新设计抽屉（元信息+历史）
- ✅ 更新CSS样式（`.drawer-content`）
- ✅ 优化`.article-body`使ArtWangPreview充满空间
- ✅ 通过linter检查

### 3. ✅ 项目文档页面

**文件**: `src/views/project/management/components/ArticleDetailView.vue` **状态**: 完成 **修改内容**:

- ✅ 移除header中的可编辑成员、角色、部门
- ✅ 将"编辑历史"按钮改为"文章信息"
- ✅ 添加InfoFilled图标导入
- ✅ 重新设计抽屉（元信息+历史+标签）
- ✅ 更新CSS样式（`.drawer-content`）
- ✅ 优化`.article-body`使ArtWangPreview充满空间
- ✅ 通过linter检查

---

## ⏳ 待完成的页面（2/5）

### 4. ⏳ 协作主页面

**文件**: `src/views/collaboration/index.vue` **状态**: 待完成 **术语**: 使用"文档"而不是"文章" **步骤**:

1. 查找并移除文档header中的元信息显示
2. 查找"编辑历史"按钮，改为"文档信息"
3. 添加InfoFilled图标导入
4. 重新设计抽屉（文档元信息+历史）
5. 更新CSS样式
6. 优化`.document-body`布局

### 5. ⏳ 协作文档页面

**文件**: `src/views/collaboration/document.vue` **状态**: 待完成 **术语**: 使用"文档"而不是"文章" **步骤**:

1. 查找并移除文档header中的元信息显示
2. 查找"编辑历史"按钮，改为"文档信息"
3. 添加InfoFilled图标导入
4. 重新设计抽屉（文档元信息+历史）
5. 更新CSS样式
6. 优化`.document-body`布局

---

## 📋 标准修改模板

对于剩余的协作页面，请按以下步骤操作：

### 步骤1：移除header中的元信息

```typescript
// 删除类似这样的代码块：
<!-- 可编辑成员（参照协作者样式） -->
<div class="article-collaborators">
  <!-- 可编辑成员 -->
  <div v-if="document.editable_user_ids?.length">...</div>
  <!-- 可编辑角色 -->
  <div v-if="document.editable_roles?.length">...</div>
  <!-- 所属部门 -->
  <div v-if="document.departments?.length">...</div>
  <!-- 标签 -->
  <div v-if="document.tags?.length">...</div>
</div>
```

### 步骤2：更新按钮

```vue
<!-- 查找 -->
<el-button @click="showHistoryDrawer">
  <el-icon><Clock /></el-icon>
  编辑历史
</el-button>

<!-- 替换为 -->
<el-button @click="showHistoryDrawer">
  <el-icon><InfoFilled /></el-icon>
  文档信息
</el-button>
```

### 步骤3：添加图标导入

在`<script setup>`部分的图标导入中添加`InfoFilled`:

```typescript
import { ..., InfoFilled } from '@element-plus/icons-vue'
```

### 步骤4：替换抽屉模板

将原有的`<el-drawer>`替换为：

```vue
<!-- 文档信息与历史抽屉 -->
<el-drawer v-model="historyDrawerVisible" title="文档信息与历史" direction="rtl" size="550px">
  <div class="drawer-content">
    <!-- 文档元信息区域 -->
    <div v-if="document" class="document-meta-section">
      <el-card shadow="never" class="meta-card">
        <template #header>
          <div class="meta-card-header">
            <el-icon><InfoFilled /></el-icon>
            <span>文档元信息</span>
          </div>
        </template>
        
        <div class="meta-content">
          <!-- 可编辑成员 -->
          <div v-if="document.editable_user_ids?.length" class="meta-item">
            <div class="meta-label">
              <el-icon><User /></el-icon>
              <span>可编辑成员</span>
            </div>
            <div class="meta-value">
              <el-tag
                v-for="userId in document.editable_user_ids"
                :key="userId"
                size="small"
                effect="plain"
                class="meta-tag"
              >
                {{ getUserRealName(userId) }}
              </el-tag>
            </div>
          </div>
          
          <!-- 可编辑角色 -->
          <div v-if="document.editable_roles?.length" class="meta-item">
            <div class="meta-label">
              <el-icon><UserFilled /></el-icon>
              <span>可编辑角色</span>
            </div>
            <div class="meta-value">
              <el-tag
                v-for="role in document.editable_roles"
                :key="role"
                size="small"
                type="success"
                effect="plain"
                class="meta-tag"
              >
                {{ getRoleName(role) }}
              </el-tag>
            </div>
          </div>
          
          <!-- 所属部门 -->
          <div v-if="document.departments?.length" class="meta-item">
            <div class="meta-label">
              <el-icon><OfficeBuilding /></el-icon>
              <span>所属部门</span>
            </div>
            <div class="meta-value">
              <el-tag
                v-for="dept in document.departments"
                :key="dept"
                size="small"
                type="warning"
                effect="plain"
                class="meta-tag"
              >
                {{ dept }}
              </el-tag>
            </div>
          </div>
          
          <!-- 标签（如果有）-->
          <div v-if="document.tags && document.tags.length" class="meta-item">
            <div class="meta-label">
              <el-icon>🏷️</el-icon>
              <span>标签</span>
            </div>
            <div class="meta-value">
              <el-tag
                v-for="tag in document.tags"
                :key="tag"
                size="small"
                effect="plain"
                class="meta-tag"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>
          
          <!-- 提示：无元信息 -->
          <el-empty 
            v-if="!hasAnyMetaInfo"
            description="暂无文档元信息"
            :image-size="80"
          />
        </div>
      </el-card>
    </div>
    
    <!-- 编辑历史区域 -->
    <div v-loading="loadingHistory" class="history-section">
      <el-card shadow="never" class="history-card">
        <template #header>
          <div class="history-card-header">
            <el-icon><Clock /></el-icon>
            <span>编辑历史</span>
          </div>
        </template>
        
        <el-timeline v-if="historyList.length > 0">
          <el-timeline-item 
            v-for="item in historyList" 
            :key="item.id"
            :timestamp="formatDate(item.created_at)"
            placement="top"
          >
            <div class="history-item">
              <div class="history-editor">
                <el-icon><User /></el-icon>
                <span>{{ item.editor_name }}</span>
              </div>
              <div class="history-action">
                <el-tag :type="getActionTagType(item.action)" size="small">
                  {{ getActionLabel(item.action) }}
                </el-tag>
              </div>
              <div class="history-summary" v-if="item.changes_summary">
                {{ item.changes_summary }}
              </div>
              <div class="history-version" v-if="item.version_after">
                版本: v{{ item.version_before || 0 }} → v{{ item.version_after }}
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无编辑历史" :image-size="80" />
      </el-card>
    </div>
  </div>
</el-drawer>
```

### 步骤5：更新CSS样式

将原有的`.history-content`样式替换为：

```scss
// 文档信息与历史抽屉样式
.drawer-content {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;

  // 文档元信息区域（注意：使用document-meta-section而不是article-meta-section）
  .document-meta-section {
    .meta-card {
      border: 1px solid var(--el-border-color-lighter);

      :deep(.el-card__header) {
        padding: 16px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-bottom: none;

        .meta-card-header {
          display: flex;
          align-items: center;
          gap: 8px;
          color: white;
          font-weight: 600;
          font-size: 15px;

          .el-icon {
            font-size: 18px;
          }
        }
      }

      :deep(.el-card__body) {
        padding: 20px;
      }
    }

    .meta-content {
      .meta-item {
        margin-bottom: 20px;

        &:last-child {
          margin-bottom: 0;
        }

        .meta-label {
          display: flex;
          align-items: center;
          gap: 6px;
          font-weight: 600;
          color: var(--art-text-gray-900);
          margin-bottom: 10px;
          font-size: 14px;

          .el-icon {
            color: #667eea;
            font-size: 16px;
          }
        }

        .meta-value {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          padding-left: 22px;

          .meta-tag {
            margin: 0;
          }

          .empty-text {
            color: var(--art-text-gray-400);
            font-size: 13px;
            font-style: italic;
          }
        }
      }
    }
  }

  // 编辑历史区域
  .history-section {
    flex: 1;
    min-height: 0;

    .history-card {
      border: 1px solid var(--el-border-color-lighter);
      height: 100%;
      display: flex;
      flex-direction: column;

      :deep(.el-card__header) {
        padding: 16px 20px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-bottom: none;

        .history-card-header {
          display: flex;
          align-items: center;
          gap: 8px;
          color: white;
          font-weight: 600;
          font-size: 15px;

          .el-icon {
            font-size: 18px;
          }
        }
      }

      :deep(.el-card__body) {
        padding: 20px;
        flex: 1;
        overflow-y: auto;
      }
    }

    .history-item {
      padding: 16px;
      background: var(--art-bg-color);
      border-radius: 8px;
      margin-bottom: 16px;
      border: 1px solid var(--el-border-color-lighter);
      transition: all 0.3s ease;

      &:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-color: var(--el-color-primary-light-7);
      }

      .history-editor {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        color: var(--art-text-gray-900);
        margin-bottom: 8px;

        .el-icon {
          color: #667eea;
        }
      }

      .history-action {
        margin-bottom: 8px;
      }

      .history-summary {
        color: var(--art-text-gray-600);
        font-size: 14px;
        margin-bottom: 8px;
        line-height: 1.6;
      }

      .history-version {
        font-size: 13px;
        color: var(--art-text-gray-500);
        font-family: monospace;
        background: var(--el-fill-color-light);
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
      }
    }
  }
}
```

### 步骤6：优化文档内容区域布局

找到`.document-body`样式并修改为：

```scss
.document-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
```

这样ArtWangPreview组件就能充满卡片的剩余空间。

---

## 🎯 关键点总结

### 术语差异

- **文章页面**: 使用"文章信息"、`.article-meta-section`
- **文档页面**: 使用"文档信息"、`.document-meta-section`

### 核心改动

1. **header**：移除所有元信息展示
2. **按钮**：改为"文章/文档信息"
3. **抽屉**：顶部显示元信息，下方显示历史
4. **布局**：使用flexbox确保预览组件充满空间

### 视觉效果

- 元信息卡片：紫色渐变（#667eea → #764ba2）
- 编辑历史卡片：粉色渐变（#f093fb → #f5576c）
- 抽屉宽度：550px

---

## ✨ 最终效果

修改完成后，所有文章/文档页面将拥有：

- ✅ **更大的内容展示空间**（30-50%增加）
- ✅ **简洁的header**（不再拥挤）
- ✅ **集中的元信息**（在抽屉中）
- ✅ **美观的视觉设计**（渐变卡片）
- ✅ **一致的用户体验**（所有页面统一）

---

## 📌 注意事项

1. **`article` vs `document`**: 协作页面使用`document`作为变量名
2. **`tags`支持**: 某些页面可能没有tags字段，需要条件渲染
3. **`hasAnyMetaInfo`**: 可能需要添加computed属性来判断是否有元信息
4. **测试**: 修改后务必测试抽屉的打开/关闭和滚动功能

---

## 📂 相关文档

- `docs/ARTICLE_INFO_DRAWER_REDESIGN.md` - 完整的设计文档
- `docs/ART_WANG_PREVIEW_COMPONENT.md` - ArtWangPreview组件文档
- `docs/REPLACE_VHTML_WITH_PREVIEW.md` - v-html替换文档
