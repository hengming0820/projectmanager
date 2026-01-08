<template>
  <ElDialog
    v-model="dialogVisible"
    :title="dialogType === 'add' ? '✨ 添加用户' : '✏️ 编辑用户'"
    width="600px"
    align-center
    :close-on-click-modal="false"
    class="user-dialog"
    append-to-body
    :z-index="3000"
  >
    <div class="dialog-content">
      <!-- 提示信息 -->
      <el-alert
        v-if="dialogType === 'add'"
        type="info"
        :closable="false"
        class="mb-4"
        show-icon
      >
        <template #title>
          <span class="font-bold">新建用户提示</span>
        </template>
        <div class="text-xs mt-1">
          • 默认密码为 <span class="text-primary font-bold">xxjz8888</span>，请提醒用户修改<br />
          • 用户名创建后不可修改
        </div>
      </el-alert>

      <ElForm ref="formRef" :model="formData" :rules="rules" label-width="80px" class="user-form">
        <div class="form-layout">
          <!-- 左侧头像 -->
          <div class="avatar-section">
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
              :on-error="handleAvatarError"
              :action="uploadUrl"
              :headers="uploadHeaders"
              accept="image/*"
            >
              <div v-if="formData.avatar_url" class="avatar-preview">
                <el-image :src="formData.avatar_url" fit="cover" class="avatar-image" />
                <div class="avatar-overlay">
                  <el-icon><Upload /></el-icon>
                </div>
              </div>
              <div v-else class="avatar-placeholder">
                <el-icon class="avatar-icon"><Plus /></el-icon>
                <span class="text-xs text-gray-400 mt-1">上传头像</span>
              </div>
            </el-upload>
            <el-button 
              v-if="formData.avatar_url" 
              type="danger" 
              link 
              size="small" 
              class="mt-2"
              @click.stop="removeAvatar"
            >
              删除头像
            </el-button>
          </div>

          <!-- 右侧表单 -->
          <div class="fields-section">
            <ElFormItem label="用户名" prop="username">
              <ElInput
                v-model="formData.username"
                placeholder="请输入用户名"
                :disabled="dialogType === 'edit'"
                clearable
              >
                <template #prefix><el-icon><User /></el-icon></template>
              </ElInput>
            </ElFormItem>

            <ElFormItem label="真实姓名" prop="real_name">
              <ElInput v-model="formData.real_name" placeholder="请输入真实姓名" clearable>
                <template #prefix><el-icon><Avatar /></el-icon></template>
              </ElInput>
            </ElFormItem>

            <ElFormItem label="邮箱地址" prop="email">
              <ElInput v-model="formData.email" placeholder="请输入邮箱地址" clearable>
                <template #prefix><el-icon><Message /></el-icon></template>
              </ElInput>
            </ElFormItem>
          </div>
        </div>

        <!-- 底部详细信息 -->
        <div class="bottom-section mt-4">
          <div class="section-divider">
            <span>组织与其他信息</span>
          </div>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <ElFormItem label="所属部门" prop="department">
                <ElSelect
                  v-model="formData.department"
                  placeholder="请选择部门"
                  filterable
                  allow-create
                  default-first-option
                  clearable
                  class="w-full"
                >
                  <el-option
                    v-for="dept in departmentOptions"
                    :key="dept.value"
                    :label="dept.label"
                    :value="dept.value"
                  >
                    <div class="flex items-center gap-2">
                      <el-icon :style="{ color: dept.color }"><component :is="dept.icon" /></el-icon>
                      <span>{{ dept.label }}</span>
                    </div>
                  </el-option>
                </ElSelect>
              </ElFormItem>
            </el-col>
            <el-col :span="12">
              <ElFormItem label="用户角色" prop="role">
                <ElSelect
                  v-model="formData.role"
                  placeholder="请选择角色"
                  class="w-full"
                  :loading="rolesLoading"
                >
                  <ElOption
                    v-for="role in roleOptions"
                    :key="role.value"
                    :label="role.label"
                    :value="role.value"
                  >
                    <div class="flex items-center gap-2">
                      <span>{{ role.icon }}</span>
                      <span>{{ role.label }}</span>
                    </div>
                  </ElOption>
                </ElSelect>
              </ElFormItem>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <ElFormItem label="入职日期" prop="hire_date">
                <ElDatePicker
                  v-model="formData.hire_date"
                  type="date"
                  placeholder="选择入职日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  class="w-full"
                  style="width: 100% !important;"
                  clearable
                />
              </ElFormItem>
            </el-col>
            <el-col :span="12" v-if="dialogType === 'add'">
              <ElFormItem label="初始密码" prop="password">
                <ElInput
                  v-model="formData.password"
                  type="password"
                  placeholder="默认: xxjz8888"
                  show-password
                  clearable
                >
                  <template #prefix><el-icon><Lock /></el-icon></template>
                </ElInput>
              </ElFormItem>
            </el-col>
          </el-row>
        </div>
      </ElForm>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <ElButton @click="dialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="handleSubmit" :loading="loading">
          {{ dialogType === 'add' ? '创建用户' : '保存修改' }}
        </ElButton>
      </div>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'
  import type { FormInstance, FormRules } from 'element-plus'
  import { ElMessage } from 'element-plus'
  import {
    User,
    Avatar,
    Message,
    Lock,
    OfficeBuilding,
    Calendar,
    Check,
    Close,
    InfoFilled,
    Monitor,
    Edit,
    UserFilled,
    Plus,
    Upload,
    Delete
  } from '@element-plus/icons-vue'
  import { userApi } from '@/api/userApi'
  import { roleApi } from '@/api/roleApi'
  import type { UserRole } from '@/types/project'
  import { useUserStore } from '@/store/modules/user'

  interface Props {
    visible: boolean
    type: string
    userData?: any
  }

  interface Emits {
    (e: 'update:visible', value: boolean): void
    (e: 'submit'): void
  }

  const props = defineProps<Props>()
  const emit = defineEmits<Emits>()

  // 获取用户store以获取token
  const userStore = useUserStore()

  // 部门选项
  const departmentOptions = [
    { label: '研发部标注组', value: '研发部标注组', icon: Edit, color: '#409eff' },
    { label: '研发部算法组', value: '研发部算法组', icon: Monitor, color: '#67c23a' },
    { label: '研发部开发组', value: '研发部开发组', icon: Monitor, color: '#e6a23c' },
    { label: '星像行政部门', value: '星像行政部门', icon: OfficeBuilding, color: '#909399' }
  ]

  // 角色选项和加载状态
  const roleOptions = ref<Array<{ label: string; value: string; icon: string }>>([])
  const rolesLoading = ref(false)

  // 角色图标映射
  const getRoleIcon = (roleName: string): string => {
    const iconMap: Record<string, string> = {
      admin: '👑',
      administrator: '👑',
      管理员: '👑',
      annotator: '✏️',
      标注员: '✏️',
      reviewer: '✅',
      审核员: '✅',
      algorithm: '🧮',
      算法工程师: '🧮',
      developer: '💻',
      开发工程师: '💻'
    }

    // 尝试完全匹配
    if (iconMap[roleName]) {
      return iconMap[roleName]
    }

    // 尝试部分匹配
    for (const [key, icon] of Object.entries(iconMap)) {
      if (roleName.toLowerCase().includes(key) || roleName.includes(key)) {
        return icon
      }
    }

    return '👤' // 默认图标
  }

  // 加载角色列表
  const loadRoles = async () => {
    try {
      rolesLoading.value = true
      const response = await roleApi.getRoles({ size: 100 })

      // 解析响应数据
      let roles = []
      if (Array.isArray(response)) {
        roles = response
      } else if ((response as any).list) {
        roles = (response as any).list
      } else if ((response as any).data?.list) {
        roles = (response as any).data.list
      }

      // 转换为选项格式
      roleOptions.value = roles.map((role: any) => ({
        label: role.name || role.roleName || role.role_name || role.role || role.id,
        value: role.role || role.id || role.name, // 使用 role 编码作为值
        icon: getRoleIcon(role.name || role.roleName || role.role_name || role.role || '')
      }))

      // 如果没有角色数据，添加提示
      if (roleOptions.value.length === 0) {
        console.warn('⚠️ 未获取到角色数据，使用默认角色')
        roleOptions.value = [
          { label: '管理员', value: 'admin', icon: '👑' },
          { label: '标注员', value: 'annotator', icon: '✏️' },
          { label: '审核员', value: 'reviewer', icon: '✅' }
        ]
      }

      console.log('✅ 角色列表加载成功:', roleOptions.value)
    } catch (error) {
      console.error('❌ 加载角色列表失败:', error)
      ElMessage.warning('加载角色列表失败，将使用默认角色')

      // 失败时使用默认角色
      roleOptions.value = [
        { label: '管理员', value: 'admin', icon: '👑' },
        { label: '标注员', value: 'annotator', icon: '✏️' },
        { label: '审核员', value: 'reviewer', icon: '✅' }
      ]
    } finally {
      rolesLoading.value = false
    }
  }

  // 对话框显示控制
  const dialogVisible = computed({
    get: () => props.visible,
    set: (value) => emit('update:visible', value)
  })

  const dialogType = computed(() => props.type)

  // 表单实例
  const formRef = ref<FormInstance>()

  // 表单数据
  type FormData = {
    username: string
    real_name: string
    email: string
    department: string
    role: UserRole
    password: string
    hire_date: string
    avatar_url: string
  }

  const formData = reactive<FormData>({
    username: '',
    real_name: '',
    email: '',
    department: '',
    role: 'annotator' as UserRole,
    password: 'xxjz8888', // 默认密码
    hire_date: new Date().toISOString().split('T')[0], // 默认为今天
    avatar_url: '' // 头像URL
  })

  // 上传地址 - 使用后端的通用图片上传接口
  const uploadUrl = ref('/api/common/upload/images')

  // 上传请求头 - 携带认证token（accessToken已包含Bearer前缀）
  const uploadHeaders = computed(() => {
    return {
      Authorization: userStore.accessToken
    }
  })

  // 表单验证规则
  const rules: FormRules = {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
    ],
    real_name: [
      { required: true, message: '请输入真实姓名', trigger: 'blur' },
      { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
    ],
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
    ],
    department: [{ required: false, message: '请选择部门', trigger: 'change' }],
    role: [{ required: true, message: '请选择角色', trigger: 'change' }],
    password: [
      { required: false }, // 不再必填，因为有默认值
      { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
    ]
  }

  // 头像上传成功
  const handleAvatarSuccess = (response: any) => {
    try {
      // 后端返回格式：{ code: 200, data: { files: [{url}], count } }
      if (response.code === 200 && response.data?.files?.length > 0) {
        formData.avatar_url = response.data.files[0].url
        ElMessage.success('✅ 头像上传成功')
      } else {
        ElMessage.error(response.message || '❌ 头像上传失败')
      }
    } catch (error) {
      console.error('头像上传错误:', error)
      ElMessage.error('❌ 头像上传失败')
    }
  }

  // 头像上传前验证
  const beforeAvatarUpload = (file: File) => {
    const isImage = file.type.startsWith('image/')
    const isLt2M = file.size / 1024 / 1024 < 2

    if (!isImage) {
      ElMessage.error('❌ 只能上传图片文件')
      return false
    }
    if (!isLt2M) {
      ElMessage.error('❌ 图片大小不能超过 2MB')
      return false
    }
    return true
  }

  // 头像上传失败
  const handleAvatarError = (error: any) => {
    console.error('头像上传失败:', error)
    try {
      const errorMsg = error?.message || error?.detail || '上传失败'
      if (errorMsg.includes('Not authenticated')) {
        ElMessage.error('❌ 认证失败，请重新登录')
      } else {
        ElMessage.error(`❌ ${errorMsg}`)
      }
    } catch {
      ElMessage.error('❌ 头像上传失败，请重试')
    }
  }

  // 删除头像
  const removeAvatar = () => {
    formData.avatar_url = ''
    ElMessage.success('✅ 头像已删除')
  }

  // 初始化表单数据
  const initFormData = () => {
    const isEdit = props.type === 'edit' && props.userData
    const row = props.userData

    if (isEdit) {
      Object.assign(formData, {
        username: row.username || row.userName || '',
        real_name: row.real_name || row.realName || '',
        email: row.email || row.userEmail || '',
        department: row.department || '',
        role: (row.role || 'annotator') as UserRole,
        hire_date: row.hire_date || row.hireDate || new Date().toISOString().split('T')[0],
        avatar_url: row.avatar_url || row.avatar || ''
      })
    } else {
      // 添加模式重置表单
      Object.assign(formData, {
        username: '',
        real_name: '',
        email: '',
        department: '',
        role: 'annotator',
        password: 'xxjz8888', // 默认密码
        hire_date: new Date().toISOString().split('T')[0],
        avatar_url: ''
      })
    }
  }

  // 统一监听对话框状态变化
  watch(
    () => [props.visible, props.type, props.userData],
    ([visible]) => {
      if (visible) {
        initFormData()
        // 加载角色列表（如果还没加载）
        if (roleOptions.value.length === 0) {
          loadRoles()
        }
        nextTick(() => {
          formRef.value?.clearValidate()
        })
      }
    },
    { immediate: true }
  )

  // 组件挂载时加载角色列表
  onMounted(() => {
    loadRoles()
  })

  const loading = ref(false)

  // 提交表单
  const handleSubmit = async () => {
    if (!formRef.value) return

    await formRef.value.validate(async (valid) => {
      if (valid) {
        loading.value = true
        try {
          if (dialogType.value === 'add') {
            // 添加用户，如果密码为空则使用默认密码
            const password = formData.password.trim() || 'xxjz8888'
            await userApi.createUser({
              username: formData.username,
              real_name: formData.real_name,
              email: formData.email,
              department: formData.department,
              role: formData.role,
              password: password,
              hire_date: formData.hire_date, // 入职日期
              avatar_url: formData.avatar_url // 头像URL
            })
            ElMessage.success('✅ 用户创建成功')
          } else {
            // 编辑用户
            if (props.userData && props.userData.id) {
              await userApi.updateUser(props.userData.id, {
                real_name: formData.real_name,
                email: formData.email,
                department: formData.department,
                role: formData.role,
                hire_date: formData.hire_date, // 入职日期
                avatar_url: formData.avatar_url // 头像URL
              })
              ElMessage.success('✅ 用户信息更新成功')
            }
          }
          dialogVisible.value = false
          emit('submit')
        } catch (error: any) {
          ElMessage.error(
            error.message || (dialogType.value === 'add' ? '❌ 创建失败' : '❌ 更新失败')
          )
        } finally {
          loading.value = false
        }
      }
    })
  }
