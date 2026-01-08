<template>
  <ArtSearchBar
    ref="searchBarRef"
    v-model="formData"
    :items="formItems"
    :rules="rules"
    :show-search="false"
    @reset="handleReset"
    @search="handleSearch"
  >
    <template #email>
      <ElInput v-model="formData.email" placeholder="我是插槽渲染出来的组件" />
    </template>
  </ArtSearchBar>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, watch } from 'vue'
  import { roleApi } from '@/api/roleApi'
  import { ElMessage } from 'element-plus'

  interface Props {
    modelValue: Record<string, any>
  }
  interface Emits {
    (e: 'update:modelValue', value: Record<string, any>): void
    (e: 'search', params: Record<string, any>): void
    (e: 'reset'): void
  }
  const props = defineProps<Props>()
  const emit = defineEmits<Emits>()

  // 表单数据双向绑定
  const searchBarRef = ref()
  const formData = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
  })

  // 校验规则
  const rules = {
    // name: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
  }

  // 动态角色选项
  const roleOptions = ref<Array<{ label: string; value: string }>>([{ label: '全部', value: '' }])

  // 部门选项
  const departmentOptions = ref<Array<{ label: string; value: string }>>([
    { label: '全部', value: '' },
    { label: '研发部标注组', value: '研发部标注组' },
    { label: '研发部算法组', value: '研发部算法组' },
    { label: '研发部开发组', value: '研发部开发组' },
    { label: '星像行政部门', value: '星像行政部门' }
  ])

  // 加载角色列表
  const loadRoles = async () => {
    try {
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
      const mappedRoles = roles.map((role: any) => ({
        label: role.name || role.roleName || role.role_name || role.role || role.id,
        value: role.role || role.id || role.name // 使用 role 编码作为值
      }))

      // 添加"全部"选项在最前面
      roleOptions.value = [{ label: '全部', value: '' }, ...mappedRoles]

      console.log('✅ 角色列表加载成功:', roleOptions.value)
    } catch (error) {
      console.error('❌ 加载角色列表失败:', error)
      ElMessage.warning('加载角色列表失败，将使用默认角色')

      // 失败时使用默认角色
      roleOptions.value = [
        { label: '全部', value: '' },
        { label: '管理员', value: 'admin' },
        { label: '标注员', value: 'annotator' },
        { label: '审核员', value: 'reviewer' }
      ]
    }
  }

  onMounted(async () => {
    await loadRoles()
  })

  // 表单配置
  const formItems = computed(() => [
    {
      label: '关键字',
      key: 'name',
      type: 'input',
      placeholder: '用户名/真实姓名',
      clearable: true
    },
    {
      label: '角色',
      key: 'role',
      type: 'select',
      props: {
        placeholder: '请选择角色',
        clearable: true,
        options: roleOptions.value
      }
    },
    {
      label: '部门',
      key: 'department',
      type: 'select',
      props: {
        placeholder: '请选择部门',
        clearable: true,
        options: departmentOptions.value
      }
    }
  ])

  // 监听表单数据变化，自动触发搜索
  watch(
    () => formData.value,
    (newVal) => {
      // 延迟一点执行，避免频繁请求
      setTimeout(() => {
        handleSearch()
      }, 300)
    },
    { deep: true }
  )

  // 事件
  function handleReset() {
    console.log('重置表单')
    emit('reset')
    // 重置后也触发搜索
    setTimeout(() => {
      handleSearch()
    }, 100)
  }

  async function handleSearch() {
    if (!searchBarRef.value) return
    try {
      await searchBarRef.value.validate()
      emit('search', formData.value)
      console.log('表单数据', formData.value)
    } catch (error) {
      console.error('表单验证失败:', error)
    }
  }
</script>
