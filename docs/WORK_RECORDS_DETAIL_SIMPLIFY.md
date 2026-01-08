# 工作记录详情页面简化

## 变更说明

工作记录页面是员工日常工作的记录工具，与会议记录、项目文档等有不同的使用场景。为了让页面更简洁、更聚焦，移除了不必要的显示字段。

## 移除的字段

### 1. 可编辑成员（editable_user_ids）

- **原因**：工作记录的权限已在创建时自动设置（只有作者和管理员可编辑），不需要额外展示
- **代码位置**：第112-126行

```vue
<!-- 已移除 -->
<div v-if="currentArticle.editable_user_ids?.length" class="collaborators-inline">
  <span class="collaborators-label">
    <el-icon><User /></el-icon>
    可编辑成员：
  </span>
  <el-tag
    v-for="userId in currentArticle.editable_user_ids"
    :key="userId"
    size="small"
    effect="plain"
  >
    {{ getUserRealName(userId) }}
  </el-tag>
</div>
```

### 2. 可编辑角色（editable_roles）

- **原因**：工作记录不使用角色权限控制，只基于作者和管理员
- **代码位置**：第110行条件判断中包含但未实际显示

```vue
<!-- 已移除条件判断中的 editable_roles -->
<div
  v-if="
    currentArticle.editable_user_ids?.length ||
    currentArticle.editable_roles?.length ||
    currentArticle.departments?.length
  "
></div>
```

### 3. 所属部门（departments）

- **原因**：工作记录已按部门分类展示在左侧导航树中，详情页再显示是重复信息
- **代码位置**：第129-144行

```vue
<!-- 已移除 -->
<div v-if="currentArticle.departments?.length" class="collaborators-inline">
  <span class="collaborators-label">
    <el-icon><OfficeBuilding /></el-icon>
    所属部门：
  </span>
  <el-tag
    v-for="dept in currentArticle.departments"
    :key="dept"
    size="small"
    type="info"
    effect="plain"
  >
    {{ dept }}
  </el-tag>
</div>
```

## 保留的字段

工作记录详情页面现在只显示核心信息：

### 文章头部（meta-info）

- ✅ **分类标签**（category）：如"日常记录"、"问题修复"等
- ✅ **作者信息**（author_name）：记录创建者
- ✅ **更新时间**（updated_at）：最后修改时间
- ✅ **浏览次数**（view_count）：查看统计

### 操作按钮

- ✅ **编辑内容**：作者和管理员可见
- ✅ **删除**：作者和管理员可见
- ✅ **导入Markdown**：编辑模式下可用

## 代码对比

### 修改前（第107-145行）

```vue
</span>

<!-- 可编辑成员（参照会议记录样式） -->
<div v-if="currentArticle.editable_user_ids?.length || currentArticle.editable_roles?.length || currentArticle.departments?.length" class="article-collaborators">
  <!-- 可编辑成员 -->
  <div v-if="currentArticle.editable_user_ids?.length" class="collaborators-inline">
    <span class="collaborators-label">
      <el-icon><User /></el-icon>
      可编辑成员：
    </span>
    <el-tag
      v-for="userId in currentArticle.editable_user_ids"
      :key="userId"
      size="small"
      effect="plain"
      class="collaborator-tag-inline"
    >
      {{ getUserRealName(userId) }}
    </el-tag>
  </div>

  <!-- 部门标签 -->
  <div v-if="currentArticle.departments?.length" class="collaborators-inline">
    <span class="collaborators-label">
      <el-icon><OfficeBuilding /></el-icon>
      所属部门：
    </span>
    <el-tag
      v-for="dept in currentArticle.departments"
      :key="dept"
      size="small"
      type="info"
      effect="plain"
      class="collaborator-tag-inline"
    >
      {{ dept }}
    </el-tag>
  </div>
</div>
```

### 修改后（第107-108行）

```vue
</span>
```

**减少代码行数**：38行 → 1行（减少37行）

## 设计理念

### 工作记录 vs 会议记录/项目文档

| 特性         | 工作记录            | 会议记录/项目文档    |
| ------------ | ------------------- | -------------------- |
| **使用场景** | 个人日常工作记录    | 团队协作文档         |
| **权限控制** | 简单（作者+管理员） | 复杂（多角色多成员） |
| **部门信息** | 已在导航树分类      | 可能跨部门协作       |
| **编辑成员** | 无需展示            | 需要明确展示         |
| **页面重点** | 内容本身            | 协作信息+内容        |

### 信息架构优化

**导航树（左侧）**：

```
研发部算法组
  └─ 张三
      └─ 2025年11月
          └─ 11月05日
              ├─ 工作记录1
              └─ 工作记录2
```

- 部门信息已在第一级展示
- 作者信息已在第二级展示
- 详情页无需重复

**详情页（右侧）**：

- 聚焦：文章标题、内容、基本元数据
- 简洁：只显示必要信息
- 高效：快速浏览和编辑

## 用户体验改进

### 修改前

```
标题：20251105记录测试
分类：日常记录 | 作者：张三 | 更新：2025-11-05 12:38 | 1 次浏览
可编辑成员：user1, user6, user9, user17  ← 冗余
所属部门：研发部算法组  ← 左侧导航已有
```

视觉杂乱，信息重复

### 修改后

```
标题：20251105记录测试
分类：日常记录 | 作者：张三 | 更新：2025-11-05 12:38 | 1 次浏览
```

简洁清晰，聚焦内容

## 权限说明

虽然详情页不再显示"可编辑成员"，但权限控制仍然有效：

### 创建时自动设置

参见 `src/views/project/articles/create/index.vue`：

```javascript
if (isWorkRecord.value) {
  // 工作记录默认权限
  articleData.editable_roles = [] // 不使用角色权限
  articleData.editable_user_ids = [] // 不指定可编辑用户（由后端控制）
  articleData.is_public = true // 公开可见
  articleData.departments = [userDepartment] // 自动归属作者部门
}
```

### 编辑权限判断

参见 `canEditArticle` 函数：

```javascript
const canEditArticle = (article) => {
  if (!article) return false
  const currentUserId = userStore.userId
  const userRoles = userStore.roles

  // 管理员可以编辑
  if (userRoles.includes('admin')) return true

  // 作者可以编辑
  if (article.author_id === currentUserId) return true

  return false
}
```

## 修改文件

- `src/views/work-log/records/index.vue`（第107-145行 → 第107-108行）

## 相关文档

- `docs/WORK_RECORDS_CREATE_SIMPLIFY.md` - 创建页面简化
- `docs/WORK_RECORDS_LAYOUT_FIX_COMPLETE.md` - 布局修复
- `docs/WORK_RECORDS_FEATURE_FINAL.md` - 功能实现

## 更新记录

- **2025-11-05**: 移除可编辑成员、可编辑角色、所属部门显示，简化详情页面

---

**状态**: ✅ 已完成  
**代码行数变化**: -37行  
**用户体验**: ✅ 显著改善
