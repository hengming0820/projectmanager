<template>
  <el-dialog
    v-model="visible"
    :close-on-click-modal="false"
    width="600px"
    class="article-meta-dialog"
    :z-index="10000000"
    :modal="true"
    :append-to-body="true"
    :destroy-on-close="true"
    @close="handleClose"
  >
    <template #header>
      <div class="dialog-header">
        <div class="dialog-icon">
          <el-icon><Edit /></el-icon>
        </div>
        <div class="dialog-title">
          <h3>{{ title }}</h3>
          <p>{{ subtitle }}</p>
        </div>
      </div>
    </template>

    <el-config-provider :z-index="10000100">
      <el-form :model="formData" label-width="90px" class="meta-form">
        <!-- 标题 -->
        <el-form-item label="标题" required>
          <el-input v-model="formData.title" placeholder="请输入标题" size="large" />
        </el-form-item>

        <!-- 描述/摘要 -->
        <el-form-item :label="descriptionLabel">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            :placeholder="`请输入${descriptionLabel}`"
          />
        </el-form-item>

        <!-- 封面（仅文章类型） -->
        <el-form-item v-if="showCover" label="封面">
          <el-upload
            list-type="picture-card"
            v-model:file-list="coverList"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="onCoverUploaded"
            :on-remove="onCoverRemoved"
            accept="image/*"
            :limit="1"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <!-- 分类（仅文章类型） -->
        <el-form-item v-if="showCategory" label="分类">
          <el-input v-model="formData.category" placeholder="输入或选择分类" />
        </el-form-item>

        <!-- 状态 -->
        <el-form-item v-if="showStatus" label="状态">
          <el-select v-model="formData.status" placeholder="选择状态" size="large">
            <el-option
              v-for="status in statusOptions"
              :key="status.value"
              :label="status.label"
              :value="status.value"
            >
              <span class="status-option">
                <span class="emoji">{{ status.emoji }}</span>
                <span>{{ status.text }}</span>
              </span>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 优先级 -->
        <el-form-item v-if="showPriority" label="优先级">
          <el-radio-group v-model="formData.priority" size="large" class="priority-group">
            <el-radio-button value="low">
              <span class="priority-option low">低</span>
            </el-radio-button>
            <el-radio-button value="normal">
              <span class="priority-option normal">普通</span>
            </el-radio-button>
            <el-radio-button value="high">
              <span class="priority-option high">高</span>
            </el-radio-button>
            <el-radio-button value="urgent">
              <span class="priority-option urgent">紧急</span>
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 可见性（仅文章类型） -->
        <el-form-item v-if="showVisibility" label="可见">
          <el-switch v-model="formData.is_public" />
        </el-form-item>

        <!-- 标签 -->
        <el-form-item label="标签">
          <el-select
            v-model="formData.tags"
            multiple
            filterable
            allow-create
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="2"
            placeholder="添加标签"
            size="large"
            class="tags-select"
          >
            <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>

        <!-- 可编辑角色 -->
        <el-form-item label="可编辑角色">
          <el-select
            v-model="formData.editable_roles"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="2"
            placeholder="选择可编辑角色"
            size="large"
          >
            <el-option
              v-for="role in roleOptions"
              :key="role.value"
              :label="role.label"
              :value="role.value"
            />
          </el-select>
        </el-form-item>

        <!-- 可编辑成员 -->
        <el-form-item label="可编辑成员">
          <el-select
            v-model="formData.editable_user_ids"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="2"
            placeholder="选择人员"
            size="large"
          >
            <el-option v-for="u in userOptions" :key="u.value" :label="u.label" :value="u.value" />
          </el-select>
        </el-form-item>

        <!-- 所属部门 -->
        <el-form-item label="所属部门">
          <el-select
            v-model="formData.departments"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="2"
            placeholder="选择部门"
            size="large"
          >
            <el-option v-for="d in deptOptions" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-config-provider>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel" size="large">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving" size="large" class="save-btn">
          <el-icon v-if="!saving"><Check /></el-icon>
          保存修改
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
  import { ref, computed, watch } from 'vue'
  import { ElMessage, ElConfigProvider } from 'element-plus'
  import { Edit, Check, Plus } from '@element-plus/icons-vue'

  interface MetaFormData {
    title: string
    description?: string
    summary?: string
    cover_url?: string
    category?: string
    status?: string
    priority?: string
    is_public?: boolean
    tags?: string[]
    editable_roles?: string[]
    editable_user_ids?: string[]
    departments?: string[]
  }

  interface StatusOption {
    label: string
    value: string
    emoji: string
    text: string
  }

  interface Props {
    modelValue: boolean
    data?: MetaFormData
    title?: string
    subtitle?: string
    descriptionLabel?: string
    showCover?: boolean
    showCategory?: boolean
    showStatus?: boolean
    showPriority?: boolean
    showVisibility?: boolean
    statusOptions?: StatusOption[]
    availableTags?: string[]
    userOptions?: Array<{ label: string; value: string }>
    roleOptions?: Array<{ label: string; value: string }>
    deptOptions?: Array<{ label: string; value: string }>
    uploadUrl?: string
    uploadHeaders?: Record<string, string>
  }

  const props = withDefaults(defineProps<Props>(), {
    title: '编辑信息',
    subtitle: '修改文档的标题、描述、状态等元数据',
    descriptionLabel: '描述',
    showCover: false,
    showCategory: false,
    showStatus: true,
    showPriority: true,
    showVisibility: false,
    statusOptions: () => [
      { label: '📝 草稿', value: 'draft', emoji: '📝', text: '草稿' },
      { label: '🔄 进行中', value: 'active', emoji: '🔄', text: '进行中' },
      { label: '✅ 已完成', value: 'completed', emoji: '✅', text: '已完成' },
      { label: '📦 已归档', value: 'archived', emoji: '📦', text: '已归档' }
    ],
    availableTags: () => [],
    userOptions: () => [],
    roleOptions: () => [],
    deptOptions: () => [],
    uploadUrl: '',
    uploadHeaders: () => ({})
  })

  const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void
    (e: 'save', data: MetaFormData): void
    (e: 'cancel'): void
  }>()

  const visible = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
  })

  const formData = ref<MetaFormData>({
    title: '',
    description: '',
    summary: '',
    cover_url: '',
    category: '',
    status: 'draft',
    priority: 'normal',
    is_public: true,
    tags: [],
    editable_roles: [],
    editable_user_ids: [],
    departments: []
  })

  const coverList = ref<any[]>([])
  const saving = ref(false)

  // 监听 data 变化，更新表单数据
  watch(
    () => props.data,
    (newData) => {
      if (newData) {
        formData.value = { ...formData.value, ...newData }
        // 更新封面列表
        if (newData.cover_url) {
          coverList.value = [{ name: 'cover', url: newData.cover_url }]
        } else {
          coverList.value = []
        }
      }
    },
    { immediate: true, deep: true }
  )

  // 封面上传成功
  const onCoverUploaded = (response: any) => {
    if (response.code === 200) {
      formData.value.cover_url = response.data.url
      ElMessage.success('封面上传成功')
    } else {
      ElMessage.error(response.msg || '封面上传失败')
    }
  }

  // 封面移除
  const onCoverRemoved = () => {
    formData.value.cover_url = ''
  }

  const handleSave = () => {
    if (!formData.value.title?.trim()) {
      ElMessage.warning('请输入标题')
      return
    }
    emit('save', { ...formData.value })
  }

  const handleCancel = () => {
    emit('cancel')
    visible.value = false
  }

  const handleClose = () => {
    emit('cancel')
  }

  // 暴露方法给父组件
  defineExpose({
    setSaving: (value: boolean) => {
      saving.value = value
    }
  })
