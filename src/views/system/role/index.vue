<template>
  <div class="role-management">
    <!-- 页面头部 -->
    <ArtPageHeader
      title="角色管理"
      description="管理系统角色和权限配置"
      icon="👥"
      badge="Roles"
      theme="pink"
    >
      <template #actions>
        <el-button type="primary" @click="showDialog('add')">
          <el-icon><Plus /></el-icon>
          新增角色
        </el-button>
      </template>
    </ArtPageHeader>

    <!-- 搜索区域 -->
    <ElCard class="art-custom-card">
      <ElForm>
        <ElRow :gutter="12">
          <ElCol :xs="24" :sm="12" :lg="6">
            <ElFormItem>
              <ElInput placeholder="请输入角色名称" v-model="searchForm.roleName"></ElInput>
            </ElFormItem>
          </ElCol>
          <ElCol :xs="24" :sm="12" :lg="6">
            <ElFormItem>
              <ElButton v-ripple @click="searchRoles">搜索</ElButton>
              <ElButton @click="resetSearch" v-ripple>重置</ElButton>
            </ElFormItem>
          </ElCol>
        </ElRow>
      </ElForm>
    </ElCard>

    <!-- 表格区域 -->
    <ElCard class="art-custom-card">
      <ArtTable
        :data="roleList"
        :loading="loading"
        :pagination="pagination"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      >
        <template #default>
          <ElTableColumn label="角色名称" prop="name" />
          <ElTableColumn label="角色编码" prop="role" />
          <ElTableColumn label="描述" prop="description" />
          <ElTableColumn label="启用" prop="is_active">
            <template #default="scope">
              <ElTag :type="scope.row.is_active ? 'primary' : 'info'">
                {{ scope.row.is_active ? '启用' : '禁用' }}
              </ElTag>
            </template>
          </ElTableColumn>
          <ElTableColumn label="创建时间" prop="created_at">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </ElTableColumn>
          <ElTableColumn fixed="right" label="操作" width="100px">
            <template #default="scope">
              <ElRow>
                <!-- 可以在 list 中添加 auth 属性来控制按钮的权限, auth 属性值为权限标识 -->
                <ArtButtonMore
                  :list="[
                    { key: 'permission', label: '菜单权限' },
                    { key: 'edit', label: '编辑角色' },
                    { key: 'delete', label: '删除角色' }
                  ]"
                  @click="buttonMoreClick($event, scope.row)"
                />
              </ElRow>
            </template>
          </ElTableColumn>
        </template>
      </ArtTable>
    </ElCard>

    <ElDialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '✨ 新增角色' : '✏️ 编辑角色'"
      width="600px"
      align-center
      :close-on-click-modal="false"
      class="role-dialog"
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
            <span class="font-bold">新建角色提示</span>
          </template>
          <div class="text-xs mt-1">
            • 角色编码只能包含 <span class="text-primary font-bold">字母和下划线</span><br />
            • 权限字符串自动生成
          </div>
        </el-alert>

        <ElForm ref="formRef" :model="form" :rules="rules" label-width="90px" class="role-form">
          <!-- 基本信息 -->
          <div class="form-section">
            <div class="section-title">
              <el-icon><UserFilled /></el-icon>
              <span>基本信息</span>
            </div>

            <el-row :gutter="20">
              <el-col :span="12">
                <ElFormItem label="角色名称" prop="name">
                  <ElInput v-model="form.name" placeholder="请输入角色名称" clearable>
                    <template #prefix><el-icon><User /></el-icon></template>
                  </ElInput>
                </ElFormItem>
              </el-col>
              <el-col :span="12">
                <ElFormItem label="角色编码" prop="role">
                  <ElInput
                    v-model="form.role"
                    placeholder="如: developer"
                    :disabled="dialogType === 'edit'"
                    clearable
                  >
                    <template #prefix><el-icon><Key /></el-icon></template>
                  </ElInput>
                </ElFormItem>
              </el-col>
            </el-row>

            <ElFormItem label="角色描述" prop="description">
              <ElInput
                v-model="form.description"
                type="textarea"
                :rows="3"
                placeholder="请输入角色描述"
                clearable
              />
            </ElFormItem>

            <ElFormItem label="启用状态">
              <ElSwitch 
                v-model="form.is_active" 
                active-text="启用" 
                inactive-text="禁用" 
                inline-prompt
              />
            </ElFormItem>
          </div>

          <!-- 权限配置 -->
          <div class="form-section">
            <div class="section-title">
              <el-icon><Lock /></el-icon>
              <span>权限配置</span>
            </div>

            <ElFormItem label="权限字符串">
              <ElInput
                v-model="form.permissions"
                type="textarea"
                :rows="2"
                placeholder="由权限树保存后自动生成"
                disabled
              />
              <div class="text-xs text-gray-400 mt-1 flex items-center gap-1">
                <el-icon><InfoFilled /></el-icon>
                <span>保存后点击"菜单权限"按钮配置</span>
              </div>
            </ElFormItem>
          </div>
        </ElForm>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <ElButton @click="dialogVisible = false">取消</ElButton>
          <ElButton type="primary" @click="handleSubmit(formRef)">
            {{ dialogType === 'add' ? '创建角色' : '保存修改' }}
          </ElButton>
        </div>
      </template>
    </ElDialog>

    <ElDialog
      v-model="permissionDialog"
      title="菜单权限"
      width="520px"
      align-center
      class="el-dialog-border"
      append-to-body
      :z-index="3000"
    >
      <ElScrollbar height="70vh">
        <ElTree
          ref="treeRef"
          :data="processedMenuList"
          show-checkbox
          node-key="name"
          :default-expand-all="isExpandAll"
          :default-checked-keys="[1, 2, 3]"
          :props="defaultProps"
          @check="handleTreeCheck"
        >
          <template #default="{ data }">
            <div style="display: flex; align-items: center">
              <span v-if="data.isAuth">
                {{ data.label }}
              </span>
              <span v-else>{{ defaultProps.label(data) }}</span>
            </div>
          </template>
        </ElTree>
      </ElScrollbar>
      <template #footer>
        <div class="dialog-footer">
          <ElButton @click="toggleExpandAll">{{ isExpandAll ? '全部收起' : '全部展开' }}</ElButton>
          <ElButton @click="toggleSelectAll" style="margin-left: 8px">{{
            isSelectAll ? '取消全选' : '全部选择'
          }}</ElButton>
          <ElButton type="primary" @click="savePermission">保存</ElButton>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<script setup lang="ts">
  import { useMenuStore } from '@/store/modules/menu'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    Plus,
    User,
    UserFilled,
    Key,
    Lock,
    InfoFilled,
    Check,
    Close
  } from '@element-plus/icons-vue'
  import type { FormInstance, FormRules } from 'element-plus'
  import { formatMenuTitle } from '@/router/utils/utils'
  import { roleApi } from '@/api/roleApi'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'

  defineOptions({ name: 'Role' })

  const dialogVisible = ref(false)
  const permissionDialog = ref(false)
  const currentRoleId = ref<string>('')
  const { menuList } = storeToRefs(useMenuStore())
  const treeRef = ref()
  const isExpandAll = ref(true)
  const isSelectAll = ref(false)
  const loading = ref(false)

  // 处理菜单数据，将 authList 转换为子节点
  const processedMenuList = computed(() => {
    const processNode = (node: any) => {
      const processed = { ...node }

      // 如果有 authList，将其转换为子节点
      if (node.meta && node.meta.authList && node.meta.authList.length) {
        const authNodes = node.meta.authList.map((auth: any) => ({
          id: `${node.id}_${auth.authMark}`,
          name: `${node.name}_${auth.authMark}`,
          label: auth.title,
          authMark: auth.authMark,
          isAuth: true,
          checked: auth.checked || false
        }))

        processed.children = processed.children ? [...processed.children, ...authNodes] : authNodes
      }

      // 递归处理子节点
      if (processed.children) {
        processed.children = processed.children.map(processNode)
      }

      return processed
    }

    return menuList.value.map(processNode)
  })

  const formRef = ref<FormInstance>()

  const rules = reactive<FormRules>({
    name: [
      { required: true, message: '请输入角色名称', trigger: 'blur' },
      { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
    ],
    role: [
      { required: true, message: '请输入角色编码', trigger: 'blur' },
      { pattern: /^[a-zA-Z_]+$/, message: '角色编码只能包含字母和下划线', trigger: 'blur' }
    ],
    description: [{ required: true, message: '请输入角色描述', trigger: 'blur' }]
  })

  const form = reactive({
    id: '',
    name: '',
    role: '',
    description: '',
    is_active: true,
    permissions: ''
  })

  const searchForm = reactive({
    roleName: ''
  })

  const roleList = ref<any[]>([])
  const pagination = reactive({
    total: 0,
    current: 1,
    size: 10
  })

  onMounted(() => {
    getRoleList()
  })

  const getRoleList = async () => {
    loading.value = true
    try {
      const res = await roleApi.getRoles({
        current: pagination.current,
        size: pagination.size,
        name: searchForm.roleName
      })

      if (res && res.data && Array.isArray(res.data.list)) {
        roleList.value = res.data.list
        pagination.total = res.data.total || 0
      } else {
        roleList.value = []
        pagination.total = 0
      }
    } catch (error) {
      ElMessage.error('获取角色列表失败')
      roleList.value = []
      pagination.total = 0
    } finally {
      loading.value = false
    }
  }

  const handleSizeChange = (size: number) => {
    pagination.size = size
    pagination.current = 1
    getRoleList()
  }

  const handleCurrentChange = (current: number) => {
    pagination.current = current
    getRoleList()
  }

  const searchRoles = () => {
    pagination.current = 1
    getRoleList()
  }

  const resetSearch = () => {
    searchForm.roleName = ''
    pagination.current = 1
    getRoleList()
  }

  const dialogType = ref('add')

  const showDialog = (type: string, row?: any) => {
    dialogVisible.value = true
    dialogType.value = type

    if (type === 'edit' && row) {
      form.id = row.id
      form.name = row.name
      form.role = row.role
      form.description = row.description
      form.is_active = row.is_active
      form.permissions = row.permissions || ''
    } else {
      form.id = ''
      form.name = ''
      form.role = ''
      form.description = ''
      form.is_active = true
      form.permissions = ''
    }
  }

  const buttonMoreClick = (item: any, row: any) => {
    if (item.key === 'permission') {
      showPermissionDialog(row)
    } else if (item.key === 'edit') {
      showDialog('edit', row)
    } else if (item.key === 'delete') {
      deleteRole(row)
    }
  }

  const showPermissionDialog = async (row?: any) => {
    permissionDialog.value = true
    if (row?.id) currentRoleId.value = row.id
    // 读取已勾选权限
    try {
      if (!currentRoleId.value) return
      const res = await roleApi.getRolePermissions(currentRoleId.value)
      const raw = (res as any)?.data
      const checked = Array.isArray(raw)
        ? raw
        : (() => {
            try {
              return JSON.parse(raw || '[]')
            } catch {
              return []
            }
          })()
      await nextTick()
      treeRef.value?.setCheckedKeys(checked)
    } catch (e) {}
  }

  const defaultProps = {
    children: 'children',
    label: (data: any) => formatMenuTitle(data.meta?.title) || ''
  }

  const deleteRole = (row: any) => {
    ElMessageBox.confirm('确定删除该角色吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'error'
    }).then(async () => {
      try {
        await roleApi.deleteRole(row.id)
        ElMessage.success('删除成功')
        getRoleList()
      } catch (error) {
        ElMessage.error('删除失败')
      }
    })
  }

  const handleSubmit = async (formEl: FormInstance | undefined) => {
    if (!formEl) return

    await formEl.validate(async (valid) => {
      if (valid) {
        try {
          if (dialogType.value === 'add') {
            // 新增角色
            await roleApi.createRole(form)
            ElMessage.success('新增成功')
          } else {
            // 编辑角色
            await roleApi.updateRole(form.id, form)
            ElMessage.success('修改成功')
          }
          dialogVisible.value = false
          formEl.resetFields()
          getRoleList()
        } catch (error: any) {
          ElMessage.error(error.message || (dialogType.value === 'add' ? '新增失败' : '修改失败'))
        }
      }
    })
  }

  const savePermission = async () => {
    const tree = treeRef.value
    if (!tree || !currentRoleId.value) return
    const keys = tree.getCheckedKeys()
    await roleApi.updateRolePermissions(currentRoleId.value, keys as string[])
    ElMessage.success('权限保存成功')
    permissionDialog.value = false
  }

  const toggleExpandAll = () => {
    const tree = treeRef.value
    if (!tree) return

    // 使用store.nodesMap直接控制所有节点的展开状态
    const nodes = tree.store.nodesMap
    for (const node in nodes) {
      nodes[node].expanded = !isExpandAll.value
    }

    isExpandAll.value = !isExpandAll.value
  }

  const toggleSelectAll = () => {
    const tree = treeRef.value
    if (!tree) return

    if (!isSelectAll.value) {
      // 全选：获取所有节点的key并设置为选中
      const allKeys = getAllNodeKeys(processedMenuList.value)
      tree.setCheckedKeys(allKeys)
    } else {
      // 取消全选：清空所有选中
      tree.setCheckedKeys([])
    }

    isSelectAll.value = !isSelectAll.value
  }

  const getAllNodeKeys = (nodes: any[]): string[] => {
    const keys: string[] = []
    const traverse = (nodeList: any[]) => {
      nodeList.forEach((node) => {
        if (node.name) {
          keys.push(node.name)
        }
        if (node.children && node.children.length > 0) {
          traverse(node.children)
        }
      })
    }
    traverse(nodes)
    return keys
  }

  const handleTreeCheck = () => {
    const tree = treeRef.value
    if (!tree) return

    // 使用树组件的getCheckedKeys方法获取选中的节点
    const checkedKeys = tree.getCheckedKeys()
    const allKeys = getAllNodeKeys(processedMenuList.value)

    // 判断是否全选：选中的节点数量等于总节点数量
    isSelectAll.value = checkedKeys.length === allKeys.length && allKeys.length > 0
  }

  const formatDate = (date: string) => {
    if (!date) return '-'
    return new Date(date)
      .toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
      .replace(/\//g, '-')
  }
</script>

<style lang="scss" scoped>
  .role-management {
    padding: 20px;
    background: var(--art-bg-color);
    min-height: 100vh;

    // ✅ 头部样式已移至 ArtPageHeader 组件
    /* .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    padding: 20px;
    background: var(--art-main-bg-color);
    border-radius: calc(var(--custom-radius) + 4px);
    border: 1px solid var(--art-card-border);

    .header-left {
      h2 {
        margin: 0 0 8px 0;
        color: var(--art-gray-900);
        font-size: 24px;
        font-weight: 600;
      }

      p {
        margin: 0;
        color: var(--art-gray-600);
        font-size: 14px;
      }
    }
  } */

    .svg-icon {
      width: 1.8em;
      height: 1.8em;
      overflow: hidden;
      vertical-align: -8px;
      fill: currentcolor;
    }
  }

  /* 角色弹窗样式 */
  .role-dialog {
    :deep(.el-dialog__header) {
      padding: 20px 24px;
      margin-right: 0;
      border-bottom: 1px solid var(--art-card-border);
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

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
      padding: 20px;
      background: var(--art-bg-color);
    }

    :deep(.el-dialog__footer) {
      padding: 16px 24px;
      border-top: 1px solid var(--art-card-border);
      background: var(--art-main-bg-color);
    }
  }

  .dialog-content {
    .role-form {
      .form-section {
        margin-bottom: 20px;
        padding: 16px;
        background: var(--art-main-bg-color);
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

        &:last-child {
          margin-bottom: 0;
        }

        .section-title {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 14px;
          padding-bottom: 10px;
          border-bottom: 2px solid var(--art-card-border);
          font-size: 14px;
          font-weight: 600;
          color: var(--art-text-gray-900);

          .el-icon {
            font-size: 16px;
            color: var(--art-primary-color);
          }
        }
      }

      .field-hint {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 6px;
        font-size: 12px;
        color: var(--art-text-gray-500);

        .el-icon {
          font-size: 14px;
        }
      }

      :deep(.el-form-item) {
        margin-bottom: 16px;

        .el-form-item__label {
          font-weight: 500;
          color: var(--art-text-gray-700);
        }

        .el-input__prefix {
          color: var(--art-text-gray-500);
        }
      }
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;

    .el-button {
      min-width: 100px;

      .el-icon {
        margin-right: 4px;
      }
    }
  }

  // Utility classes
  .mb-4 { margin-bottom: 16px; }
  .mt-1 { margin-top: 4px; }
  .text-xs { font-size: 12px; }
  .font-bold { font-weight: 600; }
  .text-primary { color: var(--art-primary-color); }
  .text-gray-400 { color: var(--art-text-gray-400); }
  .flex { display: flex; }
  .items-center { align-items: center; }
  .gap-1 { gap: 4px; }
</style>
