<template>
  <el-dialog
    v-model="visible"
    title="管理文章分类"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 分类列表 -->
    <div class="category-list">
      <div class="list-header">
        <h4>当前分类</h4>
        <el-button @click="handleAdd" type="primary" size="small">
          <el-icon><Plus /></el-icon>
          添加分类
        </el-button>
      </div>

      <el-table :data="categories" v-loading="loading" style="width: 100%">
        <el-table-column prop="icon" label="图标" width="80" align="center">
          <template #default="{ row }">
            <span style="font-size: 20px">{{ row.icon || '📄' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="分类名称" min-width="120" />
        <el-table-column prop="type" label="类型标识" min-width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button @click="handleEdit(row)" type="primary" link size="small">编辑</el-button>
            <el-button @click="handleDeleteClick(row)" type="danger" link size="small">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑/新增对话框 -->
    <el-dialog
      v-model="showFormDialog"
      :title="editingCategory ? '编辑分类' : '添加分类'"
      width="600px"
      append-to-body
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <!-- 快速选择预定义分类 -->
        <el-form-item label="快速选择" v-if="!editingCategory">
          <div class="quick-select-container">
            <div
              v-for="template in categoryTemplates"
              :key="template.type"
              @click="selectTemplate(template)"
              :class="['template-card', { active: form.name === template.name }]"
            >
              <div class="template-icon">{{ template.icon }}</div>
              <div class="template-info">
                <div class="template-name">{{ template.name }}</div>
                <div class="template-desc">{{ template.description }}</div>
              </div>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="分类名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="例如：需求文档"
            @input="onNameChange"
            size="large"
          />
        </el-form-item>

        <el-form-item label="类型标识" prop="type">
          <el-input
            v-model="form.type"
            placeholder="例如：requirement"
            :disabled="!!editingCategory"
            size="large"
          >
            <template #prepend>
              <el-icon><Tickets /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">用于文章类型，只能包含字母、数字和下划线</div>
        </el-form-item>

        <el-form-item label="选择图标" prop="icon">
          <div class="icon-selector-enhanced">
            <div class="current-icon-display">
              <span class="current-icon">{{ form.icon || '📄' }}</span>
              <span class="current-icon-label">当前图标</span>
            </div>
            <div class="icon-grid">
              <span
                v-for="icon in commonIcons"
                :key="icon"
                @click="form.icon = icon"
                :class="['icon-item', { selected: form.icon === icon }]"
                :title="icon"
              >
                {{ icon }}
              </span>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="2"
            placeholder="可选，对分类的简要说明"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="排序">
          <el-input-number
            v-model="form.sort_order"
            :min="0"
            :max="999"
            controls-position="right"
            size="large"
          />
          <span class="form-tip" style="margin-left: 12px">数字越小越靠前</span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showFormDialog = false">取消</el-button>
        <el-button @click="handleSave" type="primary" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
  import { ref, watch } from 'vue'
  import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
  import { Plus, Tickets } from '@element-plus/icons-vue'
  import { projectCategoryApi, type ProjectCategory } from '@/api/projectCategoryApi'
  import { articlesApi } from '@/api/articlesApi'

  interface Props {
    modelValue: boolean
    projectId: string
    projectName: string
  }

  const props = defineProps<Props>()

  const emit = defineEmits<{
    'update:modelValue': [value: boolean]
    refresh: []
  }>()

  const visible = ref(props.modelValue)
  const loading = ref(false)
  const saving = ref(false)
  const categories = ref<ProjectCategory[]>([])
  const showFormDialog = ref(false)
  const editingCategory = ref<ProjectCategory | null>(null)
  const formRef = ref<FormInstance>()

  interface FormData {
    name: string
    type: string
    icon: string
    description: string
    sort_order: number
  }

  const form = ref<FormData>({
    name: '',
    type: '',
    icon: '',
    description: '',
    sort_order: 0
  })

  const rules: FormRules = {
    name: [
      { required: true, message: '请输入分类名称', trigger: 'blur' },
      { min: 1, max: 100, message: '名称长度为 1-100 个字符', trigger: 'blur' }
    ],
    type: [
      { required: true, message: '请输入类型标识', trigger: 'blur' },
      { min: 1, max: 50, message: '类型长度为 1-50 个字符', trigger: 'blur' },
      { pattern: /^[a-zA-Z0-9_]+$/, message: '类型只能包含字母、数字和下划线', trigger: 'blur' }
    ]
  }

  // 预定义的分类模板
  const categoryTemplates = [
    { name: '需求文档', type: 'requirement', icon: '📋', description: '项目需求、规格说明等文档' },
    { name: '协作文档', type: 'collaboration', icon: '🤝', description: '团队协作、沟通记录等' },
    { name: '工作记录', type: 'worklog', icon: '📝', description: '日常工作记录、进展报告等' },
    { name: '其他', type: 'other', icon: '📦', description: '其他类型的文档' }
  ]

  // 常用图标列表
  const commonIcons = [
    '📋',
    '📝',
    '📄',
    '📑',
    '📊',
    '📈',
    '🤝',
    '💼',
    '📦',
    '🗂️',
    '📌',
    '🔖',
    '✅',
    '⚡',
    '🎯',
    '🚀',
    '💡',
    '🔧',
    '🧪',
    '📐',
    '🎨',
    '📱',
    '💻',
    '🌐'
  ]

  // 中文转拼音的简单映射（仅用于常用词）
  const pinyinMap: Record<string, string> = {
    需求: 'xuqiu',
    文档: 'wendang',
    协作: 'xiezuo',
    工作: 'gongzuo',
    记录: 'jilu',
    其他: 'qita',
    会议: 'huiyi',
    模型: 'moxing',
    测试: 'ceshi',
    设计: 'sheji',
    开发: 'kaifa',
    部署: 'bushu',
    运维: 'yunwei',
    日志: 'rizhi',
    报告: 'baogao',
    总结: 'zongjie',
    计划: 'jihua',
    任务: 'renwu',
    项目: 'xiangmu',
    产品: 'chanpin',
    技术: 'jishu',
    方案: 'fangan',
    流程: 'liucheng',
    规范: 'guifan',
    评审: 'pingshen',
    验收: 'yanshou'
  }

  // 将中文转换为类型标识
  const convertToType = (name: string): string => {
    // 尝试匹配预定义模板
    const template = categoryTemplates.find((t) => t.name === name)
    if (template) return template.type

    // 尝试匹配前两个字的拼音
    const words = name.match(/[\u4e00-\u9fa5]+/g) || []
    if (words.length > 0 && words[0]) {
      const firstWord = words[0].substring(0, 2)

      // 尝试整体匹配
      if (pinyinMap[firstWord]) {
        return pinyinMap[firstWord]
      }

      // 尝试逐字匹配
      let result = ''
      for (let i = 0; i < Math.min(2, firstWord.length); i++) {
        const char = firstWord[i]
        if (pinyinMap[char]) {
          result += pinyinMap[char]
        }
      }
      if (result) return result
    }

    // 默认使用小写字母和数字
    return name
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '_')
      .substring(0, 20)
  }

  // 监听 modelValue 变化
  watch(
    () => props.modelValue,
    (val) => {
      visible.value = val
      if (val) {
        loadCategories()
      }
    },
    { immediate: true }
  )

  // 监听 visible 变化
  watch(visible, (val) => {
    emit('update:modelValue', val)
  })

  // 加载分类列表
  const loadCategories = async () => {
    loading.value = true
    try {
      const result = await projectCategoryApi.getProjectCategories(props.projectId)
      categories.value = result?.items || []
    } catch (error: any) {
      ElMessage.error(error.message || '加载分类列表失败')
    } finally {
      loading.value = false
    }
  }

  // 选择预定义模板
  const selectTemplate = (template: (typeof categoryTemplates)[0]) => {
    form.value.name = template.name
    form.value.type = template.type
    form.value.icon = template.icon
    form.value.description = template.description
  }

  // 分类名称变化时自动生成类型标识
  const onNameChange = () => {
    // 只在新增且类型为空时自动生成
    if (!editingCategory.value && !form.value.type) {
      form.value.type = convertToType(form.value.name)
    }
  }

  // 打开新增对话框
  const handleAdd = () => {
    editingCategory.value = null
    form.value = {
      name: '',
      type: '',
      icon: '📄',
      description: '',
      sort_order: categories.value.length
    }
    showFormDialog.value = true
  }

  // 打开编辑对话框
  const handleEdit = (category: ProjectCategory) => {
    editingCategory.value = category
    form.value = {
      name: category.name,
      type: category.type,
      icon: category.icon || '',
      description: category.description || '',
      sort_order: category.sort_order
    }
    showFormDialog.value = true
  }

  // 保存分类
  const handleSave = async () => {
    if (!formRef.value) return

    await formRef.value.validate(async (valid) => {
      if (!valid) return

      saving.value = true
      try {
        if (editingCategory.value) {
          // 更新
          await projectCategoryApi.updateCategory(editingCategory.value.id, {
            name: form.value.name,
            icon: form.value.icon || undefined,
            description: form.value.description || undefined,
            sort_order: form.value.sort_order
          })
          ElMessage.success('分类更新成功')
        } else {
          // 新增
          await projectCategoryApi.createCategory(props.projectId, {
            project_id: props.projectId,
            name: form.value.name,
            type: form.value.type,
            icon: form.value.icon || undefined,
            description: form.value.description || undefined,
            sort_order: form.value.sort_order
          })
          ElMessage.success('分类创建成功')
        }

        showFormDialog.value = false
        await loadCategories()
        emit('refresh')
      } catch (error: any) {
        ElMessage.error(error.message || '保存失败')
      } finally {
        saving.value = false
      }
    })
  }

  // 删除分类（带确认和文章数量提示）
  const handleDeleteClick = async (category: ProjectCategory) => {
    try {
      // 先查询该分类下的文章数量
      const result = await articlesApi.getArticles({
        project_id: category.project_id,
        type: category.type,
        page: 1,
        page_size: 1
      })

      const articleCount = result?.total || 0

      // 构建确认消息
      let message = `确定要删除分类"${category.name}"吗？`
      if (articleCount > 0) {
        message = `分类"${category.name}"下有 ${articleCount} 篇文章。\n删除分类将同时删除这些文章，此操作无法撤销！\n\n确定要继续吗？`
      }

      await ElMessageBox.confirm(message, '删除确认', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false,
        distinguishCancelAndClose: true
      })

      // 用户确认后执行删除
      loading.value = true
      await projectCategoryApi.deleteCategory(category.id)
      ElMessage.success(
        '分类删除成功' + (articleCount > 0 ? `，已删除 ${articleCount} 篇相关文章` : '')
      )
      await loadCategories()
      emit('refresh')
    } catch (error: any) {
      if (error !== 'cancel' && error !== 'close') {
        ElMessage.error(error.message || '删除失败')
      }
    } finally {
      loading.value = false
    }
  }

  // 关闭对话框
  const handleClose = () => {
    visible.value = false
  }