</script>

<style scoped lang="scss">
  .article-meta-dialog {
    :deep(.el-dialog__header) {
      padding: 0;
      margin: 0;
    }

    :deep(.el-dialog__body) {
      padding: 24px;
      max-height: 70vh;
      overflow-y: auto;
    }

    :deep(.el-dialog__footer) {
      padding: 16px 24px;
      border-top: 1px solid var(--el-border-color-lighter);
    }

    .dialog-header {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 24px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;

      .dialog-icon {
        width: 48px;
        height: 48px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
      }

      .dialog-title {
        flex: 1;

        h3 {
          margin: 0 0 4px 0;
          font-size: 20px;
          font-weight: 600;
        }

        p {
          margin: 0;
          font-size: 14px;
          opacity: 0.9;
        }
      }
    }

    .meta-form {
      .el-form-item {
        margin-bottom: 20px;
      }

      .status-option {
        display: flex;
        align-items: center;
        gap: 8px;

        .emoji {
          font-size: 16px;
        }
      }

      .priority-group {
        width: 100%;

        :deep(.el-radio-button) {
          flex: 1;
        }

        :deep(.el-radio-button__inner) {
          width: 100%;
        }

        .priority-option {
          &.low {
            color: #909399;
          }
          &.normal {
            color: #409eff;
          }
          &.high {
            color: #e6a23c;
          }
          &.urgent {
            color: #f56c6c;
          }
        }
      }

      .tags-select {
        width: 100%;
      }
    }

    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;

      .save-btn {
        min-width: 120px;
      }
    }
  }
</style>

<style>
/* 全局样式：确保下拉菜单在最上层 */
.el-popper.el-select__popper {
  z-index: 99999999 !important;
}
</style>

