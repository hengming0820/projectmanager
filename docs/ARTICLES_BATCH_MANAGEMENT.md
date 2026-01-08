# 文章批量管理功能

## 📋 功能说明

为"会议记录"和"模型测试"两个页面添加了批量管理功能，支持批量删除和批量编辑文章。

---

## ✅ 功能特性

### 1. 批量管理对话框

#### 功能入口

- 位置：页面头部右侧，紧邻"发布"和"刷新"按钮
- 按钮：**批量管理**
- 图标：⚙️ (Setting)

#### 对话框功能

- **筛选功能**：
  - 搜索标题
  - 筛选部门
  - 筛选分类
  - 重置按钮
- **文章列表**：
  - 按月份分组显示
  - 勾选框批量选择
  - 全选/取消全选
  - 显示文章标题、分类、部门、日期、作者
- **批量操作**：
  - 批量删除
  - 批量编辑

---

### 2. 批量删除

#### 操作流程

1. 勾选要删除的文章
2. 点击"删除选中"按钮
3. 确认删除（显示删除数量）
4. 批量执行删除操作
5. 显示成功/失败统计
6. 自动刷新文章列表

#### 特性

- ✅ 支持批量删除多篇文章
- ✅ 删除前二次确认
- ✅ 显示删除进度统计
- ✅ 自动处理删除失败情况
- ✅ 删除成功后自动刷新列表

---

### 3. 批量编辑

#### 操作流程

1. 勾选要编辑的文章
2. 点击"批量编辑"按钮
3. 打开批量编辑对话框
4. 选择要修改的字段：
   - 修改分类（可选）
   - 修改部门（可选）
5. 确定修改
6. 批量执行更新操作
7. 显示成功/失败统计
8. 自动刷新文章列表

#### 特性

- ✅ 支持批量修改分类
- ✅ 支持批量修改部门
- ✅ 留空则不修改对应字段
- ✅ 显示修改进度统计
- ✅ 自动处理修改失败情况
- ✅ 修改成功后自动刷新列表

---

## 📊 功能对比

| 功能         | 会议记录    | 模型测试    |
| ------------ | ----------- | ----------- |
| **批量删除** | ✅ 支持     | ✅ 支持     |
| **批量编辑** | ✅ 支持     | ✅ 支持     |
| **筛选部门** | ✅ 支持     | ✅ 支持     |
| **筛选分类** | ✅ 支持     | ✅ 支持     |
| **搜索标题** | ✅ 支持     | ✅ 支持     |
| **全选功能** | ✅ 支持     | ✅ 支持     |
| **分组显示** | ✅ 按月分组 | ✅ 按月分组 |

---

## 🎯 使用示例

### 示例1：批量删除旧文章

**场景**：清理2023年的旧会议记录

**操作步骤**：

1. 点击"批量管理"按钮
2. 在搜索框输入"2023"
3. 点击"全选"勾选所有筛选结果
4. 点击"删除选中 (15)"按钮
5. 确认删除
6. 等待删除完成，查看结果统计

**结果**：

```
✅ 成功删除 15 篇文章
```

---

### 示例2：批量修改部门归属

**场景**：将某些会议记录从"研发部算法组"改为"放射科"

**操作步骤**：

1. 点击"批量管理"按钮
2. 在部门筛选中选择"研发部算法组"
3. 勾选需要修改的文章
4. 点击"批量编辑 (8)"按钮
5. 在"修改部门"中选择"放射科"
6. 点击"确定修改"
7. 等待修改完成，查看结果统计

**结果**：

```
✅ 成功修改 8 篇文章
```

---

### 示例3：批量修改分类

**场景**：将某些会议记录的分类从"周会记录"改为"月例会"

**操作步骤**：

1. 点击"批量管理"按钮
2. 在分类筛选中选择"周会记录"
3. 勾选需要修改的文章
4. 点击"批量编辑 (5)"按钮
5. 在"修改分类"中选择"月例会"
6. 点击"确定修改"
7. 等待修改完成，查看结果统计