</script>

<style scoped>
  .category-list {
    padding: 10px 0;
  }

  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .list-header h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
  }

  .form-tip {
    font-size: 12px;
    color: #6b7280;
    margin-top: 4px;
    line-height: 1.4;
  }

  /* 快速选择模板样式 */
  .quick-select-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .template-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px;
    background: linear-gradient(135deg, #f6f8fa 0%, #ffffff 100%);
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .template-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-color: #409eff;
  }

  .template-card.active {
    background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
    border-color: #409eff;
    box-shadow: 0 4px 16px rgba(64, 158, 255, 0.25);
  }

  .template-icon {
    font-size: 32px;
    flex-shrink: 0;
    line-height: 1;
  }

  .template-info {
    flex: 1;
    min-width: 0;
  }

  .template-name {
    font-size: 15px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 4px;
  }

  .template-desc {
    font-size: 12px;
    color: #6b7280;
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* 增强的图标选择器 */
  .icon-selector-enhanced {
    display: flex;
    gap: 16px;
    align-items: stretch;
    width: 100%;
  }

  .current-icon-display {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 16px;
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 2px solid #3b82f6;
    border-radius: 12px;
    flex-shrink: 0;
    width: 100px;
  }

  .current-icon {
    font-size: 48px;
    line-height: 1;
  }

  .current-icon-label {
    font-size: 12px;
    color: #3b82f6;
    font-weight: 600;
    white-space: nowrap;
  }

  .icon-grid {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(48px, 1fr));
    gap: 8px;
    padding: 16px;
    background: #f9fafb;
    border-radius: 10px;
    max-height: 240px;
    overflow-y: auto;
    align-content: start;
  }

  .icon-grid::-webkit-scrollbar {
    width: 6px;
  }

  .icon-grid::-webkit-scrollbar-track {
    background: #e5e7eb;
    border-radius: 3px;
  }

  .icon-grid::-webkit-scrollbar-thumb {
    background: #9ca3af;
    border-radius: 3px;
  }

  .icon-grid::-webkit-scrollbar-thumb:hover {
    background: #6b7280;
  }

  .icon-item {
    display: flex;
    align-items: center;
    justify-content: center;
    aspect-ratio: 1;
    min-height: 48px;
    font-size: 24px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    background: white;
    border: 2px solid #e5e7eb;
  }

  .icon-item:hover {
    background: #f3f4f6;
    transform: scale(1.1);
    border-color: #3b82f6;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    z-index: 1;
  }

  .icon-item.selected {
    border-color: #3b82f6;
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    position: relative;
    z-index: 2;
  }
</style>