</script>

<style lang="scss" scoped>
  .user-dialog {
    :deep(.el-dialog__header) {
      padding: 20px 24px;
      margin-right: 0;
      border-bottom: 1px solid var(--art-card-border);
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

      .el-dialog__title {
        font-size: 18px;
        font-weight: 600;
        color: #fff;
      }

      .el-dialog__headerbtn {
        top: 22px;

        .el-dialog__close {
          color: #fff;
          font-size: 20px;

          &:hover {
            color: rgba(255, 255, 255, 0.8);
          }
        }
      }
    }

    :deep(.el-dialog__body) {
      padding: 24px;
      background: var(--art-bg-color);
    }

    :deep(.el-dialog__footer) {
      padding: 16px 24px;
      border-top: 1px solid var(--art-card-border);
      background: var(--art-main-bg-color);
    }
  }

  .dialog-content {
    .user-form {
      .form-layout {
        display: flex;
        gap: 24px;
        
        .avatar-section {
          flex-shrink: 0;
          width: 120px;
          display: flex;
          flex-direction: column;
          align-items: center;
          
          .avatar-uploader {
            width: 100px;
            height: 100px;
            
            :deep(.el-upload) {
              width: 100%;
              height: 100%;
              border-radius: 50%;
              overflow: hidden;
              border: 2px dashed var(--art-card-border);
              transition: all 0.3s;
              background: var(--art-main-bg-color);
              display: flex;
              align-items: center;
              justify-content: center;
              cursor: pointer;
              
              &:hover {
                border-color: var(--art-primary-color);
                background: rgba(var(--art-primary-rgb), 0.05);
              }
            }
            
            .avatar-preview {
              width: 100%;
              height: 100%;
              position: relative;
              
              .avatar-image {
                width: 100%;
                height: 100%;
                border-radius: 50%;
              }
              
              .avatar-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.3s;
                color: #fff;
                border-radius: 50%;
              }
              
              &:hover .avatar-overlay {
                opacity: 1;
              }
            }
            
            .avatar-placeholder {
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              
              .avatar-icon {
                font-size: 24px;
                color: var(--art-text-gray-400);
              }
            }
          }
        }
        
        .fields-section {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
      }
      
      .bottom-section {
        .section-divider {
          display: flex;
          align-items: center;
          margin: 16px 0 20px;
          color: var(--art-text-gray-500);
          font-size: 12px;
          
          &::before,
          &::after {
            content: '';
            flex: 1;
            height: 1px;
            background: var(--art-card-border);
          }
          
          span {
            padding: 0 12px;
          }
        }
      }

      :deep(.el-form-item) {
        margin-bottom: 18px;

        .el-form-item__label {
          font-weight: 500;
          color: var(--art-text-gray-700);
        }
      }
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;

    .el-button {
      min-width: 90px;
    }
  }
  
  // Utility classes
  .mb-4 { margin-bottom: 16px; }
  .mt-1 { margin-top: 4px; }
  .mt-2 { margin-top: 8px; }
  .mt-4 { margin-top: 16px; }
  .text-xs { font-size: 12px; }
  .font-bold { font-weight: 600; }
  .text-primary { color: var(--art-primary-color); }
  .text-gray-400 { color: var(--art-text-gray-400); }
  .w-full { width: 100%; }
  .flex { display: flex; }
  .items-center { align-items: center; }
  .gap-2 { gap: 8px; }
</style>