**结果**：

```
✅ 成功修改 5 篇文章
```

---

## 🔄 修改文件列表

### 修改的文件（2个）

#### 1. **`src/views/project/articles/meeting/index.vue`**

**新增功能**：

- ✅ 批量管理按钮（头部）
- ✅ 批量管理对话框
- ✅ 批量编辑对话框
- ✅ 批量管理状态变量（14个）
- ✅ 批量管理计算属性（3个）
- ✅ 批量管理方法（5个）
- ✅ 批量管理对话框样式

**主要代码**：

```vue
<!-- 批量管理按钮 -->
<el-button @click="showBatchManageDialog = true" size="large">
  <el-icon><Setting /></el-icon>
  批量管理
</el-button>

<!-- 批量管理对话框 -->
<el-dialog v-model="showBatchManageDialog" title="批量管理会议记录" width="850px">
  <!-- 筛选区 + 文章列表 + 操作按钮 -->
</el-dialog>

<!-- 批量编辑对话框 -->
<el-dialog v-model="showBatchEditDialog" title="批量编辑文章" width="600px">
  <!-- 修改分类 + 修改部门 -->
</el-dialog>
```

**新增状态**：

```typescript
const showBatchManageDialog = ref(false)
const showBatchEditDialog = ref(false)
const selectedArticleIds = ref<string[]>([])
const selectAllArticles = ref(false)
const batchSearchText = ref('')
const batchDeptFilter = ref('')
const batchCategoryFilter = ref('')
const batchDeleting = ref(false)
const batchEditing = ref(false)
const batchEditForm = ref({
  category: '',
  departments: [] as string[]
})
```

**新增计算属性**：

```typescript
// 所有部门列表
const allDepartments = computed(() => { ... })

// 筛选后的文章列表
const filteredArticlesForBatch = computed(() => { ... })

// 按月分组的文章列表
const groupedArticlesForBatch = computed(() => { ... })
```

**新增方法**：

```typescript
// 全选/取消全选
const handleSelectAllArticles = () => { ... }

// 清空筛选条件
const clearBatchFilters = () => { ... }

// 批量删除
const batchDeleteArticles = async () => { ... }

// 批量编辑
const batchEditArticles = async () => { ... }

// 监听对话框关闭
watch(() => showBatchManageDialog.value, (val) => { ... })
```

---

#### 2. **`src/views/project/articles/model-test/index.vue`**

**新增功能**：

- ✅ 与会议记录页面完全相同的批量管理功能
- ✅ 唯一区别：对话框标题为"批量管理模型测试"
- ✅ 分类选项不同（功能测试、压力测试、对比测试）

---

## 📝 技术细节

### 1. 筛选逻辑

**实现方式**：

```typescript
const filteredArticlesForBatch = computed(() => {
  let filtered = [...articles.value]

  // 按搜索文本过滤
  if (batchSearchText.value) {
    const searchLower = batchSearchText.value.toLowerCase()
    filtered = filtered.filter((a) => a.title.toLowerCase().includes(searchLower))
  }

  // 按部门过滤
  if (batchDeptFilter.value) {
    filtered = filtered.filter((a) => (a.departments || []).includes(batchDeptFilter.value))
  }

  // 按分类过滤
  if (batchCategoryFilter.value) {
    filtered = filtered.filter((a) => a.category === batchCategoryFilter.value)
  }

  // 按创建时间倒序排序
  return filtered.sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
})
```

**特性**：

- ✅ 多条件组合筛选
- ✅ 实时响应筛选条件变化
- ✅ 按时间倒序排序
- ✅ 大小写不敏感搜索

---

### 2. 批量操作错误处理

**批量删除错误处理**：

```typescript
for (const articleId of selectedArticleIds.value) {
  try {
    await articlesApi.remove(articleId)
    successCount++
  } catch (e) {
    console.error(`删除文章 ${articleId} 失败:`, e)
    failCount++
  }
}

if (successCount > 0) {
  ElMessage.success(
    `成功删除 ${successCount} 篇文章` + (failCount > 0 ? `，失败 ${failCount} 篇` : '')
  )
} else {
  ElMessage.error('删除失败')
}
```

