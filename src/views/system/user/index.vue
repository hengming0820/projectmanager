<!-- 用户管理 -->
<!-- art-full-height 自动计算出页面剩余高度 -->
<!-- art-table-card 一个符合系统样式的 class，同时自动撑满剩余高度 -->
<!-- 更多 useTable 使用示例请移步至 功能示例 下面的 高级表格示例 -->
<template>
  <div class="user-page art-full-height">
    <!-- 页面头部 -->
    <ArtPageHeader
      title="用户管理"
      description="管理系统用户信息和账户配置"
      icon="👤"
      badge="Users"
      theme="purple"
    >
      <template #actions>
        <el-button type="primary" @click="showDialog('add')">
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
      </template>
    </ArtPageHeader>

    <!-- 搜索栏 -->
    <UserSearch v-model="searchForm" @search="handleSearch" @reset="resetSearchParams"></UserSearch>

    <ElCard class="art-table-card" shadow="never">
      <!-- 表格头部 -->
      <ArtTableHeader v-model:columns="columnChecks" @refresh="refreshData"> </ArtTableHeader>

      <!-- 表格 -->
      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @selection-change="handleSelectionChange"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      >
      </ArtTable>

      <!-- 用户弹窗 -->
      <UserDialog
        v-model:visible="dialogVisible"
        :type="dialogType"
        :user-data="currentUserData"
        @submit="handleDialogSubmit"
      />
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { ElMessageBox, ElMessage, ElTag, ElImage } from 'element-plus'
  import { Plus } from '@element-plus/icons-vue'
  import { useTable } from '@/composables/useTable'
  import { userApi } from '@/api/userApi'
  import UserSearch from './modules/user-search.vue'
  import UserDialog from './modules/user-dialog.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'

  defineOptions({ name: 'User' })

  type UserListItem = Api.User.UserListItem
  const { getUsers } = userApi

  // 弹窗相关
  const dialogType = ref<Form.DialogType>('add')
  const dialogVisible = ref(false)
  const currentUserData = ref<Partial<UserListItem>>({})

  // 选中行
  const selectedRows = ref<UserListItem[]>([])

  // 搜索表单
  const searchForm = ref({
    name: undefined,
    level: undefined,
    date: undefined,
    daterange: undefined,
    status: undefined
  })

  // 用户状态配置
  const USER_STATUS_CONFIG = {
    active: { type: 'success' as const, text: '活跃' },
    inactive: { type: 'danger' as const, text: '禁用' }
  } as const

  /**
   * 获取用户状态配置
   */
  const getUserStatusConfig = (status: string) => {
    return (
      USER_STATUS_CONFIG[status as keyof typeof USER_STATUS_CONFIG] || {
        type: 'info' as const,
        text: '未知'
      }
    )
  }

  /**
   * 头像URL重写：将直链重写为后端代理路径
   * 参考 art-header-bar 中的实现
   */
  const defaultAvatar = '/src/assets/img/user/avatar.webp'
  const rewriteAvatarUrl = (url?: string) => {
    if (!url) return defaultAvatar
    // 将直链重写为后端代理 /api/files
    const rewrittenUrl = url.replace(/^https?:\/\/[^/]+\/medical-annotations\//, '/api/files/')
    return rewrittenUrl || defaultAvatar
  }

  const {
    columns,
    columnChecks,
    data,
    loading,
    pagination,
    getData,
    searchParams,
    resetSearchParams,
    handleSizeChange,
    handleCurrentChange,
    refreshData
  } = useTable<UserListItem>({
    // 核心配置
    core: {
      apiFn: getUsers,
      apiParams: {
        current: 1,
        size: 20,
        ...searchForm.value
      },
      // 排除 apiParams 中的属性
      excludeParams: ['daterange'],
      columnsFactory: () => [
        { type: 'selection' }, // 勾选列
        { type: 'index', width: 60, label: '序号' }, // 序号
        {
          prop: 'avatar',
          label: '用户名',
          width: 280,
          formatter: (row) => {
            const r: any = row as any
            const rawAvatar = r.avatar_url || r.avatar || ''
            const avatar = rewriteAvatarUrl(rawAvatar)
            const name = r.userName || r.username || r.real_name || '-'
            const email = r.userEmail || r.email || ''
            return h('div', { class: 'user', style: 'display: flex; align-items: center' }, [
              h(ElImage, {
                class: 'avatar',
                src: avatar,
                previewSrcList: [avatar],
                previewTeleported: true,
                fit: 'cover'
              } as any),
              h('div', {}, [
                h('p', { class: 'user-name' }, name),
                h('p', { class: 'email' }, email)
              ])
            ])
          }
        },
        {
          prop: 'realName',
          label: '真实姓名',
          sortable: true,
          formatter: (row) => (row as any).real_name || (row as any).realName || '-'
        },
        {
          prop: 'role',
          label: '角色',
          formatter: (row) => {
            const roleMap: Record<string, string> = {
              admin: '管理员',
              annotator: '标注员',
              reviewer: '审核员'
            }
            const roleVal = (row as any).role || (row as any).userRole || '-'
            return roleMap[roleVal] || roleVal || '-'
          }
        },
        {
          prop: 'status',
          label: '状态',
          formatter: (row) => {
            const statusConfig = getUserStatusConfig(row.status)
            return h(ElTag, { type: statusConfig.type }, () => statusConfig.text)
          }
        },
        {
          prop: 'createdAt',
          label: '创建日期',
          sortable: true,
          formatter: (row) => {
            const created = (row as any).created_at || (row as any).createdAt
            if (!created) return '-'
            return new Date(created).toLocaleDateString()
          }
        },
        {
          prop: 'hireDate',
          label: '入职日期',
          sortable: true,
          formatter: (row) => {
            const hireDate = (row as any).hire_date || (row as any).hireDate
            if (!hireDate) return '-'
            // 如果是字符串格式的日期，直接格式化
            if (typeof hireDate === 'string') {
              return new Date(hireDate).toLocaleDateString()
            }
            return new Date(hireDate).toLocaleDateString()
          }
        },
        {
          prop: 'operation',
          label: '操作',
          width: 200,
          fixed: 'right', // 固定列
          formatter: (row) => {
            const isActive = (row as any).status === 'active'
            return h('div', { style: 'display: flex; gap: 8px; justify-content: flex-start;' }, [
              h(ArtButtonTable, {
                type: 'edit',
                onClick: () => showDialog('edit', row)
              }),
              h(ArtButtonTable, {
                icon: isActive ? '&#xe686;' : '&#xe67a;', // 停用/启用图标
                iconColor: isActive ? '#f56c6c' : '#67c23a',
                onClick: () => toggleUserStatus(row)
              } as any),
              h(ArtButtonTable, {
                type: 'delete',
                onClick: () => deleteUser(row)
              })
            ])
          }
        }
      ]
    },
    // 数据处理
    transform: {
      // 数据转换器 - 处理后端返回的数据格式
      dataTransformer: (response: any) => {
        // 标准：{ code, msg, data: { list, total } }
        if (response && response.data && Array.isArray(response.data.list)) {
          return response.data.list
        }
        // 顶层：{ list, total }
        if (response && Array.isArray(response.list)) {
          return response.list
        }
        // 直接数组
        if (Array.isArray(response)) {
          return response
        }
        console.warn('数据转换器: 未识别的数据结构，返回空数组', response)
        return []
      },
      // 响应适配器 - 提供分页信息
      responseAdapter: (response: any) => {
        // 目标：返回标准结构 { records, total, current?, size? }
        // 情况1：后端标准包装 { data: { list, total, current, size } }
        if (response && response.data && response.data.data) {
          const d = response.data.data
          const list = Array.isArray(d?.list) ? d.list : []
          return {
            records: list,
            total: Number(d?.total || list.length || 0),
            current: Number(d?.current || 1),
            size: Number(d?.size || list.length || 20)
          } as any
        }
        // 情况2：较扁平 { data: { list, total } }
        if (
          response &&
          response.data &&
          (Array.isArray(response.data.list) || typeof response.data.total !== 'undefined')
        ) {
          const d = response.data
          const list = Array.isArray(d?.list) ? d.list : []
          return {
            records: list,
            total: Number(d?.total || list.length || 0),
            current: Number(d?.current || 1),
            size: Number(d?.size || list.length || 20)
          } as any
        }
        // 情况3：顶层 { list, total }
        if (response && Array.isArray(response.list)) {
          return {
            records: response.list,
            total: Number(response.total || response.list.length || 0),
            current: Number(response.current || 1),
            size: Number(response.size || response.list.length || 20)
          } as any
        }
        // 情况4：直接数组
        if (Array.isArray(response)) {
          return {
            records: response,
            total: response.length,
            current: 1,
            size: response.length
          } as any
        }
        return { records: [], total: 0, current: 1, size: 20 } as any
      }
    }
  })

  /**
   * 搜索处理
   * @param params 参数
   */
  const handleSearch = (params: Record<string, any>) => {
    // 处理日期区间参数，把 daterange 转换为 startTime 和 endTime
    const { daterange, ...filtersParams } = params
    const [startTime, endTime] = Array.isArray(daterange) ? daterange : [null, null]

    // 搜索参数赋值
    Object.assign(searchParams, { ...filtersParams, startTime, endTime })
    getData()
  }

  /**
   * 显示用户弹窗
   */
  const showDialog = (type: Form.DialogType, row?: UserListItem): void => {
    console.log('打开弹窗:', { type, row })
    dialogType.value = type
    currentUserData.value = row || {}
    nextTick(() => {
      dialogVisible.value = true
    })
  }

  /**
   * 切换用户状态（停用/启用）
   */
  const toggleUserStatus = (row: UserListItem): void => {
    const isActive = (row as any).status === 'active'
    const actionText = isActive ? '停用' : '启用'
    const tipText = isActive ? '停用后该用户将无法登录系统' : '启用后该用户可以正常使用系统'

    ElMessageBox.confirm(`确定要${actionText}该用户吗？${tipText}`, `${actionText}用户`, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(async () => {
        try {
          await userApi.toggleUserStatus(String((row as any).id))
          ElMessage.success(`${actionText}成功`)
          refreshData()
        } catch (error: any) {
          const errorMsg = error?.response?.data?.detail || error?.message || `${actionText}失败`
          ElMessage.error(errorMsg)
        }
      })
      .catch(() => {
        // 取消操作
      })
  }

  /**
   * 删除用户
   */
  const deleteUser = (row: UserListItem): void => {
    console.log('删除用户:', row)

    const userName = (row as any).real_name || (row as any).username
    const confirmMessage = `确定要删除用户「${userName}」吗？

系统会自动处理以下关联数据：

📦 数据转移（转给系统管理员）
   创建的项目、创建的任务、发布的文章
   创建的工作周、协作文档、任务附件、文章编辑历史

🔄 任务处理
   进行中的任务 → 设为未分配
   已完成的任务 → 保留（历史记录）

📊 数据保留
   用户的绩效统计 → 保留（历史记录）

🗑️ 数据删除
   用户的工作日志、文档协作关系

⚠️ 注意：删除操作不可恢复，建议优先使用「停用」功能`

    ElMessageBox.confirm(confirmMessage, '删除用户', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: false,
      distinguishCancelAndClose: true,
      customClass: 'user-delete-confirm'
    })
      .then(async () => {
        try {
          await userApi.deleteUser(String((row as any).id))
          ElMessage.success('删除成功')
          refreshData()
        } catch (error: any) {
          // 显示详细的错误信息
          const errorMsg = error?.response?.data?.detail || error?.message || '删除失败'
          ElMessageBox.alert(errorMsg, '删除失败', {
            confirmButtonText: '知道了',
            type: 'error',
            dangerouslyUseHTMLString: false
          })
        }
      })
      .catch(() => {
        // 取消删除
      })
  }

  /**
   * 处理弹窗提交事件
   */
  const handleDialogSubmit = async () => {
    try {
      dialogVisible.value = false
      currentUserData.value = {}
      refreshData()
    } catch (error) {
      console.error('提交失败:', error)
    }
  }

  /**
   * 处理表格行选择变化
   */
  const handleSelectionChange = (selection: UserListItem[]): void => {
    selectedRows.value = selection
    console.log('选中行数据:', selectedRows.value)
  }
</script>

<style lang="scss" scoped>
  .user-page {
    /* 占满剩余高度并用弹性布局承载卡片，避免顶部/内容被裁切 */
    padding: 10px;
    background: var(--art-bg-color);
    min-height: 100vh;
    display: flex;
    flex-direction: column;

    :deep(.art-table-card) {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

    :deep(.el-card__body) {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

    /* 表格区域自适应填充并滚动，防止被遮挡或溢出 */
    :deep(.el-table) {
      flex: 1;
      min-height: 0;
    }

    :deep(.user) {
      .avatar {
        width: 40px;
        height: 40px;
        margin-left: 0;
        border-radius: 6px;
      }

      > div {
        margin-left: 10px;

        .user-name {
          font-weight: 500;
          color: var(--art-text-gray-800);
        }
      }
    }
  }
</style>

<style lang="scss">
  /* 用户删除确认对话框样式 - 全局样式，不使用 scoped */
  .user-delete-confirm {
    .el-message-box__message {
      white-space: pre-line !important;
      line-height: 1.8 !important;
      font-size: 14px !important;
      color: #606266 !important;
      max-height: 500px !important;
      overflow-y: auto !important;
      text-align: left !important;
    }

    .el-message-box__content {
      padding: 20px !important;
    }

    .el-message-box {
      width: 500px !important;
    }
  }
</style>
