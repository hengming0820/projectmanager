<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-title">总用户数</div>
        <div class="stat-value">{{ userStats.total_users }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">活跃用户</div>
        <div class="stat-value">{{ userStats.active_users }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">管理员</div>
        <div class="stat-value">{{ userStats.admin_users }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">标注员</div>
        <div class="stat-value">{{ userStats.annotator_users }}</div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名或真实姓名"
        style="width: 300px"
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select v-model="filterRole" placeholder="角色筛选" clearable @change="handleFilter">
        <el-option label="管理员" value="admin" />
        <el-option label="标注员" value="annotator" />
      </el-select>

      <el-select v-model="filterStatus" placeholder="状态筛选" clearable @change="handleFilter">
        <el-option label="活跃" value="active" />
        <el-option label="禁用" value="inactive" />
      </el-select>
    </div>

    <!-- 用户列表 -->
    <el-table :data="filteredUsers" v-loading="loading" style="width: 100%" border>
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="realName" label="真实姓名" width="120" />
      <el-table-column prop="email" label="邮箱" width="200" />
      <el-table-column prop="role" label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
            {{ row.role === 'admin' ? '管理员' : '标注员' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="department" label="部门" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '活跃' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.createdAt) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button
            size="small"
            :type="row.status === 'active' ? 'warning' : 'success'"
            @click="handleToggleStatus(row)"
          >
            {{ row.status === 'active' ? '禁用' : '启用' }}
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(row)"
            :disabled="row.id === currentUserId"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingUser ? '编辑用户' : '新增用户'"
      width="500px"
    >
      <el-form ref="userFormRef" :model="userForm" :rules="userRules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            :disabled="!!editingUser"
            placeholder="请输入用户名"
          />
        </el-form-item>

        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="userForm.real_name" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="密码" prop="password" v-if="!editingUser">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="标注员" value="annotator" />
          </el-select>
        </el-form-item>

        <el-form-item label="部门" prop="department">
          <el-input v-model="userForm.department" placeholder="请输入部门" />
        </el-form-item>

        <el-form-item label="头像URL" prop="avatar_url">
          <el-input v-model="userForm.avatar_url" placeholder="请输入头像URL" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingUser ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted } from 'vue'
  import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
  import { Plus, Search } from '@element-plus/icons-vue'
  import { useUserStore } from '@/store/modules/user'
  import type { User, UserCreate, UserUpdate } from '@/types/project'

  const userStore = useUserStore()

  // 响应式数据
  const loading = ref(false)
  const showCreateDialog = ref(false)
  const editingUser = ref<User | null>(null)
  const submitting = ref(false)
  const searchKeyword = ref('')
  const filterRole = ref('')
  const filterStatus = ref('')
  const currentPage = ref(1)
  const pageSize = ref(20)
  const currentUserId = ref('') // 当前登录用户ID

  // 表单相关
  const userFormRef = ref<FormInstance>()
  const userForm = reactive<UserCreate>({
    username: '',
    real_name: '',
    email: '',
    password: '',
    role: 'annotator',
    department: '',
    avatar_url: ''
  })

  // 表单验证规则
  const userRules: FormRules = {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
    ],
    real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
    ],
    role: [{ required: true, message: '请选择角色', trigger: 'change' }]
  }

  // 计算属性
  const filteredUsers = computed(() => {
    let users = userStore.users

    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      users = users.filter(
        (user) =>
          user.username.toLowerCase().includes(keyword) ||
          user.realName.toLowerCase().includes(keyword)
      )
    }

    if (filterRole.value) {
      users = users.filter((user) => user.role === filterRole.value)
    }

    if (filterStatus.value) {
      users = users.filter((user) => user.status === filterStatus.value)
    }

    return users
  })

  const userStats = computed(() => userStore.userStats)
  const total = computed(() => userStore.total)

  // 方法
  const loadUsers = async () => {
    loading.value = true
    try {
      await userStore.fetchUsers({
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      })
      await userStore.fetchUserStats()
    } catch {
      ElMessage.error('加载用户列表失败')
    } finally {
      loading.value = false
    }
  }

  const handleSearch = () => {
    // 实时搜索，不需要额外处理
  }

  const handleFilter = () => {
    // 筛选功能通过计算属性实现
  }

  const handleSizeChange = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    loadUsers()
  }

  const handleCurrentChange = (page: number) => {
    currentPage.value = page
    loadUsers()
  }

  const resetForm = () => {
    userForm.username = ''
    userForm.real_name = ''
    userForm.email = ''
    userForm.password = ''
    userForm.role = 'annotator'
    userForm.department = ''
    userForm.avatar_url = ''
    editingUser.value = null
  }

  const handleEdit = (user: User) => {
    editingUser.value = user
    userForm.username = user.username
    userForm.real_name = user.realName
    userForm.email = user.email
    userForm.role = user.role
    userForm.department = user.department || ''
    userForm.avatar_url = user.avatar || ''
    showCreateDialog.value = true
  }

  const handleSubmit = async () => {
    if (!userFormRef.value) return

    await userFormRef.value.validate(async (valid) => {
      if (valid) {
        submitting.value = true
        try {
          if (editingUser.value) {
            // 更新用户
            const updateData: UserUpdate = {
              real_name: userForm.real_name,
              email: userForm.email,
              role: userForm.role,
              department: userForm.department,
              avatar_url: userForm.avatar_url
            }
            await userStore.updateUser(editingUser.value.id, updateData)
            ElMessage.success('用户更新成功')
          } else {
            // 创建用户
            await userStore.createUser({ ...userForm })
            ElMessage.success('用户创建成功')
          }
          showCreateDialog.value = false
          resetForm()
          loadUsers()
        } catch (error: any) {
          ElMessage.error(error.message || '操作失败')
        } finally {
          submitting.value = false
        }
      }
    })
  }

  const handleToggleStatus = async (user: User) => {
    try {
      await ElMessageBox.confirm(
        `确定要${user.status === 'active' ? '禁用' : '启用'}用户 "${user.realName}" 吗？`,
        '确认操作',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      await userStore.toggleUserStatus(user.id)
      ElMessage.success(`用户已${user.status === 'active' ? '禁用' : '启用'}`)
      loadUsers()
    } catch (error: any) {
      if (error !== 'cancel') {
        ElMessage.error(error.message || '操作失败')
      }
    }
  }

  const handleDelete = async (user: User) => {
    try {
      await ElMessageBox.confirm(
        `确定要删除用户 "${user.realName}" 吗？此操作不可恢复！`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      await userStore.deleteUser(user.id)
      ElMessage.success('用户删除成功')
      loadUsers()
    } catch (error: any) {
      if (error !== 'cancel') {
        ElMessage.error(error.message || '删除失败')
      }
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN')
  }

  // 生命周期
  onMounted(() => {
    loadUsers()
    // 这里应该从用户认证信息中获取当前用户ID
    // currentUserId.value = getCurrentUserId()
  })
</script>

<style scoped lang="scss">
  .user-management {
    padding: 20px;

    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      h2 {
        margin: 0;
        color: #303133;
      }
    }

    .stats-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 20px;

      .stat-card {
        background: #fff;
        border: 1px solid #e6e6e6;
        border-radius: 8px;
        padding: 20px;
        text-align: center;

        .stat-title {
          color: #666;
          font-size: 14px;
          margin-bottom: 8px;
        }

        .stat-value {
          color: #303133;
          font-size: 24px;
          font-weight: bold;
        }
      }
    }

    .search-bar {
      display: flex;
      gap: 15px;
      margin-bottom: 20px;
      align-items: center;
    }

    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
</style>
