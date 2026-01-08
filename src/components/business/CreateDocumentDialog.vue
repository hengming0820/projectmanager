<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="600px"
    :close-on-click-modal="false"
    :z-index="10000000"
    :modal="true"
    :append-to-body="true"
    :destroy-on-close="true"
    class="create-document-dialog"
    @closed="handleClosed"
  >
    <el-config-provider :z-index="10000100">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        label-position="right"
      >
        <!-- 文档标题 -->
        <el-form-item label="文档标题" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入文档标题"
            maxlength="100"
            show-word-limit
            clearable
            size="large"
          />
        </el-form-item>

        <!-- 文档描述 -->
        <el-form-item :label="descriptionLabel" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :placeholder="`简要描述${descriptionLabel.replace('文档', '')}内容...`"
            :rows="4"
            maxlength="500"
            show-word-limit
            clearable
          />
        </el-form-item>

        <!-- 优先级 -->
        <el-form-item v-if="showPriority" label="优先级" prop="priority">
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

        <!-- 标签 -->
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="formData.tags"
            multiple
            filterable
            allow-create
            default-first-option
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="2"
            placeholder="选择或创建标签"
            size="large"
            style="width: 100%"
          >
            <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>

        <!-- 协作角色（用于筛选协作者） -->
        <el-form-item label="协作角色" prop="collaborator_roles">
          <el-select
            v-model="formData.collaborator_roles"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="2"
            placeholder="选择协作角色，自动添加该角色的所有成员"
            size="large"
            style="width: 100%"
            @change="handleRoleChange"
          >
            <el-option
              v-for="role in roleOptions"
              :key="role.value"
              :label="role.label"
              :value="role.value"
            />
          </el-select>
          <div v-if="!formData.collaborator_roles || formData.collaborator_roles.length === 0" class="form-tip warning">
            💡 请先选择协作角色，系统将自动添加该角色的所有成员
          </div>
          <div v-else class="form-tip success">
            ✅ 已自动选择 {{ filteredUsersByRole.length }} 位成员（可手动调整）
          </div>
        </el-form-item>

        <!-- 协作者/可编辑成员 -->
        <el-form-item :label="collaboratorLabel" prop="editable_user_ids">
          <el-select
            v-model="formData.editable_user_ids"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="2"
            :placeholder="`选择可以编辑此${documentType}的用户`"
            size="large"
            style="width: 100%"
            :disabled="!formData.collaborator_roles || formData.collaborator_roles.length === 0"
          >
            <el-option
              v-for="user in filteredUsersByRole"
              :key="user.value"
              :label="user.label"
              :value="user.value"
            >
              <span>{{ user.label }}</span>
              <span style="color: #8492a6; font-size: 12px; margin-left: 8px">
                ({{ getRoleLabel(user.role) }})
              </span>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 可编辑角色（用于文章权限控制） -->
        <el-form-item v-if="showRoles" label="可编辑角色" prop="editable_roles">
          <el-select
            v-model="formData.editable_roles"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="2"
            placeholder="选择可编辑角色"
            size="large"
            style="width: 100%"
          >
            <el-option
              v-for="role in roleOptions"
              :key="role.value"
              :label="role.label"
              :value="role.value"
            />
          </el-select>
        </el-form-item>

        <!-- 所属部门 -->
        <el-form-item v-if="showDepartments" label="所属部门" prop="departments">
          <el-select
            v-model="formData.departments"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            :max-collapse-tags="2"
            placeholder="选择部门"
            size="large"
            style="width: 100%"
          >
            <el-option v-for="d in deptOptions" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-config-provider>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel" size="large">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
          size="large"
          class="submit-btn"
        >
          <el-icon v-if="!submitting"><Check /></el-icon>
          {{ submitButtonText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
  import { ref, reactive, watch, computed } from 'vue'
  import { ElMessage, ElConfigProvider, type FormInstance, type FormRules } from 'element-plus'
  import { Check } from '@element-plus/icons-vue'

  interface FormData {
    title: string
    description: string
    priority?: 'low' | 'normal' | 'high' | 'urgent'
    tags: string[]
    collaborator_roles?: string[]
    editable_roles?: string[]
    editable_user_ids: string[]
    departments?: string[]
  }

  interface UserOption {
    label: string
    value: string
    role?: string
  }

  interface Props {
    modelValue: boolean
    title?: string
    descriptionLabel?: string
    collaboratorLabel?: string
    documentType?: string
    submitButtonText?: string
    showPriority?: boolean
    showRoles?: boolean
    showDepartments?: boolean
    availableTags?: string[]
    userOptions?: UserOption[]
    roleOptions?: Array<{ label: string; value: string }>
    deptOptions?: Array<{ label: string; value: string }>
  }

  const props = withDefaults(defineProps<Props>(), {
    title: '创建协作文档',
    descriptionLabel: '文档描述',
    collaboratorLabel: '协作者',
    documentType: '文档',
    submitButtonText: '创建并编辑',
    showPriority: true,
    showRoles: false,
    showDepartments: false,
    availableTags: () => [],
    userOptions: () => [],
    roleOptions: () => [],
    deptOptions: () => []
  })

  const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void
    (e: 'submit', data: FormData): void
    (e: 'cancel'): void
  }>()

  const visible = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
  })

  const formRef = ref<FormInstance>()
  const submitting = ref(false)

  const formData = reactive<FormData>({
    title: '',
    description: '',
    priority: 'normal',
    tags: [],
    collaborator_roles: [],
    editable_roles: [],
    editable_user_ids: [],
    departments: []
  })

  const rules: FormRules = {
    title: [
      { required: true, message: '请输入文档标题', trigger: 'blur' },
      { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' }
    ],
    description: [{ max: 500, message: '描述不能超过 500 个字符', trigger: 'blur' }]
  }

  // 根据选择的角色筛选用户
  const filteredUsersByRole = computed(() => {
    if (!formData.collaborator_roles || formData.collaborator_roles.length === 0) {
      return props.userOptions || []
    }
    return (props.userOptions || []).filter((user) =>
      formData.collaborator_roles!.includes(user.role || '')
    )
  })

  // 获取角色标签
  const getRoleLabel = (roleValue?: string) => {
    if (!roleValue) return ''
    const role = props.roleOptions?.find((r) => r.value === roleValue)
    return role?.label || roleValue
  }

  // 角色变化时自动更新协作者列表
  const handleRoleChange = () => {
    // 自动选择该角色下的所有用户
    const selectedUserIds = filteredUsersByRole.value.map((u) => u.value)
    formData.editable_user_ids = selectedUserIds
  }

  const handleSubmit = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validate()
      emit('submit', { ...formData })
    } catch (error) {
      console.error('表单验证失败:', error)
    }
  }

  const handleCancel = () => {
    emit('cancel')
    visible.value = false
  }

  const handleClosed = () => {
    formRef.value?.resetFields()
    formData.title = ''
    formData.description = ''
    formData.priority = 'normal'
    formData.tags = []
    formData.collaborator_roles = []
    formData.editable_roles = []
    formData.editable_user_ids = []
    formData.departments = []
  }

  // 暴露方法给父组件
  defineExpose({
    setSubmitting: (value: boolean) => {
      submitting.value = value
    },
    close: () => {
      visible.value = false
    }
  })
</script>

<style scoped lang="scss">
  .create-document-dialog {
    :deep(.el-dialog__header) {
      border-bottom: 1px solid var(--el-border-color-lighter);
      padding: 20px 24px;
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

    :deep(.el-form-item__label) {
      font-weight: 500;
      color: var(--el-text-color-primary);
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

    .form-tip {
      margin-top: 8px;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 13px;
      line-height: 1.5;

      &.warning {
        background-color: #fef0e6;
        color: #e6a23c;
        border: 1px solid #f5dab1;
      }

      &.success {
        background-color: #f0f9ff;
        color: #409eff;
        border: 1px solid #c6e2ff;
      }
    }

    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;

      .submit-btn {
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

