<template>
  <div class="work-log-week-detail">
    <!-- 工作日志表格卡片 -->
    <el-card class="art-custom-card table-card">
      <template #header>
        <div class="table-header">
          <div class="header-left">
            <div class="header-info">
              <h3>{{ workWeek?.title || '工作周详情' }}</h3>
              <span v-if="workWeek" class="date-info">
                {{ formatDateRange(workWeek.week_start_date, workWeek.week_end_date) }}
                <el-tag
                  :type="getWeekStatusType(workWeek.status)"
                  size="small"
                  style="margin-left: 8px"
                >
                  {{ getWeekStatusText(workWeek.status) }}
                </el-tag>
                <el-tag
                  v-if="workWeek && (workWeek as any).config?.covered_user_ids?.length"
                  type="info"
                  effect="plain"
                  size="small"
                  style="margin-left: 8px"
                >
                  覆盖员工数：{{ (workWeek as any).config.covered_user_ids.length }}
                </el-tag>
              </span>
            </div>
          </div>
          <div class="header-actions">
            <el-button
              v-if="userStore.hasPermission('WorkLogManagement') && workWeek?.status === 'active'"
              @click="handleArchiveWeek"
              size="default"
            >
              <el-icon><Finished /></el-icon>
              归档工作周
            </el-button>
            <el-button
              v-if="userStore.hasPermission('WorkLogManagement') && workWeek?.status === 'archived'"
              @click="handleUnarchiveWeek"
              type="info"
              size="default"
            >
              <el-icon><RefreshLeft /></el-icon>
              恢复归档
            </el-button>
            <el-button
              v-if="userStore.hasPermission('WorkLogManagement')"
              @click="showManageCoveredUsers = true"
              type="primary"
              size="default"
            >
              <el-icon><User /></el-icon>
              管理覆盖员工
            </el-button>
            <el-button @click="showStatistics = true" size="default">
              <el-icon><DataAnalysis /></el-icon>
              统计报表
            </el-button>
            <el-button type="warning" @click="exportWorkLog" size="default">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
            <el-button type="success" @click="refreshData" size="default">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <div class="table-layout">
        <!-- 表格区域（全宽） -->
        <div class="table-container">
          <el-table v-loading="loading" :data="displayRows" stripe border class="work-log-table">
            <!-- 用户信息列 -->
            <el-table-column label="姓名" width="120" fixed="left">
              <template #default="{ row }">
                <div class="user-info">
                  <div class="user-name">{{ row.userName }}</div>
                  <div class="user-meta">{{ row.realName || row.department || '-' }}</div>
                </div>
              </template>
            </el-table-column>

            <!-- 工作日列 -->
            <el-table-column
              v-for="(day, index) in workDays"
              :key="day.date"
              :label="day.label"
              min-width="240"
            >
              <template #default="{ row }">
                <div class="work-day-cell">
                  <WorkLogEntryCell
                    :entry="getEntryForDay(row, index)"
                    :entries="getEntriesForDay(row, index)"
                    :work-date="day.date"
                    :day-name="day.label"
                    :user-id="row.userId"
                    :work-week-id="workWeekId"
                    :can-edit="canEditEntry(row.userId, getEntryForDay(row, index))"
                    @entry-updated="handleEntryUpdated"
                    @entry-deleted="handleEntryDeleted"
                    @entry-submitted="handleEntrySubmitted"
                  />
                </div>
              </template>
            </el-table-column>
          </el-table>
          <!-- 真正的空状态：工作周未配置覆盖用户 -->
          <div v-if="!loading && coveredUserIds.length === 0" class="empty-guidance">
            <el-empty description="工作周未配置">
              <div class="tips">当前工作周尚未配置覆盖人员</div>
              <el-button type="primary" @click="$router.push('/work-log')"
                >返回工作周列表</el-button
              >
            </el-empty>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 统计报表对话框 -->
    <el-dialog
      v-model="showStatistics"
      title="工作周统计报表"
      width="90%"
      top="5vh"
      :close-on-click-modal="false"
      append-to-body
      :z-index="3000"
      class="statistics-dialog"
    >
      <WorkLogStatistics v-if="showStatistics && workWeekId" :work-week-id="workWeekId" />
    </el-dialog>

    <!-- 导出报告对话框 -->
    <el-dialog
      v-model="showExportDialog"
      title="导出工作日志报告"
      width="500px"
      :close-on-click-modal="false"
      append-to-body
      :z-index="3000"
    >
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="报告类型">
          <el-radio-group v-model="exportForm.reportType">
            <el-radio label="single">单个工作周</el-radio>
            <el-radio label="monthly">月度报告</el-radio>
            <el-radio label="quarterly">季度报告</el-radio>
            <el-radio label="yearly">年度报告</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 单个工作周提示 -->
        <el-alert
          v-if="exportForm.reportType === 'single'"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          将导出当前工作周：<strong>{{ workWeek?.title }}</strong>
        </el-alert>

        <!-- 月度报告选择 -->
        <template v-if="exportForm.reportType === 'monthly'">
          <el-form-item label="选择年份">
            <el-date-picker
              v-model="exportForm.year"
              type="year"
              placeholder="选择年份"
              value-format="YYYY"
              :clearable="false"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="选择月份">
            <el-select v-model="exportForm.month" placeholder="选择月份" style="width: 100%">
              <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
            </el-select>
          </el-form-item>
        </template>

        <!-- 季度报告选择 -->
        <template v-if="exportForm.reportType === 'quarterly'">
          <el-form-item label="选择年份">
            <el-date-picker
              v-model="exportForm.year"
              type="year"
              placeholder="选择年份"
              value-format="YYYY"
              :clearable="false"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="选择季度">
            <el-select v-model="exportForm.quarter" placeholder="选择季度" style="width: 100%">
              <el-option label="第一季度 (1-3月)" :value="1" />
              <el-option label="第二季度 (4-6月)" :value="2" />
              <el-option label="第三季度 (7-9月)" :value="3" />
              <el-option label="第四季度 (10-12月)" :value="4" />
            </el-select>
          </el-form-item>
        </template>

        <!-- 年度报告选择 -->
        <template v-if="exportForm.reportType === 'yearly'">
          <el-form-item label="选择年份">
            <el-date-picker
              v-model="exportForm.year"
              type="year"
              placeholder="选择年份"
              value-format="YYYY"
              :clearable="false"
              style="width: 100%"
            />
          </el-form-item>
        </template>
      </el-form>

      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" :loading="exportLoading" @click="confirmExport">
          <el-icon v-if="!exportLoading"><Download /></el-icon>
          {{ exportLoading ? '生成中...' : '导出报告' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 管理覆盖员工对话框 -->
    <el-dialog
      v-model="showManageCoveredUsers"
      title="管理覆盖员工"
      width="750px"
      :close-on-click-modal="false"
      append-to-body
      :z-index="3000"
    >
      <div class="manage-covered-users">
        <el-alert type="info" :closable="false" style="margin-bottom: 20px">
          <template #title>
            <span style="font-weight: 600">提示</span>
          </template>
          <div style="font-size: 13px; line-height: 1.6">
            • 添加员工后，该员工将出现在工作周列表中，初始状态为"暂无日志"<br />
            • 移除员工不会删除已有的日志条目<br />
            • 当前已覆盖
            <span style="color: #409eff; font-weight: 600">{{ coveredUserIds.length }}</span> 名员工
          </div>
        </el-alert>

        <div class="user-selector-custom">
          <!-- 左侧：按部门分组的可选员工 -->
          <div class="left-panel">
            <div class="panel-header">
              <span class="panel-title">可选员工</span>
              <span class="panel-count">{{ availableUsersList.length }}</span>
            </div>
            <div class="panel-search">
              <el-input v-model="leftSearchText" placeholder="搜索员工" clearable size="small">
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
            <div class="panel-body">
              <el-scrollbar height="380px">
                <el-collapse v-model="expandedDepts" accordion>
                  <el-collapse-item
                    v-for="dept in filteredDepartmentGroups"
                    :key="dept.name"
                    :name="dept.name"
                  >
                    <template #title>
                      <div class="dept-title">
                        <span class="dept-name">{{ dept.name }}</span>
                        <span class="dept-count">({{ dept.users.length }})</span>
                      </div>
                    </template>
                    <div class="dept-users">
                      <el-checkbox
                        v-for="user in dept.users"
                        :key="user.id"
                        :label="user.id"
                        :model-value="selectedCoveredUserIds.includes(user.id)"
                        @change="(val) => toggleUser(user.id, val)"
                        class="user-checkbox"
                      >
                        {{ user.label }}
                      </el-checkbox>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </el-scrollbar>
            </div>
          </div>

          <!-- 右侧：已覆盖员工 -->
          <div class="right-panel">
            <div class="panel-header">
              <span class="panel-title">已覆盖员工</span>
              <span class="panel-count">{{ selectedCoveredUserIds.length }}</span>
            </div>
            <div class="panel-search">
              <el-input v-model="rightSearchText" placeholder="搜索员工" clearable size="small">
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
            <div class="panel-body">
              <el-scrollbar height="380px">
                <div v-if="filteredSelectedUsers.length === 0" class="empty-state">
                  <el-icon class="empty-icon"><User /></el-icon>
                  <p class="empty-text">暂无已覆盖员工</p>
                </div>
                <div v-else class="selected-users-list">
                  <div
                    v-for="user in filteredSelectedUsers"
                    :key="user.id"
                    class="selected-user-item"
                  >
                    <div class="user-info-wrapper">
                      <div class="user-avatar">
                        {{ user.label.charAt(0) }}
                      </div>
                      <div class="user-details">
                        <span class="user-name">{{ user.label }}</span>
                        <span class="user-dept">{{ user.department || '未分配部门' }}</span>
                      </div>
                    </div>
                    <el-button
                      type="danger"
                      text
                      circle
                      size="small"
                      @click="removeUser(user.id)"
                      class="remove-btn"
                    >
                      <el-icon><Close /></el-icon>
                    </el-button>
                  </div>
                </div>
              </el-scrollbar>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showManageCoveredUsers = false">取消</el-button>
          <el-button type="primary" @click="handleUpdateCoveredUsers" :loading="savingCoveredUsers">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    ArrowLeft,
    ArrowRight,
    DataAnalysis,
    Download,
    Refresh,
    User,
    Check,
    Clock,
    Trophy,
    Search,
    Finished,
    RefreshLeft,
    Close
  } from '@element-plus/icons-vue'
  import { useUserStore } from '@/store/modules/user'
  import { workWeekApi, workLogEntryApi, workLogUtils } from '@/api/workLogApi'
  import { userApi } from '@/api/userApi'
  import type {
    WorkWeek,
    WorkLogEntry,
    WorkLogTableRow,
    WorkWeekStatistics as WorkWeekStatsType
  } from '@/types/work-log'
  import WorkLogEntryCell from './components/WorkLogEntryCell.vue'
  import WorkLogStatistics from './components/WorkLogStatistics.vue'

  // Props 定义
  const props = defineProps<{
    weekId?: string
  }>()

  // Emits 定义
  const emit = defineEmits<{
    refresh: []
  }>()

  const route = useRoute()
  const userStore = useUserStore()

  // 响应式数据
  const loading = ref(false)
  const showStatistics = ref(false)
  const showManageCoveredUsers = ref(false)
  const savingCoveredUsers = ref(false)
  const selectedCoveredUserIds = ref<string[]>([])
  const allActiveUsers = ref<
    Array<{ id: string; username: string; real_name?: string; department?: string }>
  >([])
  // 优先使用 props.weekId，如果没有则从路由参数获取
  const workWeekId = ref(props.weekId || (route.params.weekId as string))
  const workWeek = ref<WorkWeek | null>(null)
  const coveredUserIds = ref<string[]>([])
  const coveredUsers = ref<Array<{ id: string; name: string; department?: string }>>([])
  // 筛选状态
  const filterSearch = ref('')
  const filterRoles = ref<string[]>([])
  const filterDepts = ref<string[]>([])
  // 管理覆盖员工 - 自定义选择器状态
  const leftSearchText = ref('')
  const rightSearchText = ref('')
  const expandedDepts = ref<string>('') // accordion 模式，只能展开一个
  const roleOptions = ['admin', 'annotator', 'reviewer']
  const deptOptions = ref<string[]>([])
  const workLogEntries = ref<WorkLogEntry[]>([])
  const tableData = ref<WorkLogTableRow[]>([])
  // 管理权限（可生成所有成员条目）
  const canManage = computed(
    () => userStore.hasPermission('WorkLogManagement') || userStore.hasPermission('WorkLogEdit')
  )
  // 筛选功能已移除

  // 可选用户列表
  const availableUsersList = computed(() => {
    return allActiveUsers.value.map((user) => ({
      id: user.id,
      label: user.real_name || user.username,
      department: user.department || '未分配部门'
    }))
  })

  // 按部门分组的用户列表
  const departmentGroups = computed(() => {
    const groups: Record<string, typeof availableUsersList.value> = {}

    availableUsersList.value.forEach((user) => {
      const dept = user.department || '未分配部门'
      if (!groups[dept]) {
        groups[dept] = []
      }
      groups[dept].push(user)
    })

    // 转换为数组格式，并按部门名排序
    return Object.entries(groups)
      .map(([name, users]) => ({
        name,
        users: users.sort((a, b) => a.label.localeCompare(b.label, 'zh-CN'))
      }))
      .sort((a, b) => {
        // "未分配部门"排在最后
        if (a.name === '未分配部门') return 1
        if (b.name === '未分配部门') return -1
        return a.name.localeCompare(b.name, 'zh-CN')
      })
  })

  // 根据左侧搜索筛选部门分组
  const filteredDepartmentGroups = computed(() => {
    if (!leftSearchText.value.trim()) {
      return departmentGroups.value
    }

    const searchLower = leftSearchText.value.toLowerCase()
    return departmentGroups.value
      .map((dept) => ({
        ...dept,
        users: dept.users.filter(
          (user) =>
            user.label.toLowerCase().includes(searchLower) ||
            user.department.toLowerCase().includes(searchLower)
        )
      }))
      .filter((dept) => dept.users.length > 0)
  })

  // 已选择的用户列表（用于右侧显示）
  const selectedUsers = computed(() => {
    return availableUsersList.value.filter((user) => selectedCoveredUserIds.value.includes(user.id))
  })

  // 根据右侧搜索筛选已选择的用户
  const filteredSelectedUsers = computed(() => {
    if (!rightSearchText.value.trim()) {
      return selectedUsers.value
    }

    const searchLower = rightSearchText.value.toLowerCase()
    return selectedUsers.value.filter(
      (user) =>
        user.label.toLowerCase().includes(searchLower) ||
        user.department.toLowerCase().includes(searchLower)
    )
  })

  // 统计数据
  const statistics = reactive({
    totalUsers: 0,
    totalEntries: 0,
    submittedEntries: 0,
    totalActualHours: 0,
    completionRate: 0
  })

  // 计算属性
  const workDays = computed(() => {
    if (!workWeek.value) return []

    const days = []
    const startDate = new Date(workWeek.value.week_start_date)
    const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    for (let i = 0; i < 7; i++) {
      const date = new Date(startDate)
      date.setDate(startDate.getDate() + i)

      days.push({
        date: date.toISOString().split('T')[0],
        label: `${dayNames[i]} (${date.getMonth() + 1}/${date.getDate()})`
      })
    }

    return days
  })

  // 筛选计算属性已移除，直接使用 tableData

  const canEditEntry = computed(() => {
    return (userId: string, entry?: WorkLogEntry) => {
      const currentUserId = userStore.currentUser?.id
      const isOwnEntry = userId === currentUserId
      const isPending = !entry || entry.status === 'pending'

      // 所有用户（包括管理员）只能编辑自己的条目，且状态为 pending
      return isOwnEntry && isPending
    }
  })

  // 方法
  const fetchWorkWeek = async () => {
    try {
      console.log('📡 [WorkLogDetail] 获取工作周详情，ID:', workWeekId.value)
      const response = await workWeekApi.getWorkWeek(workWeekId.value)
      console.log('✅ [WorkLogDetail] 工作周详情获取成功:', response)
      // backendApi 返回的是完整响应对象 { code, msg, data: {...} }
      const data = (response as any).data || response
      workWeek.value = data as any
      const cfg: any = (workWeek.value as any)?.config || {}
      coveredUserIds.value = Array.isArray(cfg.covered_user_ids) ? cfg.covered_user_ids : []
    } catch (error) {
      console.error('❌ [WorkLogDetail] 获取工作周详情失败:', error)
      ElMessage.error('获取工作周详情失败')
    }
  }

  const fetchWorkLogEntries = async () => {
    loading.value = true
    try {
      console.log('📡 [WorkLogDetail] 获取工作日志条目，工作周ID:', workWeekId.value)
      const response = await workLogEntryApi.getWorkLogEntries(workWeekId.value)
      console.log('✅ [WorkLogDetail] 工作日志条目获取成功:', response)
      // backendApi 返回的是完整响应对象 { code, msg, data: [...] }
      const data = (response as any).data || response
      workLogEntries.value = Array.isArray(data) ? data : []
      console.log('📋 [WorkLogDetail] 解析后的条目数量:', workLogEntries.value.length)
      await ensureCoveredUsersLoaded()
      buildTableData()
      calculateStatistics()
      console.log('📋 [WorkLogDetail] 表格数据构建完成，条目数量:', workLogEntries.value.length)
    } catch (error) {
      console.error('❌ [WorkLogDetail] 获取工作日志条目失败:', error)
      ElMessage.error('获取工作日志条目失败')
    } finally {
      loading.value = false
    }
  }

  // 加载覆盖员工的基本信息（用于渲染空行）
  const ensureCoveredUsersLoaded = async () => {
    if (!coveredUserIds.value?.length) {
      coveredUsers.value = []
      return
    }
    try {
      const res: any = await userApi.getUsersBasic({ status: 'active', size: 9999 })
      const list: any[] = res?.list || res?.data?.list || res?.data || []
      const idSet = new Set(coveredUserIds.value)
      coveredUsers.value = list
        .filter((u: any) => idSet.has(u.id))
        .map((u: any) => ({
          id: u.id,
          name: u.real_name || u.username,
          department: u.department,
          role: (u.role || '').toLowerCase()
        }))
      // 汇总部门选项
      const depts = new Set<string>()
      coveredUsers.value.forEach((u: any) => {
        if (u.department) depts.add(u.department)
      })
      deptOptions.value = Array.from(depts)
    } catch (e) {
      coveredUsers.value = coveredUserIds.value.map((id) => ({ id, name: id }))
    }
  }

  const buildTableData = () => {
    const data: WorkLogTableRow[] = []

    // 基于覆盖员工先构造空行
    const coveredMap = new Map<string, WorkLogTableRow>()
    coveredUsers.value.forEach((u) => {
      const row: WorkLogTableRow = {
        userId: u.id,
        userName: u.name,
        realName: u.name,
        department: u.department
      }
      coveredMap.set(u.id, row)
    })

    // 把已有条目归并到对应用户行
    // 先按用户和日期分组，然后选择最早创建的条目作为主条目
    const entriesByUserAndDay = new Map<string, WorkLogEntry[]>()

    workLogEntries.value.forEach((entry) => {
      const key = `${entry.user_id}-${entry.day_of_week}`
      if (!entriesByUserAndDay.has(key)) {
        entriesByUserAndDay.set(key, [])
      }
      entriesByUserAndDay.get(key)!.push(entry)
    })

    // 对每个用户每天的条目按创建时间排序，选择最早创建的作为主条目
    entriesByUserAndDay.forEach((entries, key) => {
      // 按创建时间排序：先创建的在前
      entries.sort((a, b) => {
        const timeA = new Date(a.created_at || 0).getTime()
        const timeB = new Date(b.created_at || 0).getTime()
        return timeA - timeB
      })

      const mainEntry = entries[0] // 最早创建的条目
      const [userId, dayOfWeekStr] = key.split('-')
      const dayOfWeek = parseInt(dayOfWeekStr)

      // 优先从 coveredMap 获取，确保使用 real_name
      let row = coveredMap.get(userId)
      if (!row) {
        // 如果不在覆盖用户中，尝试从 coveredUsers 查找
        const user = coveredUsers.value.find((u) => u.id === userId)
        row = {
          userId: userId,
          userName: user?.name || mainEntry.user_name || `用户${userId}`,
          realName: user?.name || mainEntry.user_name || `用户${userId}`,
          department: user?.department
        } as WorkLogTableRow
      }

      // 设置主条目（最早创建的）
      switch (dayOfWeek) {
        case 1:
          row.monday = mainEntry
          break
        case 2:
          row.tuesday = mainEntry
          break
        case 3:
          row.wednesday = mainEntry
          break
        case 4:
          row.thursday = mainEntry
          break
        case 5:
          row.friday = mainEntry
          break
      }

      coveredMap.set(userId, row)
    })

    // 计算汇总并输出行集
    coveredMap.forEach((row) => {
      // 收集每天的所有条目（支持一天多条日志）
      const daysEntries = [
        getEntriesForDay(row, 0), // 周一
        getEntriesForDay(row, 1), // 周二
        getEntriesForDay(row, 2), // 周三
        getEntriesForDay(row, 3), // 周四
        getEntriesForDay(row, 4), // 周五
        getEntriesForDay(row, 5), // 周六
        getEntriesForDay(row, 6) // 周日
      ]

      // 所有工作日志条目（展平）
      const allEntries = daysEntries.flat().filter(Boolean) as WorkLogEntry[]

      // 按天分组计算
      let totalActualHours = 0
      let totalLeaveHours = 0 // 请假总时长
      let submittedDays = 0
      let totalDaysWithEntries = 0

      daysEntries.forEach((dayEntries) => {
        if (dayEntries.length > 0) {
          totalDaysWithEntries++

          // 计算当天的总时长
          const dayActual = dayEntries.reduce((sum, e) => sum + (e.actual_hours || 0), 0)

          // 计算请假时长（工作类型为 请假/病假/年假 的条目）
          const dayLeave = dayEntries
            .filter((e) => ['请假', '病假', '年假'].includes(e.work_type || ''))
            .reduce((sum, e) => sum + (e.actual_hours || 0), 0)

          totalActualHours += dayActual
          totalLeaveHours += dayLeave

          // 如果当天至少有一个条目已提交或通过，则算作已提交
          if (dayEntries.some((e) => ['submitted', 'approved'].includes(e.status))) {
            submittedDays++
          }
        }
      })

      // 计划时间固定为每天8小时
      // 如果没有任何日志条目，默认7天56小时；否则按实际有日志的天数计算
      const totalPlannedHours = totalDaysWithEntries === 0 ? 56 : totalDaysWithEntries * 8

      // 计算完成率：(实际工作时长) / (计划时长 - 请假时长) * 100
      // 请假不算作未完成的工作
      const effectivePlannedHours = Math.max(totalPlannedHours - totalLeaveHours, 0.01) // 避免除以0
      const workCompletionRate =
        effectivePlannedHours > 0
          ? ((totalActualHours - totalLeaveHours) / effectivePlannedHours) * 100
          : 0

      row.weekSummary = {
        totalPlannedHours,
        totalActualHours,
        averageCompletionRate: Math.min(workCompletionRate, 100), // 最高100%
        submittedDays,
        totalDays: totalDaysWithEntries
      }
      data.push(row)
    })

    tableData.value = data
  }

  // 角色文本
  const roleLabel = (r: string) =>
    r === 'admin' ? '管理员' : r === 'annotator' ? '标注员' : r === 'reviewer' ? '算法工程师' : r

  // 显示行（按筛选）
  const displayRows = computed(() => {
    const rows = tableData.value
    const search = (filterSearch.value || '').trim().toLowerCase()
    const roles = new Set(filterRoles.value)
    const depts = new Set(filterDepts.value)
    return rows.filter((row) => {
      const nameOk = !search || (row.userName || '').toLowerCase().includes(search)
      const user = coveredUsers.value.find((u) => u.id === row.userId)
      const roleOk = roles.size === 0 || (user && roles.has((user as any).role))
      const deptOk = depts.size === 0 || (user && user.department && depts.has(user.department))
      return nameOk && roleOk && deptOk
    })
  })

  const calculateStatistics = () => {
    statistics.totalUsers = tableData.value.length
    statistics.totalEntries = workLogEntries.value.length
    statistics.submittedEntries = workLogEntries.value.filter((entry) =>
      ['submitted', 'approved'].includes(entry.status)
    ).length
    statistics.totalActualHours = workLogEntries.value.reduce(
      (sum, entry) => sum + (entry.actual_hours || 0),
      0
    )
    statistics.completionRate =
      statistics.totalEntries > 0
        ? (statistics.submittedEntries / statistics.totalEntries) * 100
        : 0
  }

  // 获取某天的第一个条目（用于兼容旧版组件）
  const getEntryForDay = (row: WorkLogTableRow, dayIndex: number): WorkLogEntry | undefined => {
    switch (dayIndex) {
      case 0:
        return row.monday
      case 1:
        return row.tuesday
      case 2:
        return row.wednesday
      case 3:
        return row.thursday
      case 4:
        return row.friday
      default:
        return undefined
    }
  }

  // 获取某天的所有条目（支持多条目）
  const getEntriesForDay = (row: WorkLogTableRow, dayIndex: number): WorkLogEntry[] => {
    const entries = []
    const mainEntry = getEntryForDay(row, dayIndex)
    if (mainEntry) {
      entries.push(mainEntry)
    }

    // 查找同一天的其他条目
    const targetDate = workDays.value[dayIndex]?.date
    if (targetDate) {
      const additionalEntries = workLogEntries.value.filter(
        (entry) =>
          entry.user_id === row.userId &&
          entry.work_date === targetDate &&
          entry.id !== mainEntry?.id
      )
      entries.push(...additionalEntries)
    }

    // 按创建时间排序：先创建的在前（序号小），后创建的在后（序号大）
    entries.sort((a, b) => {
      const timeA = new Date(a.created_at || 0).getTime()
      const timeB = new Date(b.created_at || 0).getTime()
      return timeA - timeB // 升序：时间早的在前面
    })

    return entries
  }

  const handleEntryUpdated = (entry: WorkLogEntry) => {
    console.log('🔄 [WorkLogDetail] 条目更新事件:', entry)

    // 更新本地数据
    const index = workLogEntries.value.findIndex((e) => e.id === entry.id)
    if (index >= 0) {
      // 更新现有条目
      workLogEntries.value[index] = entry
      console.log('✏️ [WorkLogDetail] 更新现有条目:', entry.id)
    } else {
      // 添加新条目
      workLogEntries.value.push(entry)
      console.log('➕ [WorkLogDetail] 添加新条目:', entry.id)
    }

    buildTableData()
    calculateStatistics()
  }

  const handleEntrySubmitted = (entry: WorkLogEntry) => {
    console.log('🚀 [WorkLogDetail] 条目提交事件:', entry)
    handleEntryUpdated(entry)
    ElMessage.success('提交成功')
  }

  const handleEntryDeleted = (entryId: string) => {
    console.log('🗑️ [WorkLogDetail] 条目删除事件:', entryId)

    // 从本地数据中移除
    const index = workLogEntries.value.findIndex((e) => e.id === entryId)
    if (index >= 0) {
      workLogEntries.value.splice(index, 1)
      console.log('✅ [WorkLogDetail] 已从本地数据中移除条目:', entryId)

      // 重新构建表格数据
      buildTableData()
    } else {
      console.warn('⚠️ [WorkLogDetail] 未找到要删除的条目:', entryId)
    }
  }

  // 加载所有活跃用户
  const loadActiveUsers = async () => {
    try {
      const res: any = await userApi.getUsersBasic({ status: 'active', size: 9999 })
      const list: any[] = res?.list || res?.data?.list || res?.data || []
      allActiveUsers.value = list
      console.log('✅ [WorkLogDetail] 已加载活跃用户:', allActiveUsers.value.length, '名')
    } catch (error) {
      console.error('❌ [WorkLogDetail] 加载活跃用户失败:', error)
      ElMessage.error('加载用户列表失败')
    }
  }

  // 左侧：切换用户选择状态（勾选/取消勾选）
  const toggleUser = (userId: string, checked: boolean | string | number) => {
    const isChecked = !!checked
    if (isChecked) {
      if (!selectedCoveredUserIds.value.includes(userId)) {
        selectedCoveredUserIds.value.push(userId)
      }
    } else {
      const index = selectedCoveredUserIds.value.indexOf(userId)
      if (index > -1) {
        selectedCoveredUserIds.value.splice(index, 1)
      }
    }
  }

  // 右侧：移除单个用户
  const removeUser = (userId: string) => {
    const index = selectedCoveredUserIds.value.indexOf(userId)
    if (index > -1) {
      selectedCoveredUserIds.value.splice(index, 1)
    }
  }

  // 更新覆盖员工
  const handleUpdateCoveredUsers = async () => {
    try {
      savingCoveredUsers.value = true
      console.log('💾 [WorkLogDetail] 更新覆盖员工:', selectedCoveredUserIds.value)

      // 更新工作周配置
      const currentConfig = (workWeek.value as any)?.config || {}
      await workWeekApi.updateWorkWeek(workWeekId.value, {
        config: {
          ...currentConfig,
          covered_user_ids: selectedCoveredUserIds.value
        }
      })

      console.log('✅ [WorkLogDetail] 工作周配置更新成功')

      ElMessage.success('覆盖员工更新成功')
      showManageCoveredUsers.value = false

      // 刷新数据
      await refreshData()
    } catch (error) {
      console.error('❌ [WorkLogDetail] 更新覆盖员工失败:', error)
      ElMessage.error('更新失败，请重试')
    } finally {
      savingCoveredUsers.value = false
    }
  }

  const refreshData = async () => {
    console.log('🔄 [WorkLogDetail] 刷新数据，工作周ID:', workWeekId.value)
    // 先获取工作周信息（包含 covered_user_ids）
    await fetchWorkWeek()
    // 再获取工作日志条目（依赖 covered_user_ids）
    await fetchWorkLogEntries()
    console.log('✅ [WorkLogDetail] 数据刷新完成')
  }

  // resetFilters 函数已移除

  // 导出对话框状态
  const showExportDialog = ref(false)
  const exportLoading = ref(false)

  // 使用 ref 而不是 reactive，以便更好地处理日期选择器
  const exportForm = ref({
    reportType: 'single', // single: 单个工作周, monthly: 月度, quarterly: 季度, yearly: 年度
    year: new Date().getFullYear().toString(), // 使用字符串类型
    month: new Date().getMonth() + 1,
    quarter: Math.floor(new Date().getMonth() / 3) + 1
  })

  // 打开导出对话框
  const exportWorkLog = () => {
    // 重置表单
    exportForm.value.reportType = 'single'

    // 从 week_start_date 中提取年份
    let defaultYear = new Date().getFullYear()
    if (workWeek.value?.week_start_date) {
      defaultYear = new Date(workWeek.value.week_start_date).getFullYear()
    }

    exportForm.value.year = defaultYear.toString()
    exportForm.value.month = new Date().getMonth() + 1
    exportForm.value.quarter = Math.floor(new Date().getMonth() / 3) + 1

    showExportDialog.value = true
  }

  // 确认导出
  const confirmExport = async () => {
    try {
      exportLoading.value = true
      console.log('📊 [WorkLogDetail] 开始导出报告:', exportForm.value)

      ElMessage.info('正在生成PDF报告，请稍候...')

      // 构建API URL
      let apiUrl = '/api/work-logs/export?'
      const params = new URLSearchParams()

      if (exportForm.value.reportType === 'single') {
        // 单个工作周
        params.append('week_id', workWeekId.value)
        params.append('report_type', 'single')
      } else if (exportForm.value.reportType === 'monthly') {
        // 月度报告
        params.append('report_type', 'monthly')
        params.append('year', exportForm.value.year)
        params.append('month', exportForm.value.month.toString())
      } else if (exportForm.value.reportType === 'quarterly') {
        // 季度报告
        params.append('report_type', 'quarterly')
        params.append('year', exportForm.value.year)
        params.append('quarter', exportForm.value.quarter.toString())
      } else if (exportForm.value.reportType === 'yearly') {
        // 年度报告
        params.append('report_type', 'yearly')
        params.append('year', exportForm.value.year)
      }

      apiUrl += params.toString()
      console.log('📡 [WorkLogDetail] API URL:', apiUrl)

      // 调用后端API导出PDF
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || '导出失败')
      }

      // 获取文件blob
      const blob = await response.blob()

      // 从响应头获取文件名
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = '工作日志统计报告.pdf'
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(
          /filename\*?=["']?(?:UTF-\d['"]*)?([^;\r\n"']*)["']?;?/
        )
        if (filenameMatch && filenameMatch[1]) {
          filename = decodeURIComponent(filenameMatch[1])
        }
      }

      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()

      // 清理
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('PDF报告导出成功')
      console.log('✅ [WorkLogDetail] PDF报告导出成功:', filename)

      // 关闭对话框
      showExportDialog.value = false
    } catch (error: any) {
      console.error('❌ [WorkLogDetail] 导出失败:', error)
      ElMessage.error(`导出失败: ${error.message || '未知错误'}`)
    } finally {
      exportLoading.value = false
    }
  }

  // 归档工作周
  const handleArchiveWeek = async () => {
    if (!workWeek.value) {
      ElMessage.warning('未找到工作周信息')
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要归档工作周 "${workWeek.value.title}" 吗？归档后可以在筛选中查看。`,
        '归档确认',
        {
          confirmButtonText: '确定归档',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      await workWeekApi.updateWorkWeek(workWeek.value.id, {
        status: 'archived'
      })

      ElMessage.success('归档成功')
      await refreshData()

      // 通知父组件刷新工作周列表
      emit('refresh')
      console.log('✅ [WorkLogDetail] 已通知父组件刷新工作周列表')
    } catch (error: any) {
      if (error !== 'cancel') {
        console.error('归档失败:', error)
        ElMessage.error('归档失败')
      }
    }
  }

  // 恢复归档
  const handleUnarchiveWeek = async () => {
    if (!workWeek.value) {
      ElMessage.warning('未找到工作周信息')
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要恢复工作周 "${workWeek.value.title}" 的归档状态吗？`,
        '恢复确认',
        {
          confirmButtonText: '确定恢复',
          cancelButtonText: '取消',
          type: 'info'
        }
      )

      await workWeekApi.updateWorkWeek(workWeek.value.id, {
        status: 'active'
      })

      ElMessage.success('恢复成功')
      await refreshData()

      // 通知父组件刷新工作周列表
      emit('refresh')
      console.log('✅ [WorkLogDetail] 已通知父组件刷新工作周列表')
    } catch (error: any) {
      if (error !== 'cancel') {
        console.error('恢复失败:', error)
        ElMessage.error('恢复失败')
      }
    }
  }

  // 工具函数
  const getWeekStatusText = (status: string) => {
    const statusMap = {
      active: '活跃',
      archived: '已归档',
      deleted: '已删除'
    }
    return statusMap[status as keyof typeof statusMap] || status
  }

  const getWeekStatusType = (status: string) => {
    const typeMap = {
      active: 'success',
      archived: 'info',
      deleted: 'danger'
    }
    return (typeMap[status as keyof typeof typeMap] || 'info') as
      | 'success'
      | 'info'
      | 'warning'
      | 'danger'
  }

  const formatDateRange = (startDate: string, endDate: string) => {
    const start = new Date(startDate)
    const end = new Date(endDate)
    return `${start.getFullYear()}年${start.getMonth() + 1}月${start.getDate()}日 到 ${end.getFullYear()}年${end.getMonth() + 1}月${end.getDate()}日`
  }

  // 监听 props.weekId 变化
  watch(
    () => props.weekId,
    (newWeekId) => {
      if (newWeekId) {
        workWeekId.value = newWeekId
        refreshData()
      }
    }
  )

  // 监听路由变化（用于独立页面模式）
  watch(
    () => route.params.weekId,
    (newWeekId) => {
      if (newWeekId && !props.weekId) {
        workWeekId.value = newWeekId as string
        refreshData()
      }
    }
  )

  // 监听管理覆盖员工对话框的打开
  watch(showManageCoveredUsers, (show) => {
    if (show) {
      // 初始化选中的用户ID列表
      selectedCoveredUserIds.value = [...coveredUserIds.value]
      // 如果还没加载用户列表，则加载
      if (allActiveUsers.value.length === 0) {
        loadActiveUsers()
      }
    }
  })

  // 生命周期
  onMounted(() => {
    console.log('🚀 [WorkLogDetail] 组件已挂载')
    console.log('  - props.weekId:', props.weekId)
    console.log('  - route.params.weekId:', route.params.weekId)
    console.log('  - workWeekId.value:', workWeekId.value)
    refreshData()
    // 预加载活跃用户列表（用于管理覆盖员工功能）
    if (userStore.hasPermission('WorkLogManagement')) {
      loadActiveUsers()
    }
  })

  // 已移除：seedCurrentUserWeek 和 generateAllUsersWeek
  // 工作周创建时应该自动初始化所有覆盖用户的空白条目