**特性**：

- ✅ 逐个处理，不因单个失败而中断
- ✅ 统计成功和失败数量
- ✅ 显示详细的结果信息
- ✅ 即使部分失败也会刷新列表

---

### 3. 对话框关闭自动清理

**实现方式**：

```typescript
watch(
  () => showBatchManageDialog.value,
  (val) => {
    if (!val) {
      selectedArticleIds.value = []
      selectAllArticles.value = false
      batchSearchText.value = ''
      batchDeptFilter.value = ''
      batchCategoryFilter.value = ''
    }
  }
)
```

**特性**：

- ✅ 关闭对话框自动清空选中
- ✅ 关闭对话框自动清空筛选
- ✅ 确保下次打开对话框状态干净

---

### 4. 分组显示逻辑

**实现方式**：

```typescript
const groupedArticlesForBatch = computed(() => {
  const groups: Record<string, any[]> = {}

  filteredArticlesForBatch.value.forEach((article) => {
    const date = new Date(article.created_at)
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const yearMonth = `${year}年${String(month).padStart(2, '0')}月`

    if (!groups[yearMonth]) {
      groups[yearMonth] = []
    }
    groups[yearMonth].push(article)
  })

  // 按时间倒序排序
  const months = Object.keys(groups).sort((a, b) => b.localeCompare(a))
  return months.map((yearMonth) => ({
    label: yearMonth,
    articles: groups[yearMonth]
  }))
})
```

**特性**：

- ✅ 按年-月分组
- ✅ 月份倒序排列（最新在前）
- ✅ 每个分组显示标题
- ✅ 易于快速定位文章

---

## 🚀 验证步骤

### 测试会议记录

1. **进入会议记录页面**
2. **测试批量删除**：

   - ✅ 点击"批量管理"
   - ✅ 勾选几篇文章
   - ✅ 点击"删除选中"
   - ✅ 确认删除
   - ✅ 验证删除成功

3. **测试批量编辑**：

   - ✅ 点击"批量管理"
   - ✅ 勾选几篇文章
   - ✅ 点击"批量编辑"
   - ✅ 修改分类或部门
   - ✅ 验证修改成功

4. **测试筛选功能**：

   - ✅ 搜索标题
   - ✅ 筛选部门
   - ✅ 筛选分类
   - ✅ 点击"重置"

5. **测试全选功能**：
   - ✅ 点击"全选"
   - ✅ 验证所有文章被选中
   - ✅ 再次点击取消全选

---

### 测试模型测试

1. **进入模型测试页面**
2. **重复上述所有测试步骤**
3. **验证功能与会议记录完全一致**

---

## 💡 使用建议

### 1. 批量删除注意事项

- ⚠️ 删除操作不可恢复，请谨慎操作
- ⚠️ 建议先使用筛选功能缩小范围
- ⚠️ 删除前请仔细确认勾选的文章
- ✅ 建议分批删除，避免一次删除过多

### 2. 批量编辑技巧

- ✅ 可以只修改分类，留空部门
- ✅ 可以只修改部门，留空分类
- ✅ 修改部门支持多选（会覆盖原有部门）
- ✅ 建议修改前使用筛选精确定位

### 3. 筛选功能使用

- ✅ 多条件可组合使用
- ✅ 搜索框支持模糊搜索
- ✅ 筛选后可查看数量（显示在"全选"旁）
- ✅ 使用"重置"快速清空所有筛选

---

## 📚 相关文档

- [文章导航栏部门分组优化](./ARTICLES_NAV_DEPARTMENT_OPTIMIZATION.md)
- [工作日志批量管理](./WORK_LOG_BATCH_MANAGEMENT.md)（参考实现）

---

**版本**: v1.0  
**更新时间**: 2025-10-17  
**功能开发**: AI Assistant