</script>

<style lang="scss" scoped>
  .work-log-week-detail {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;

    .overview-section {
      margin-bottom: 20px;

      .stat-card {
        .stat-content {
          display: flex;
          align-items: center;

          .stat-icon {
            width: 48px;
            height: 48px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 16px;

            .el-icon {
              font-size: 24px;
              color: white;
            }

            &.total {
              background: linear-gradient(45deg, #409eff, #1890ff);
            }

            &.submitted {
              background: linear-gradient(45deg, #67c23a, #52c41a);
            }

            &.hours {
              background: linear-gradient(45deg, #e6a23c, #fa8c16);
            }

            &.completion {
              background: linear-gradient(45deg, #f56c6c, #ff4d4f);
            }
          }

          .stat-info {
            .stat-value {
              font-size: 28px;
              font-weight: 700;
              color: var(--art-text-gray-900);
              line-height: 1;
              margin-bottom: 4px;
            }

            .stat-label {
              font-size: 14px;
              color: var(--art-text-gray-600);
            }
          }
        }
      }
    }

    .table-card {
      // 让卡片占满剩余空间
      flex: 1;
      min-height: 0;
      display: flex;
      flex-direction: column;
      background: var(--art-main-bg-color);

      :deep(.el-card__header) {
        padding: 18px 24px;
        border-bottom: 1px solid var(--art-card-border);
        background: var(--art-bg-color);
        flex-shrink: 0;
      }

      :deep(.el-card__body) {
        flex: 1;
        min-height: 0;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        padding: 0;
      }

      .table-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;

        .header-left {
          flex: 1;
          min-width: 0;

          .header-info {
            h3 {
              margin: 0 0 8px 0;
              color: var(--art-text-gray-900);
              font-size: 19px;
              font-weight: 600;
              line-height: 1.4;
              letter-spacing: 0.3px;
            }

            .date-info {
              color: var(--art-text-gray-600);
              font-size: 14px;
              display: flex;
              align-items: center;
              flex-wrap: wrap;
              gap: 8px;

              :deep(.el-tag) {
                border-radius: 6px;
                padding: 0 10px;
                height: 24px;
                line-height: 24px;
              }
            }
          }
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 10px;
          flex-shrink: 0;

          :deep(.el-button) {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;

            &:hover {
              transform: translateY(-1px);
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
          }
        }
      }

      .table-layout {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }

      .table-container {
        flex: 1;
        overflow: auto;
        min-height: 600px; // 确保表格区域有足够的高度
        display: flex;
        flex-direction: column;

        .empty-guidance {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 400px;

          .tips {
            margin-bottom: 16px;
            color: var(--art-text-gray-600);
            font-size: 14px;
          }
        }

        .work-log-table {
          height: 100%; // 让表格占满容器

          // 表头样式
          :deep(.el-table__header-wrapper) {
            .el-table__header {
              th {
                background: var(--art-bg-color) !important;
                color: var(--art-text-gray-800) !important;
              }
            }
          }

          .user-info {
            .user-name {
              font-weight: 600;
              color: var(--art-text-gray-900);
              margin-bottom: 2px;
            }

            .user-meta {
              font-size: 12px;
              color: var(--art-text-gray-600);
            }
          }

          .work-day-cell {
            padding: 8px;
            min-height: 120px;
          }

          .week-summary {
            .summary-item {
              display: flex;
              justify-content: space-between;
              margin-bottom: 4px;
              font-size: 12px;

              .label {
                color: var(--art-text-gray-600);
              }

              .value {
                font-weight: 500;
                color: var(--art-text-gray-800);
              }
            }
          }
        }
      }
    }
  }

  // 管理覆盖员工对话框样式
  .manage-covered-users {
    .user-selector-custom {
      display: flex;
      gap: 20px;
      align-items: stretch;

      .left-panel,
      .right-panel {
        flex: 1;
        border: 1px solid var(--art-card-border);
        border-radius: 12px;
        background: var(--art-main-bg-color);
        display: flex;
        flex-direction: column;
        min-width: 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

        .panel-header {
          background: var(--art-bg-color);
          border-bottom: 2px solid var(--art-card-border);
          padding: 14px 18px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-radius: 12px 12px 0 0;

          .panel-title {
            font-weight: 600;
            color: var(--art-text-gray-900);
            font-size: 15px;
            letter-spacing: 0.3px;
          }

          .panel-count {
            color: var(--art-text-gray-700);
            font-size: 12px;
            background: var(--art-gray-300);
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 600;
          }
        }

        .panel-search {
          padding: 14px;
          background: var(--art-bg-color);
          border-bottom: 1px solid var(--art-border-dashed-color);
        }

        .panel-body {
          flex: 1;
          overflow: hidden;
          padding: 4px 0;

          // 空状态样式
          .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            padding: 60px 20px;

            .empty-icon {
              font-size: 64px;
              color: var(--art-gray-400);
              margin-bottom: 16px;
            }

            .empty-text {
              color: var(--art-text-gray-500);
              font-size: 14px;
              margin: 0;
            }
          }

          // 左侧：部门分组样式
          :deep(.el-collapse) {
            border: none;

            .el-collapse-item {
              border-bottom: 1px solid var(--art-card-border);

              &:last-child {
                border-bottom: none;
              }

              .el-collapse-item__header {
                padding: 0 18px;
                height: 48px;
                background: transparent;
                border: none;
                font-size: 14px;
                transition: all 0.3s;

                &:hover {
                  background: var(--art-bg-color);
                }

                &.is-active {
                  background: rgba(var(--art-primary-rgb), 0.08);
                  color: var(--art-primary-color);
                }

                .el-collapse-item__arrow {
                  color: var(--art-text-gray-500);
                  transition: transform 0.3s;

                  &.is-active {
                    color: var(--art-primary-color);
                  }
                }
              }

              .el-collapse-item__wrap {
                border: none;
                background: var(--art-bg-color);
              }

              .el-collapse-item__content {
                padding: 0;
              }
            }
          }

          .dept-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            width: 100%;

            .dept-name {
              font-weight: 600;
              color: var(--art-text-gray-900);
            }

            .dept-count {
              color: var(--art-text-gray-500);
              font-size: 12px;
              font-weight: 500;
            }
          }

          .dept-users {
            padding: 12px 0;
            display: flex;
            flex-direction: column;
            gap: 2px;

            .user-checkbox {
              margin-left: 0 !important;
              padding: 10px 24px;
              width: 100%;
              border-radius: 6px;
              transition: all 0.2s;

              :deep(.el-checkbox__input) {
                .el-checkbox__inner {
                  border-radius: 4px;
                  border-width: 2px;
                  width: 16px;
                  height: 16px;

                  &:hover {
                    border-color: var(--art-primary-color);
                  }
                }

                &.is-checked {
                  .el-checkbox__inner {
                    background-color: var(--art-primary-color);
                    border-color: var(--art-primary-color);
                  }
                }
              }

              :deep(.el-checkbox__label) {
                font-size: 14px;
                color: var(--art-text-gray-700);
                padding-left: 10px;
                transition: color 0.2s;
              }

              &:hover {
                background: var(--art-bg-color);

                :deep(.el-checkbox__label) {
                  color: var(--art-text-gray-900);
                }
              }
            }
          }

          // 右侧：已选择用户列表样式
          .selected-users-list {
            display: flex;
            flex-direction: column;
            padding: 12px;
            gap: 10px;

            .selected-user-item {
              display: flex;
              align-items: center;
              justify-content: space-between;
              padding: 12px 14px;
              background: var(--art-main-bg-color);
              border: 1px solid var(--art-card-border);
              border-radius: 10px;
              transition: all 0.3s ease;
              position: relative;
              overflow: hidden;

              &::before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 3px;
                background: var(--art-primary-color);
                opacity: 0;
                transition: opacity 0.3s;
              }

              &:hover {
                transform: translateX(2px);
                box-shadow: 0 4px 12px rgba(var(--art-primary-rgb), 0.15);
                border-color: var(--art-primary-color);

                &::before {
                  opacity: 1;
                }

                .remove-btn {
                  opacity: 1;
                  transform: scale(1);
                }
              }

              .user-info-wrapper {
                display: flex;
                align-items: center;
                gap: 12px;
                flex: 1;
                min-width: 0;

                .user-avatar {
                  width: 36px;
                  height: 36px;
                  border-radius: 50%;
                  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
                  color: white;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  font-weight: 600;
                  font-size: 14px;
                  flex-shrink: 0;
                  box-shadow: 0 2px 8px rgba(6, 182, 212, 0.25);
                }

                .user-details {
                  display: flex;
                  flex-direction: column;
                  gap: 4px;
                  flex: 1;
                  min-width: 0;

                  .user-name {
                    font-size: 14px;
                    font-weight: 600;
                    color: var(--art-text-gray-900);
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                  }

                  .user-dept {
                    font-size: 12px;
                    color: var(--art-text-gray-500);
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                  }
                }
              }

              .remove-btn {
                opacity: 0;
                transform: scale(0.8);
                transition: all 0.3s ease;
                flex-shrink: 0;

                :deep(.el-icon) {
                  font-size: 16px;
                }
              }
            }
          }
        }
      }
    }
  }

  // 全局表格样式调整
  :deep(.el-table) {
    .el-table__cell {
      padding: 8px 0;
    }

    .el-table__header-wrapper {
      .el-table__header {
        th {
          font-weight: 600;
          font-size: 13px;
          text-align: center;
        }
      }
    }
  }

  // ========================================
  // 夜间模式额外适配
  // ========================================
  html.dark {
    .work-log-week-detail {
      // 确保对话框在夜间模式下的阴影更明显
      .manage-covered-users {
        .left-panel,
        .right-panel {
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
        }
      }
    }
  }
</style>
