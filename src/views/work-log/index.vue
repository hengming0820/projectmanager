<template>
  <div class="work-log-page">
    <!-- 顶部标题栏 -->
    <ArtPageHeader
      title="工作日志管理"
      description="管理团队工作日志，查看工作进度"
      icon="📋"
      badge="Work Log"
      theme="cyan"
    >
      <template #actions>
        <el-button @click="jumpToCurrentWeek" type="info" title="跳转到当前工作周">
          <el-icon><Calendar /></el-icon>
          当前周：{{ currentWeekISO }}
        </el-button>
        <el-button @click="openExternalLink" type="success" title="打开外部工具">
          <el-icon><Link /></el-icon>
          外部工具
        </el-button>
        <el-button v-if="canManageWorkLog" @click="showBatchManageDialog = true">
          <el-icon><Setting /></el-icon>
          批量管理
        </el-button>
        <el-button v-if="canManageWorkLog" type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建工作周
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </template>
    </ArtPageHeader>

    <el-container class="page-container">
      <el-container class="page-body">
        <!-- 左侧导航栏 -->
        <el-aside class="sidebar" v-if="navReady">
          <div class="nav-panel">
            <!-- 筛选器 -->
            <div class="filter-section">
              <el-input
                v-model="filterSearch"
                placeholder="搜索工作周..."
                clearable
                size="small"
                :prefix-icon="Search"
              />

              <!-- 显示已归档工作周的开关 -->
              <div class="archived-toggle">
                <el-switch
                  v-model="showArchivedWeeks"
                  size="small"
                  active-text="显示已归档"
                  inactive-text="隐藏已归档"
                  @change="onArchivedToggleChange"
                />
              </div>
            </div>

            <!-- 工作周树 -->
            <el-tree
              ref="treeRef"
              :data="treeData"
              node-key="key"
              :highlight-current="true"
              :current-node-key="currentWeekId"
              :expand-on-click-node="false"
              :default-expanded-keys="expandedKeys"
              :filter-node-method="filterNode"
              :indent="4"
              :props="{ label: 'label', children: 'children' }"
              @node-click="onNodeClick"
            >
              <template #default="{ node, data }">
                <div :class="['tree-node', data.isLeaf ? 'tree-leaf' : 'tree-group']">
                  <!-- 工作周叶子节点 -->
                  <template v-if="data.isLeaf">
                    <el-tooltip
                      placement="right"
                      :content="`${data.dateRange} · ${data.statusText}`"
                    >
                      <span class="node-label" :class="{ 'is-current-week': data.isCurrentWeek }">
                        {{ data.label }}
                      </span>
                    </el-tooltip>
                  </template>
                  <!-- 工作组节点（第一级） -->
                  <template v-else-if="data.isWorkGroup">
                    <i class="iconfont" style="margin-right: 6px">&#xe761;</i>
                    <span class="node-label">{{ data.label }}</span>
                  </template>
                  <!-- 月份分组节点（第二级） -->
                  <template v-else-if="data.isGroup">
                    <i class="iconfont" style="margin-right: 6px">&#xe623;</i>
                    <span class="node-label">{{ data.label }}</span>
                  </template>
                  <!-- 其他分组节点 -->
                  <template v-else>
                    <span class="node-label">{{ data.label }}</span>
                  </template>
                </div>
              </template>
            </el-tree>
          </div>
        </el-aside>

        <!-- 右侧主内容区 - 嵌入工作周详情 -->
        <el-main class="main-col">
          <div v-if="currentWeekId && currentWorkWeek" class="week-detail-wrapper">
            <!-- 直接嵌入工作周详情组件，不使用路由 -->
            <WorkLogWeekDetail
              :key="currentWeekId"
              :week-id="currentWeekId"
              @refresh="loadWorkWeeks"
            />
          </div>
          <el-empty v-else description="请从左侧选择一个工作周查看详情" :image-size="200">
            <el-button type="primary" @click="showCreateDialog = true" v-if="canManageWorkLog">
              创建第一个工作周
            </el-button>
          </el-empty>
        </el-main>
      </el-container>
    </el-container>

    <!-- 批量管理对话框 -->
    <el-dialog
      v-model="showBatchManageDialog"
      title="批量管理工作周"
      width="800px"
      :close-on-click-modal="false"
      append-to-body
      destroy-on-close
    >
      <div class="batch-manage-container">
        <el-alert type="info" :closable="false" style="margin-bottom: 20px">
          <template #title>
            <span style="font-weight: 600">批量操作说明</span>
          </template>
          <div style="font-size: 13px; line-height: 1.6">
            • 选择需要删除的工作周，点击"批量删除"按钮<br />
            • 删除工作周会同时删除其下所有日志条目，此操作不可恢复<br />
            • 已选中
            <span style="color: var(--art-primary-color); font-weight: 600">{{
              selectedWeekIds.length
            }}</span>
            个工作周
          </div>
        </el-alert>

        <!-- 筛选和搜索 -->
        <div
          class="batch-filters"
          style="
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
          "
        >
          <div style="display: flex; gap: 12px">
            <el-input
              v-model="batchSearchText"
              placeholder="搜索工作周标题..."
              clearable
              style="width: 300px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="batchStatusFilter"
              placeholder="筛选状态"
              clearable
              style="width: 150px"
            >
              <el-option label="全部" value="" />
              <el-option label="进行中" value="active" />
              <el-option label="已归档" value="archived" />
              <el-option label="草稿" value="draft" />
            </el-select>
          </div>
          <el-button
            type="warning"
            plain
            :disabled="selectedWeekIds.length === 0"
            @click="handleBatchArchive"
          >
            <el-icon><Finished /></el-icon>
            归档选中项
          </el-button>
        </div>

        <!-- 工作周列表 -->
        <div class="batch-week-list">
          <el-checkbox
            v-model="selectAllWeeks"
            @change="handleSelectAll"
            style="margin-bottom: 12px; font-weight: 500"
          >
            全选 ({{ filteredWeeksForBatch.length }})
          </el-checkbox>

          <el-scrollbar max-height="450px">
            <el-checkbox-group v-model="selectedWeekIds">
              <div v-for="group in groupedWeeksForBatch" :key="group.label" class="batch-group">
                <div class="batch-group-header">
                  {{ group.label }}
                </div>
                <div v-for="week in group.weeks" :key="week.id" class="batch-week-item">
                  <el-checkbox :label="week.id">
                    <div class="week-item-compact">
                      <span class="week-title">{{ week.title }}</span>
                      <div class="week-info">
                        <el-tag :type="getStatusType(week.status)" size="small" effect="plain">
                          {{ getStatusText(week.status) }}
                        </el-tag>
                        <span class="week-date">{{
                          formatCompactDate(week.week_start_date, week.week_end_date)
                        }}</span>
                        <span class="week-entries">{{ week.total_entries || 0 }} 条</span>
                      </div>
                    </div>
                  </el-checkbox>
                </div>
              </div>
            </el-checkbox-group>
          </el-scrollbar>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer" style="display: flex; justify-content: space-between">
          <el-button @click="showBatchManageDialog = false">取消</el-button>
          <div style="display: flex; gap: 12px">
            <el-button
              type="warning"
              @click="handleBatchArchive"
              :disabled="selectedWeekIds.length === 0"
              :loading="batchArchiving"
            >
              <el-icon><Finished /></el-icon>
              批量归档 ({{ selectedWeekIds.length }})
            </el-button>
            <el-button
              type="danger"
              @click="handleBatchDelete"
              :disabled="selectedWeekIds.length === 0"
              :loading="batchDeleting"
            >
              <el-icon><Delete /></el-icon>
              批量删除 ({{ selectedWeekIds.length }})
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑工作周对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑工作周"
      width="680px"
      :close-on-click-modal="false"
      :modal="true"
      append-to-body
    >
      <el-form :model="editForm" label-width="110px">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" placeholder="工作周标题" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始日期">
              <el-date-picker
                v-model="editForm.startDate"
                type="date"
                format="YYYY-MM-DD"
                placeholder="选择起始日期"
                style="width: 100%"
                :disabled-date="disabledDate"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期">
              <el-date-picker
                v-model="editForm.endDate"
                type="date"
                format="YYYY-MM-DD"
                placeholder="选择结束日期"
                style="width: 100%"
                :disabled-date="disabledDate"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="周序号">
              <el-input-number v-model="editForm.weekNumber" :min="1" :max="53" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="editForm.status" style="width: 100%">
                <el-option label="进行中" value="active" />
                <el-option label="已归档" value="archived" />
                <el-option label="草稿" value="draft" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="工作周描述（可选）"
          />
        </el-form-item>

        <el-form-item label="按部门选择">
          <el-select
            v-model="editSelectedDepartments"
            multiple
            filterable
            collapse-tags
            placeholder="选择部门快速添加人员"
            style="width: 100%"
            @change="handleEditDepartmentSelect"
          >
            <el-option
              v-for="dept in editDepartmentOptions"
              :key="dept"
              :label="dept"
              :value="dept"
            >
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span>{{ dept }}</span>
                <el-tag size="small" type="info">{{ getEditDepartmentUserCount(dept) }}人</el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="覆盖员工">
          <el-select
            v-model="editForm.coveredUserIds"
            multiple
            filterable
            placeholder="选择覆盖员工"
            style="width: 100%"
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option-group
              v-for="dept in editUsersByDepartment"
              :key="dept.department"
              :label="dept.department"
            >
              <el-option
                v-for="user in dept.users"
                :key="user.id"
                :label="user.real_name || user.username"
                :value="user.id"
              >
                <span>{{ user.real_name || user.username }}</span>
                <span style="color: #8492a6; font-size: 13px; margin-left: 8px">
                  {{ user.department || '-' }}
                </span>
              </el-option>
            </el-option-group>
          </el-select>
          <div style="margin-top: 8px; font-size: 12px; color: #909399">
            已选择 {{ editForm.coveredUserIds.length }} 人
            <el-button
              v-if="editForm.coveredUserIds.length > 0"
              text
              type="primary"
              size="small"
              @click="editForm.coveredUserIds = []"
              style="margin-left: 8px"
            >
              清空
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpdate" :loading="updating"> 保存 </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 创建工作周对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建工作周"
      width="680px"
      :close-on-click-modal="false"
      :modal="true"
      append-to-body
    >
      <el-form :model="createForm" label-width="110px">
        <el-form-item label="创建模式">
          <el-radio-group v-model="createForm.batchMode" @change="handleBatchModeChange">
            <el-radio :label="false">单个工作周</el-radio>
            <el-radio :label="true">批量创建</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="createForm.batchMode" label="批量数量">
          <el-input-number
            v-model="createForm.batchCount"
            :min="2"
            :max="12"
            @change="handleBatchCountChange"
          />
          <span style="margin-left: 10px; color: #909399; font-size: 13px">
            将创建连续的 {{ createForm.batchCount }} 个工作周
          </span>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="起始年份">
              <el-input-number
                v-model="createForm.year"
                :min="2020"
                :max="2030"
                style="width: 100%"
                @change="handleYearChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="起始周序号">
              <div style="display: flex; align-items: center">
                <el-input-number
                  v-model="createForm.weekNumber"
                  :min="1"
                  :max="53"
                  style="width: 120px"
                  @change="handleWeekNumberChange"
                />
                <span style="margin-left: 8px; color: #909399; font-size: 12px; white-space: nowrap">ISO (1-53)</span>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="工作组">
          <el-select
            v-model="createForm.groupName"
            placeholder="选择或输入工作组名称"
            filterable
            allow-create
            default-first-option
            style="width: 100%"
            @change="handleGroupNameChange"
          >
            <el-option
              v-for="group in PRESET_WORK_GROUPS"
              :key="group.value"
              :label="group.label"
              :value="group.value"
            >
              <div style="display: flex; align-items: center; gap: 8px">
                <i
                  class="iconfont"
                  :style="{ color: group.color, fontSize: '16px' }"
                  v-html="group.icon"
                ></i>
                <span>{{ group.label }}</span>
              </div>
            </el-option>
          </el-select>
          <div style="margin-top: 6px; color: #909399; font-size: 12px">
            可选择预设工作组或输入自定义名称
          </div>
        </el-form-item>

        <el-form-item label="标题预览">
          <el-input v-model="createForm.title" readonly>
            <template #suffix>
              <el-button text type="primary" size="small" @click="generateTitle">
                重新生成
              </el-button>
            </template>
          </el-input>
          <div v-if="createForm.batchMode" style="margin-top: 8px; color: #909399; font-size: 12px">
            将依次创建：{{ generateBatchTitlePreview() }}
          </div>
        </el-form-item>

        <el-form-item label="起始日期">
          <el-date-picker
            v-model="createForm.startDate"
            type="week"
            format="[第] ww [周] YYYY-MM-DD"
            placeholder="选择周"
            style="width: 100%"
            :disabled-date="disabledDate"
            @change="handleStartDateChange"
          />
        </el-form-item>

        <el-form-item label="按部门选择">
          <el-select
            v-model="selectedDepartments"
            multiple
            filterable
            collapse-tags
            placeholder="选择部门快速添加人员"
            style="width: 100%; margin-bottom: 12px"
            @change="handleDepartmentSelect"
          >
            <el-option v-for="dept in departmentOptions" :key="dept" :label="dept" :value="dept">
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span>{{ dept }}</span>
                <el-tag size="small" type="info">{{ getDepartmentUserCount(dept) }}人</el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="覆盖人员">
          <el-select
            v-model="createForm.coveredUserIds"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            placeholder="选择人员"
            style="width: 100%"
          >
            <el-option-group
              v-for="dept in usersByDepartment"
              :key="dept.department"
              :label="dept.department"
            >
              <el-option
                v-for="user in dept.users"
                :key="user.value"
                :label="user.label"
                :value="user.value"
              >
                <span>{{ user.realName }}</span>
                <span style="color: #8492a6; font-size: 13px; margin-left: 8px">
                  {{ user.department }}
                </span>
              </el-option>
            </el-option-group>
          </el-select>
          <div style="margin-top: 8px; font-size: 12px; color: #909399">
            已选择 {{ createForm.coveredUserIds.length }} 人
            <el-button
              v-if="createForm.coveredUserIds.length > 0"
              text
              type="primary"
              size="small"
              @click="createForm.coveredUserIds = []"
              style="margin-left: 8px"
            >
              清空
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          {{ createForm.batchMode ? `批量创建 ${createForm.batchCount} 个工作周` : '创建工作周' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, watch, nextTick } from 'vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    Plus,
    Refresh,
    Search,
    MoreFilled,
    Edit,
    Delete,
    Setting,
    Finished,
    Link,
    Calendar
  } from '@element-plus/icons-vue'
  import { useUserStore } from '@/store/modules/user'
  import { workWeekApi } from '@/api/workLogApi'
  import { userApi } from '@/api/userApi'
  import type { WorkWeek } from '@/types/work-log'
  import WorkLogWeekDetail from './week-detail.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'

  const userStore = useUserStore()
  const canManageWorkLog = computed(() =>
    ['admin', 'reviewer', 'annotator', 'algorithm', 'development', 'executive'].includes(
      userStore.currentUser?.role || ''
    )
  )

  // 当前选中的工作周
  const currentWeekId = ref<string>('')
  const currentWorkWeek = ref<WorkWeek | null>(null)

  // 导航栏数据
  const navReady = ref(false)
  const treeData = ref<any[]>([])
  const expandedKeys = ref<string[]>([])
  const treeRef = ref()
  const filterSearch = ref('')
  const showArchivedWeeks = ref(false) // 是否显示已归档的工作周

  // 工作周列表数据
  const workWeeks = ref<WorkWeek[]>([])

  // 创建对话框
  const showCreateDialog = ref(false)
  const creating = ref(false)
  const createForm = ref({
    batchMode: false,
    batchCount: 4,
    year: new Date().getFullYear(),
    weekNumber: 1,
    groupName: '标注组',
    title: '',
    startDate: undefined as Date | undefined,
    coveredUserIds: [] as string[]
  })
  const userOptions = ref<
    Array<{ label: string; value: string; realName: string; department: string }>
  >([])
  const selectedDepartments = ref<string[]>([])

  // 编辑对话框
  const showEditDialog = ref(false)
  const updating = ref(false)
  const editingWeek = ref<WorkWeek | null>(null)
  const editForm = ref({
    title: '',
    startDate: undefined as Date | undefined,
    endDate: undefined as Date | undefined,
    weekNumber: 1,
    status: 'active' as 'active' | 'archived' | 'draft',
    description: '',
    coveredUserIds: [] as string[]
  })

  // 活跃用户列表
  const activeUsers = ref<any[]>([])
  const editSelectedDepartments = ref<string[]>([])

  // 批量管理对话框
  const showBatchManageDialog = ref(false)
  const batchDeleting = ref(false)
  const batchArchiving = ref(false)
  const selectedWeekIds = ref<string[]>([])
  const selectAllWeeks = ref(false)
  const batchSearchText = ref('')
  const batchStatusFilter = ref('')
  // 加载工作周列表
  const loadWorkWeeks = async () => {
    try {
      const response = await workWeekApi.getWorkWeeks({ page: 1, pageSize: 100 })
      console.log('📦 [WorkLog] 工作周API响应:', response)
      // backendApi 返回的是完整响应对象 { code, msg, data: { list, total } }
      const data = (response as any).data || response
      workWeeks.value = data.list || []
      console.log('✅ [WorkLog] 加载了', workWeeks.value.length, '个工作周')
      buildTree()
    } catch (error) {
      console.error('❌ [WorkLog] 加载工作周列表失败:', error)
      ElMessage.error('加载工作周列表失败')
    }
  }

  // 预设工作组列表
  const PRESET_WORK_GROUPS = [
    { value: '标注组', label: '标注组', icon: '&#xe70f;', color: '#667eea' },
    { value: '算法组', label: '算法组', icon: '&#xe6b8;', color: '#f59e0b' },
    { value: '开发组', label: '开发组', icon: '&#xe666;', color: '#10b981' },
    { value: '行政组', label: '行政组', icon: '&#xe634;', color: '#ec4899' }
  ]

  // 从标题中提取工作组名称
  const extractGroupName = (title: string): string => {
    // 匹配格式：2025W50标注组工作计划 -> 标注组
    const match = title.match(/\d{4}W\d{2}(.+?)工作计划/)
    return match ? match[1] : '其他'
  }

  // 获取指定工作组的最新周序号
  const getGroupLatestWeekNumber = (groupName: string): { year: number; weekNumber: number } => {
    // 过滤出该工作组的所有工作周
    const groupWeeks = workWeeks.value
      .filter((w) => extractGroupName(w.title) === groupName)
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

    if (groupWeeks.length > 0) {
      const latestWeek = groupWeeks[0]
      const match = latestWeek.title.match(/(\d{4})W(\d{2})(.+?)工作计划/)
      if (match) {
        const year = parseInt(match[1])
        const weekNum = parseInt(match[2])

        // 返回下一周
        return {
          year: weekNum >= 52 ? year + 1 : year,
          weekNumber: weekNum >= 52 ? 1 : weekNum + 1
        }
      }
    }

    // 如果该工作组没有历史记录，返回当前日期的周信息
    const now = new Date()
    return {
      year: now.getFullYear(),
      weekNumber: getWeekNumber(now)
    }
  }

  // 构建树形数据结构（三层：工作组 > 年月 > 工作周）
  const buildTree = () => {
    // 按创建时间倒序排序
    let sortedWeeks = [...workWeeks.value].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )

    // 如果不显示已归档的工作周，则过滤掉它们
    if (!showArchivedWeeks.value) {
      sortedWeeks = sortedWeeks.filter((week) => week.status !== 'archived')
    }

    // 第一层：按工作组分组
    const workGroups: Record<string, any[]> = {}

    sortedWeeks.forEach((week) => {
      const groupName = extractGroupName(week.title)

      if (!workGroups[groupName]) {
        workGroups[groupName] = []
      }

      workGroups[groupName].push(week)
    })

    // 构建三层树结构
    const groupNames = Object.keys(workGroups).sort()
    treeData.value = groupNames.map((groupName) => {
      const groupWeeks = workGroups[groupName]

      // 第二层：按年月分组
      const monthGroups: Record<string, any[]> = {}

      groupWeeks.forEach((week) => {
        const date = new Date(week.week_start_date)
        const year = date.getFullYear()
        const month = date.getMonth() + 1
        const yearMonth = `${year}年${String(month).padStart(2, '0')}月`

        if (!monthGroups[yearMonth]) {
          monthGroups[yearMonth] = []
        }

        monthGroups[yearMonth].push({
          key: week.id,
          label: week.title,
          isLeaf: true,
          dateRange: `${week.week_start_date} ~ ${week.week_end_date}`,
          statusText: getWeekStatusText(week.status),
          isCurrentWeek: isCurrentWeek(week),
          week: week
        })
      })

      // 构建月份子节点
      const months = Object.keys(monthGroups).sort((a, b) => b.localeCompare(a))
      const monthNodes = months.map((yearMonth) => ({
        key: `${groupName}-${yearMonth}`,
        label: yearMonth,
        isGroup: true,
        children: monthGroups[yearMonth]
      }))

      return {
        key: `group-${groupName}`,
        label: `${groupName}工作计划`,
        isWorkGroup: true,
        children: monthNodes
      }
    })

    // 智能选择工作周：优先选择当前用户所在工作组的当前日期所在工作周
    if (!currentWeekId.value && sortedWeeks.length > 0) {
      let targetWeek: WorkWeek | null = null

      // 1. 尝试找到当前用户所在工作组的当前日期所在工作周
      const currentUserDept = userStore.currentUser?.department
      if (currentUserDept) {
        // 从部门中提取工作组名称（例如：研发部算法组 -> 算法组）
        const deptGroupMatch = currentUserDept.match(/([^部]+组)/)
        const userWorkGroup = deptGroupMatch ? deptGroupMatch[1] : null

        if (userWorkGroup) {
          console.log('🔍 [WorkLog] 当前用户部门:', currentUserDept, '=> 工作组:', userWorkGroup)

          // 获取当前日期（考虑时区）
          const now = new Date()
          const currentDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())

          // 在该工作组中找到包含当前日期的工作周
          const userGroupWeeks = sortedWeeks.filter((week) => {
            const groupName = extractGroupName(week.title)
            return groupName === userWorkGroup
          })

          targetWeek =
            userGroupWeeks.find((week) => {
              const startDate = new Date(week.week_start_date)
              const endDate = new Date(week.week_end_date)
              return currentDate >= startDate && currentDate <= endDate
            }) || null

          if (targetWeek) {
            console.log('✅ [WorkLog] 找到当前日期所在工作周:', targetWeek.title)
          } else {
            // 如果没有找到包含当前日期的工作周，选择该工作组最新的工作周
            targetWeek = userGroupWeeks[0] || null
            if (targetWeek) {
              console.log(
                '⚠️ [WorkLog] 未找到当前日期所在工作周，选择该工作组最新工作周:',
                targetWeek.title
              )
            }
          }
        }
      }

      // 2. 如果没有找到目标工作周，回退到选择第一个工作周
      if (!targetWeek) {
        targetWeek = sortedWeeks[0]
        console.log('📌 [WorkLog] 选择默认第一个工作周:', targetWeek.title)
      }

      currentWeekId.value = targetWeek.id
      currentWorkWeek.value = targetWeek
    }

    // 默认展开目标工作周所在的工作组和月份
    if (expandedKeys.value.length === 0 && treeData.value.length > 0 && currentWorkWeek.value) {
      const targetGroupName = extractGroupName(currentWorkWeek.value.title)
      const targetGroup = treeData.value.find((g) => g.label.includes(targetGroupName))

      if (targetGroup) {
        expandedKeys.value.push(targetGroup.key)

        // 找到包含目标工作周的月份
        if (targetGroup.children && targetGroup.children.length > 0) {
          const targetDate = new Date(currentWorkWeek.value.week_start_date)
          const targetYearMonth = `${targetDate.getFullYear()}年${String(targetDate.getMonth() + 1).padStart(2, '0')}月`

          const targetMonth = targetGroup.children.find((m: any) => m.label === targetYearMonth)
          if (targetMonth) {
            expandedKeys.value.push(targetMonth.key)
          }

          // 同时展开前后一个月（如果存在）
          const monthIndex = targetGroup.children.findIndex((m: any) => m.label === targetYearMonth)
          if (monthIndex > 0) {
            expandedKeys.value.push(targetGroup.children[monthIndex - 1].key)
          }
          if (monthIndex < targetGroup.children.length - 1) {
            expandedKeys.value.push(targetGroup.children[monthIndex + 1].key)
          }
        }
      }
    } else if (expandedKeys.value.length === 0 && treeData.value.length > 0) {
      // 如果没有选中工作周，展开第一个工作组的前2个月
      const firstGroup = treeData.value[0]
      expandedKeys.value.push(firstGroup.key)

      if (firstGroup.children && firstGroup.children.length > 0) {
        const firstTwoMonths = firstGroup.children.slice(0, 2).map((m: any) => m.key)
        expandedKeys.value.push(...firstTwoMonths)
      }
    }

    navReady.value = true
  }

  // 树节点点击（支持点击展开）
  const onNodeClick = (node: any) => {
    // 如果是叶子节点（工作周），直接选中
    if (node.isLeaf) {
      if (node.key !== currentWeekId.value) {
        currentWeekId.value = node.key
        currentWorkWeek.value = node.week
      }
      return
    }

    // 如果是分组节点（工作组或月份），切换展开/收起
    if (node.isWorkGroup || node.isGroup) {
      const treeInstance = treeRef.value
      if (!treeInstance) return

      const treeNode = treeInstance.getNode(node.key)
      if (!treeNode) return

      if (treeNode.expanded) {
        // 已展开，收起
        treeInstance.store.nodesMap[node.key].expanded = false
        const idx = expandedKeys.value.indexOf(node.key)
        if (idx >= 0) {
          expandedKeys.value.splice(idx, 1)
        }
      } else {
        // 未展开，展开
        treeInstance.store.nodesMap[node.key].expanded = true
        if (!expandedKeys.value.includes(node.key)) {
          expandedKeys.value.push(node.key)
        }

        // 如果是工作组节点，自动展开第一个月份
        if (node.isWorkGroup && node.children && node.children.length > 0) {
          nextTick(() => {
            const firstMonth = node.children[0]
            if (firstMonth && !expandedKeys.value.includes(firstMonth.key)) {
              expandedKeys.value.push(firstMonth.key)
              treeInstance.store.nodesMap[firstMonth.key].expanded = true
            }
          })
        }
      }
    }
  }

  // 树节点过滤
  const filterNode = (value: string, data: any) => {
    if (!value) return true
    return data.label.toLowerCase().includes(value.toLowerCase())
  }

  // 监听搜索框变化
  watch(filterSearch, (val) => {
    treeRef.value?.filter(val)
  })

  // 切换显示已归档工作周
  const onArchivedToggleChange = (value: string | number | boolean) => {
    // 类型守卫：确保是布尔值
    if (typeof value !== 'boolean') {
      console.warn('⚠️ [WorkLog] 无效的切换值类型:', value)
      return
    }

    console.log('🔄 [WorkLog] 切换显示已归档工作周:', value)
    buildTree()

    // 如果关闭显示已归档，且当前选中的工作周是已归档状态，则清空选择
    if (!value && currentWorkWeek.value?.status === 'archived') {
      console.log('⚠️ [WorkLog] 当前选中的工作周是已归档状态，清空选择')
      currentWeekId.value = ''
      currentWorkWeek.value = null

      // 尝试选中第一个非归档的工作周
      const activeWeeks = workWeeks.value.filter((w) => w.status !== 'archived')
      if (activeWeeks.length > 0) {
        const firstActiveWeek = activeWeeks[0]
        currentWeekId.value = firstActiveWeek.id
        currentWorkWeek.value = firstActiveWeek
        console.log('✅ [WorkLog] 已自动选中第一个活跃工作周:', firstActiveWeek.title)
      }
    }
  }

  // 获取状态文本
  const getWeekStatusText = (status: string) => {
    const map: Record<string, string> = {
      active: '活跃',
      archived: '已归档',
      draft: '草稿'
    }
    return map[status] || status
  }

  // 加载用户列表
  const loadUsers = async () => {
    try {
      const res: any = await userApi.getUsersBasic({ status: 'active', size: 9999 })
      const list: any[] = res?.list || res?.data?.list || res?.data || []
      userOptions.value = list.map((u: any) => ({
        label: `${u.real_name || u.username} (${u.department || '未知部门'})`,
        value: u.id,
        realName: u.real_name || u.username,
        department: u.department || '未知部门'
      }))
    } catch (e) {
      console.error('加载用户列表失败:', e)
    }
  }

  // 按部门分组的用户列表
  const usersByDepartment = computed(() => {
    const grouped: Record<string, any[]> = {}
    userOptions.value.forEach((user) => {
      if (!grouped[user.department]) {
        grouped[user.department] = []
      }
      grouped[user.department].push(user)
    })
    return Object.entries(grouped).map(([department, users]) => ({
      department,
      users
    }))
  })

  // 部门选项列表
  const departmentOptions = computed(() => {
    const depts = new Set<string>()
    userOptions.value.forEach((user) => {
      if (user.department) {
        depts.add(user.department)
      }
    })
    return Array.from(depts).sort()
  })

  // 获取部门人数
  const getDepartmentUserCount = (dept: string): number => {
    return userOptions.value.filter((u) => u.department === dept).length
  }

  // 处理部门选择
  const handleDepartmentSelect = (departments: string[]) => {
    // 获取所有选中部门的用户ID
    const userIds = new Set(createForm.value.coveredUserIds)

    departments.forEach((dept) => {
      const deptUsers = userOptions.value.filter((u) => u.department === dept)
      deptUsers.forEach((u) => userIds.add(u.value))
    })

    createForm.value.coveredUserIds = Array.from(userIds)
  }

  // 编辑对话框 - 按部门分组的用户列表
  const editUsersByDepartment = computed(() => {
    const grouped: Record<string, any[]> = {}
    activeUsers.value.forEach((user) => {
      const dept = user.department || '未知部门'
      if (!grouped[dept]) {
        grouped[dept] = []
      }
      grouped[dept].push(user)
    })
    return Object.entries(grouped).map(([department, users]) => ({
      department,
      users
    }))
  })

  // 编辑对话框 - 部门选项列表
  const editDepartmentOptions = computed(() => {
    const depts = new Set<string>()
    activeUsers.value.forEach((user) => {
      if (user.department) {
        depts.add(user.department)
      }
    })
    return Array.from(depts).sort()
  })

  // 编辑对话框 - 获取部门人数
  const getEditDepartmentUserCount = (dept: string): number => {
    return activeUsers.value.filter((u) => (u.department || '未知部门') === dept).length
  }

  // 编辑对话框 - 处理部门选择
  const handleEditDepartmentSelect = (departments: string[]) => {
    const userIds = new Set(editForm.value.coveredUserIds)

    departments.forEach((dept) => {
      const deptUsers = activeUsers.value.filter((u) => (u.department || '未知部门') === dept)
      deptUsers.forEach((u) => userIds.add(u.id))
    })

    editForm.value.coveredUserIds = Array.from(userIds)
  }

  // 生成工作周标题
  const generateTitle = () => {
    const { year, weekNumber, groupName } = createForm.value
    createForm.value.title = `${year}W${String(weekNumber).padStart(2, '0')}${groupName}工作计划`
  }

  // 生成批量标题预览
  const generateBatchTitlePreview = () => {
    const { year, weekNumber, batchCount, groupName } = createForm.value
    const titles: string[] = []
    for (let i = 0; i < Math.min(batchCount, 3); i++) {
      titles.push(`${year}W${String(weekNumber + i).padStart(2, '0')}${groupName}工作计划`)
    }
    if (batchCount > 3) {
      titles.push('...')
    }
    return titles.join('、')
  }

  // 根据ISO周计算日期范围（使用本地时区）
  const getWeekDateRange = (year: number, week: number): { start: string; end: string } => {
    // ISO周从周一开始
    const jan4 = new Date(year, 0, 4)
    const jan4Day = jan4.getDay() || 7
    const weekStart = new Date(jan4)
    weekStart.setDate(jan4.getDate() - jan4Day + 1 + (week - 1) * 7)
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekStart.getDate() + 4)

    // 使用本地时区格式化为 YYYY-MM-DD
    const formatLocalDate = (date: Date) => {
      const y = date.getFullYear()
      const m = String(date.getMonth() + 1).padStart(2, '0')
      const d = String(date.getDate()).padStart(2, '0')
      return `${y}-${m}-${d}`
    }

    return {
      start: formatLocalDate(weekStart),
      end: formatLocalDate(weekEnd)
    }
  }

  // 处理批量模式变化
  const handleBatchModeChange = () => {
    generateTitle()
  }

  // 处理批量数量变化
  const handleBatchCountChange = () => {
    // 批量数量变化时不需要特殊处理，只更新预览
  }

  // 处理年份变化
  const handleYearChange = () => {
    generateTitle()
    if (createForm.value.startDate) {
      // 更新起始日期以匹配新年份
      const dateRange = getWeekDateRange(createForm.value.year, createForm.value.weekNumber)
      createForm.value.startDate = new Date(dateRange.start)
    }
  }

  // 处理周序号变化
  const handleWeekNumberChange = () => {
    generateTitle()
    if (createForm.value.year) {
      const dateRange = getWeekDateRange(createForm.value.year, createForm.value.weekNumber)
      createForm.value.startDate = new Date(dateRange.start)
    }
  }

  // 处理工作组名称变化
  const handleGroupNameChange = (value: string) => {
    // 更新工作组名称
    createForm.value.groupName = value

    // 获取该工作组的最新周序号并更新
    const { year, weekNumber } = getGroupLatestWeekNumber(value)
    createForm.value.year = year
    createForm.value.weekNumber = weekNumber

    // 更新起始日期
    const dateRange = getWeekDateRange(year, weekNumber)
    createForm.value.startDate = new Date(dateRange.start)

    // 重新生成标题
    generateTitle()
  }

  // 处理起始日期变化
  const handleStartDateChange = (date: Date | null) => {
    if (date) {
      // 根据选择的日期计算年份和周序号
      const year = date.getFullYear()
      const weekNumber = getWeekNumber(date)
      createForm.value.year = year
      createForm.value.weekNumber = weekNumber
      generateTitle()
    }
  }

  // 计算日期的ISO周序号
  const getWeekNumber = (date: Date): number => {
    const target = new Date(date.valueOf())
    const dayNr = (date.getDay() + 6) % 7
    target.setDate(target.getDate() - dayNr + 3)
    const firstThursday = new Date(target.getFullYear(), 0, 4)
    const weekNumber =
      1 +
      Math.round(
        ((target.getTime() - firstThursday.getTime()) / 86400000 -
          3 +
          ((firstThursday.getDay() + 6) % 7)) /
          7
      )
    return weekNumber
  }

  // 获取当前日期所在的ISO周（格式：2025W46）
  const getCurrentISOWeek = (): string => {
    const now = new Date()
    const year = now.getFullYear()
    const weekNumber = getWeekNumber(now)
    return `${year}W${String(weekNumber).padStart(2, '0')}`
  }

  // 当前周ISO格式
  const currentWeekISO = computed(() => getCurrentISOWeek())

  // 判断一个工作周是否是当前周
  const isCurrentWeek = (week: WorkWeek): boolean => {
    const now = new Date()
    const currentDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const startDate = new Date(week.week_start_date)
    const endDate = new Date(week.week_end_date)

    // 将时间部分设为0，只比较日期
    startDate.setHours(0, 0, 0, 0)
    endDate.setHours(23, 59, 59, 999)

    return currentDate >= startDate && currentDate <= endDate
  }

  // 跳转到当前周
  const jumpToCurrentWeek = () => {
    // 查找所有当前周的工作周
    const currentWeeks = workWeeks.value.filter((week) => isCurrentWeek(week))

    if (currentWeeks.length === 0) {
      ElMessage.warning('未找到当前工作周，请先创建当前周的工作计划')
      return
    }

    let targetWeek: WorkWeek | null = null

    // 1. 优先查找当前用户所在工作组的当前周
    const currentUserDept = userStore.currentUser?.department
    if (currentUserDept) {
      // 从部门中提取工作组名称（例如：研发部算法组 -> 算法组）
      const deptGroupMatch = currentUserDept.match(/([^部]+组)/)
      const userWorkGroup = deptGroupMatch ? deptGroupMatch[1] : null

      if (userWorkGroup) {
        // 在该工作组中找到当前周
        targetWeek =
          currentWeeks.find((week) => {
            const groupName = extractGroupName(week.title)
            return groupName === userWorkGroup
          }) || null

        if (targetWeek) {
          console.log('✅ [WorkLog] 找到当前用户所在工作组的当前周:', targetWeek.title)
        }
      }
    }

    // 2. 如果没找到，选择第一个当前周
    if (!targetWeek) {
      targetWeek = currentWeeks[0]
      console.log('📌 [WorkLog] 选择第一个当前周:', targetWeek.title)

      // 如果有多个当前周，提示用户
      if (currentWeeks.length > 1) {
        const groupNames = currentWeeks.map((w) => extractGroupName(w.title)).join('、')
        ElMessage.info(
          `找到 ${currentWeeks.length} 个工作组的当前周（${groupNames}），已跳转到第一个`
        )
      }
    }

    // 设置当前选中的工作周
    currentWeekId.value = targetWeek.id
    currentWorkWeek.value = targetWeek

    // 确保导航树展开到当前周
    nextTick(() => {
      const treeInstance = treeRef.value
      if (!treeInstance) return

      // 找到当前周所在的组和月份
      const targetGroupName = extractGroupName(targetWeek.title)
      const targetDate = new Date(targetWeek.week_start_date)
      const targetYearMonth = `${targetDate.getFullYear()}年${String(targetDate.getMonth() + 1).padStart(2, '0')}月`

      // 展开工作组
      const groupKey = `group-${targetGroupName}`
      const groupNode = treeInstance.getNode(groupKey)
      if (groupNode && !groupNode.expanded) {
        expandedKeys.value.push(groupKey)
        treeInstance.store.nodesMap[groupKey].expanded = true
      }

      // 展开月份
      nextTick(() => {
        const monthKey = `${targetGroupName}-${targetYearMonth}`
        const monthNode = treeInstance.getNode(monthKey)
        if (monthNode && !monthNode.expanded) {
          expandedKeys.value.push(monthKey)
          treeInstance.store.nodesMap[monthKey].expanded = true
        }

        // 滚动到当前周节点
        nextTick(() => {
          const weekNode = treeInstance.getNode(targetWeek.id)
          if (weekNode) {
            const nodeElement = weekNode.$el
            if (nodeElement) {
              nodeElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
            }
          }
        })
      })
    })

    ElMessage.success(`已跳转到当前工作周：${targetWeek.title}`)
  }

  // 禁用过去的日期
  const disabledDate = (time: Date) => {
    // 允许选择过去30天内的日期，但不能太久远
    const thirtyDaysAgo = new Date()
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
    return time.getTime() < thirtyDaysAgo.getTime()
  }

  // 初始化表单（基于当前选择的工作组或最新工作周）
  const initializeCreateForm = () => {
    let targetGroupName = '标注组' // 默认工作组
    let targetWeek: WorkWeek | null = null

    if (workWeeks.value.length > 0) {
      // 尝试从当前选择的工作周获取工作组
      if (currentWorkWeek.value) {
        targetGroupName = extractGroupName(currentWorkWeek.value.title)

        // 在同一工作组中找到最新的工作周
        const sameGroupWeeks = workWeeks.value
          .filter((w) => extractGroupName(w.title) === targetGroupName)
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

        targetWeek = sameGroupWeeks[0]
      } else {
        // 没有选中，使用整体最新的
        targetWeek = workWeeks.value[0]
        targetGroupName = extractGroupName(targetWeek.title)
      }

      if (targetWeek) {
        const latestTitle = targetWeek.title || ''

        // 尝试解析标题格式：2025W50标注组工作计划
        const match = latestTitle.match(/(\d{4})W(\d{2})(.+?)工作计划/)
        if (match) {
          const year = parseInt(match[1])
          const weekNum = parseInt(match[2])
          const groupName = match[3]

          // 设置为下一周
          createForm.value.year = weekNum >= 52 ? year + 1 : year
          createForm.value.weekNumber = weekNum >= 52 ? 1 : weekNum + 1
          createForm.value.groupName = groupName
        }

        // 继承工作周的覆盖人员
        const config = (targetWeek as any).config
        if (config && Array.isArray(config.covered_user_ids)) {
          createForm.value.coveredUserIds = [...config.covered_user_ids]
        }
      }
    } else {
      // 没有历史工作周，使用当前日期初始化
      const now = new Date()
      createForm.value.year = now.getFullYear()
      createForm.value.weekNumber = getWeekNumber(now)
      createForm.value.groupName = targetGroupName
    }

    // 生成标题和日期
    generateTitle()
    const dateRange = getWeekDateRange(createForm.value.year, createForm.value.weekNumber)
    createForm.value.startDate = new Date(dateRange.start)
  }

  // 监听对话框打开，初始化表单
  watch(showCreateDialog, (show) => {
    if (show) {
      selectedDepartments.value = [] // 清空部门选择
      initializeCreateForm()
    }
  })

  // 创建工作周
  const handleCreate = async () => {
    if (!createForm.value.groupName) {
      ElMessage.warning('请输入工作组名称')
      return
    }
    if (!createForm.value.startDate) {
      ElMessage.warning('请选择起始日期')
      return
    }

    try {
      creating.value = true

      if (createForm.value.batchMode) {
        // 批量创建
        let successCount = 0
        let failCount = 0

        for (let i = 0; i < createForm.value.batchCount; i++) {
          const currentWeek = createForm.value.weekNumber + i
          const currentYear = createForm.value.year

          // 如果周序号超过53，需要跨年
          const actualYear = currentWeek > 53 ? currentYear + 1 : currentYear
          const actualWeek = currentWeek > 53 ? currentWeek - 53 : currentWeek

          const dateRange = getWeekDateRange(actualYear, actualWeek)
          const title = `${actualYear}W${String(actualWeek).padStart(2, '0')}${createForm.value.groupName}工作计划`

          try {
            await workWeekApi.createWorkWeek({
              title,
              week_start_date: dateRange.start,
              week_end_date: dateRange.end,
              week_number: actualWeek,
              status: 'active',
              config: {
                covered_user_ids: createForm.value.coveredUserIds
              }
            })
            successCount++
          } catch (error) {
            console.error(`创建工作周 ${title} 失败:`, error)
            failCount++
          }
        }

        if (successCount > 0) {
          ElMessage.success(
            `成功创建 ${successCount} 个工作周${failCount > 0 ? `，${failCount} 个失败` : ''}`
          )
        } else {
          ElMessage.error('批量创建失败')
        }
      } else {
        // 单个创建
        const dateRange = getWeekDateRange(createForm.value.year, createForm.value.weekNumber)
        await workWeekApi.createWorkWeek({
          title: createForm.value.title,
          week_start_date: dateRange.start,
          week_end_date: dateRange.end,
          week_number: createForm.value.weekNumber,
          status: 'active',
          config: {
            covered_user_ids: createForm.value.coveredUserIds
          }
        })
        ElMessage.success('创建成功')
      }

      showCreateDialog.value = false
      await refreshData()
    } catch (error) {
      console.error('创建失败:', error)
      ElMessage.error('创建失败')
    } finally {
      creating.value = false
    }
  }

  // 批量管理相关
  const filteredWeeksForBatch = computed(() => {
    let filtered = [...workWeeks.value]

    // 按搜索文本过滤
    if (batchSearchText.value) {
      const searchLower = batchSearchText.value.toLowerCase()
      filtered = filtered.filter((w) => w.title.toLowerCase().includes(searchLower))
    }

    // 按状态过滤
    if (batchStatusFilter.value) {
      filtered = filtered.filter((w) => w.status === batchStatusFilter.value)
    }

    // 按创建时间倒序排序
    filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

    return filtered
  })

  // 按月份分组的工作周列表
  const groupedWeeksForBatch = computed(() => {
    const groups: Record<string, any[]> = {}

    filteredWeeksForBatch.value.forEach((week) => {
      const date = new Date(week.week_start_date)
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const yearMonth = `${year}-${String(month).padStart(2, '0')}`

      if (!groups[yearMonth]) {
        groups[yearMonth] = []
      }
      groups[yearMonth].push(week)
    })

    // 转换为数组并排序（按年月倒序）
    return Object.keys(groups)
      .sort((a, b) => b.localeCompare(a))
      .map((yearMonth) => {
        const [year, month] = yearMonth.split('-')
        return {
          key: yearMonth,
          label: `${year}年${parseInt(month)}月`,
          weeks: groups[yearMonth]
        }
      })
  })

  // 格式化紧凑日期
  const formatCompactDate = (startDate: string, endDate: string) => {
    const start = new Date(startDate)
    const end = new Date(endDate)
    const startMonth = start.getMonth() + 1
    const endMonth = end.getMonth() + 1

    if (startMonth === endMonth) {
      return `${startMonth}/${start.getDate()}-${end.getDate()}`
    } else {
      return `${startMonth}/${start.getDate()}-${endMonth}/${end.getDate()}`
    }
  }

  // 全选/取消全选
  const handleSelectAll = (checked: string | number | boolean) => {
    if (checked) {
      selectedWeekIds.value = filteredWeeksForBatch.value.map((w) => w.id)
    } else {
      selectedWeekIds.value = []
    }
  }

  // 监听选中状态，同步全选按钮
  watch(
    () => selectedWeekIds.value.length,
    (newLen) => {
      selectAllWeeks.value = newLen > 0 && newLen === filteredWeeksForBatch.value.length
    }
  )

  // 批量删除
  const handleBatchDelete = async () => {
    if (selectedWeekIds.value.length === 0) {
      ElMessage.warning('请选择要删除的工作周')
      return
    }

    // 保存选中的工作周 ID（因为关闭对话框会清空）
    const weekIdsToDelete = [...selectedWeekIds.value]
    const deleteCount = weekIdsToDelete.length

    try {
      // 临时关闭批量管理对话框,显示确认框
      const tempDialogState = showBatchManageDialog.value
      showBatchManageDialog.value = false
      
      await nextTick()
      
      try {
        await ElMessageBox.confirm(
          `确定要删除选中的 ${deleteCount} 个工作周吗？此操作将同时删除所有相关日志条目，且不可恢复。`,
          '批量删除确认',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning',
            confirmButtonClass: 'el-button--danger'
          }
        )
      } catch (error) {
        // 用户取消,恢复对话框和选中状态
        showBatchManageDialog.value = tempDialogState
        selectedWeekIds.value = weekIdsToDelete
        throw error
      }

      batchDeleting.value = true
      let successCount = 0
      let failCount = 0

      // 使用保存的 ID 列表进行删除
      for (const weekId of weekIdsToDelete) {
        try {
          console.log('🗑️ [WorkLog] 开始删除工作周:', weekId)
          const response = await workWeekApi.deleteWorkWeek(weekId)
          console.log('✅ [WorkLog] 删除成功，响应:', response)
          successCount++

          // 如果删除的是当前选中的工作周，清空选中
          if (currentWeekId.value === weekId) {
            currentWeekId.value = ''
            currentWorkWeek.value = null
          }
        } catch (error: any) {
          console.error(`❌ [WorkLog] 删除工作周 ${weekId} 失败:`, error)
          console.error('❌ [WorkLog] 错误详情:', {
            message: error.message,
            status: error.status,
            response: error.response,
            data: error.data
          })
          failCount++
        }
      }

      if (successCount > 0) {
        ElMessage.success(
          `成功删除 ${successCount} 个工作周${failCount > 0 ? `，${failCount} 个失败` : ''}`
        )
      } else {
        ElMessage.error('批量删除失败')
      }

      showBatchManageDialog.value = false
      selectedWeekIds.value = []
      await refreshData()
    } catch (error: any) {
      if (error !== 'cancel') {
        console.error('批量删除失败:', error)
      }
    } finally {
      batchDeleting.value = false
    }
  }

  // 获取状态文本
  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      active: '进行中',
      archived: '已归档',
      draft: '草稿'
    }
    return statusMap[status] || status
  }

  // 获取状态类型
  const getStatusType = (status: string) => {
    const typeMap: Record<string, any> = {
      active: 'success',
      archived: 'info',
      draft: 'warning'
    }
    return typeMap[status] || ''
  }

  // 批量归档
  const handleBatchArchive = async () => {
    if (selectedWeekIds.value.length === 0) {
      ElMessage.warning('请选择要归档的工作周')
      return
    }

    // 保存选中的工作周 ID（因为关闭对话框会清空）
    const weekIdsToArchive = [...selectedWeekIds.value]
    const archiveCount = weekIdsToArchive.length

    try {
      // 临时关闭批量管理对话框,显示确认框
      const tempDialogState = showBatchManageDialog.value
      showBatchManageDialog.value = false
      
      await nextTick()
      
      try {
        await ElMessageBox.confirm(
          `确定要归档选中的 ${archiveCount} 个工作周吗？归档后可以在筛选中查看。`,
          '批量归档确认',
          {
            confirmButtonText: '确定归档',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch (error) {
        // 用户取消,恢复对话框和选中状态
        showBatchManageDialog.value = tempDialogState
        selectedWeekIds.value = weekIdsToArchive
        throw error
      }

      batchArchiving.value = true
      let successCount = 0
      let failCount = 0

      // 使用保存的 ID 列表进行归档
      for (const weekId of weekIdsToArchive) {
        try {
          await workWeekApi.updateWorkWeek(weekId, {
            status: 'archived'
          })
          successCount++
        } catch (error) {
          console.error(`归档工作周 ${weekId} 失败:`, error)
          failCount++
        }
      }

      if (successCount > 0) {
        ElMessage.success(
          `成功归档 ${successCount} 个工作周${failCount > 0 ? `，${failCount} 个失败` : ''}`
        )
      } else {
        ElMessage.error('批量归档失败')
      }

      showBatchManageDialog.value = false
      selectedWeekIds.value = []
      await refreshData()
    } catch (error: any) {
      if (error !== 'cancel') {
        console.error('批量归档失败:', error)
      }
    } finally {
      batchArchiving.value = false
    }
  }

  // 监听批量管理对话框关闭，清空选中
  watch(
    () => showBatchManageDialog.value,
    (val) => {
      if (!val) {
        selectedWeekIds.value = []
        selectAllWeeks.value = false
        batchSearchText.value = ''
        batchStatusFilter.value = ''
      }
    }
  )

  // 监听编辑对话框打开，清空部门选择
  watch(showEditDialog, (show) => {
    if (show) {
      editSelectedDepartments.value = []
    }
  })

  // 更新工作周
  const handleUpdate = async () => {
    if (!editForm.value.title) {
      ElMessage.warning('请输入工作周标题')
      return
    }
    if (!editForm.value.startDate || !editForm.value.endDate) {
      ElMessage.warning('请选择起止日期')
      return
    }

    try {
      updating.value = true

      await workWeekApi.updateWorkWeek(editingWeek.value!.id, {
        title: editForm.value.title,
        week_start_date: formatDate(editForm.value.startDate),
        week_end_date: formatDate(editForm.value.endDate),
        week_number: editForm.value.weekNumber,
        status: editForm.value.status,
        description: editForm.value.description,
        config: {
          covered_user_ids: editForm.value.coveredUserIds
        }
      })

      ElMessage.success('更新成功')
      showEditDialog.value = false
      await refreshData()

      // 如果更新的是当前选中的工作周，重新加载详情
      if (currentWeekId.value === editingWeek.value!.id) {
        currentWorkWeek.value = workWeeks.value.find((w) => w.id === currentWeekId.value) || null
      }
    } catch (error) {
      console.error('更新失败:', error)
      ElMessage.error('更新失败')
    } finally {
      updating.value = false
    }
  }

  // 加载活跃用户
  const loadActiveUsers = async () => {
    try {
      const response = await userApi.getUsersBasic({
        status: 'active',
        size: 100
      })
      const users = (response as any).list || (response as any).data?.list || []
      activeUsers.value = users
    } catch (error) {
      console.error('加载用户列表失败:', error)
    }
  }

  // 格式化日期
  const formatDate = (date: Date): string => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  // 刷新数据
  const refreshData = async () => {
    await loadWorkWeeks()
  }

  // 打开外部链接
  const openExternalLink = () => {
    window.open('http://192.168.80.100:10086/', '_blank', 'noopener,noreferrer')
    ElMessage.success('已在新标签页打开外部工具')
  }

  // 初始化
  onMounted(async () => {
    await Promise.all([loadWorkWeeks(), loadUsers(), loadActiveUsers()])
  })
</script>

<style lang="scss" scoped>
  .work-log-page {
    background: var(--art-bg-color);
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    padding: 10px;
    box-sizing: border-box;

    .page-container {
      display: flex !important;
      flex-direction: column !important;
      flex: 1;
      min-height: 0;
    }

    .page-body {
      flex: 1 !important;
      min-height: 0 !important;
      overflow: hidden !important;
      gap: 16px;
      height: auto !important;
    }

    /* 左侧导航栏 */
    .sidebar {
      width: 280px;
      padding: 0;
      background: transparent;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      min-height: 0;
      position: relative; /* 确保 z-index 生效 */
      z-index: 1; /* 设置较低的 z-index，确保弹窗能覆盖 */
    }

    .nav-panel {
      flex: 0.95;
      min-height: 0;
      overflow: hidden;
      padding: 16px;
      background: var(--art-main-bg-color);
      border: 1px solid var(--art-card-border);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      display: flex;
      flex-direction: column;

      .filter-section {
        flex-shrink: 0;
        margin-bottom: 16px;

        :deep(.el-input__wrapper) {
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        .archived-toggle {
          margin-top: 12px;
          padding: 8px 12px;
          background: var(--art-bg-color);
          border-radius: 6px;
          display: flex;
          align-items: center;
          justify-content: center;

          :deep(.el-switch) {
            .el-switch__label {
              font-size: 12px;
              color: #606266;
            }

            .el-switch__label.is-active {
              color: #409eff;
            }
          }
        }
      }

      :deep(.el-tree) {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        min-height: 0;
      }
    }

    /* 美化滚动条 */
    .nav-panel::-webkit-scrollbar {
      width: 6px;
    }

    .nav-panel::-webkit-scrollbar-track {
      background: transparent;
      border-radius: 3px;
    }

    .nav-panel::-webkit-scrollbar-thumb {
      background: var(--art-gray-400);
      border-radius: 3px;
    }

    .nav-panel::-webkit-scrollbar-thumb:hover {
      background: var(--art-gray-500);
    }

    // 工作组节点样式（第一级）
    .tree-work-group {
      font-weight: 700;
      color: var(--art-text-gray-900);
      font-size: 15px;
      user-select: none;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;

      .iconfont {
        color: var(--art-primary-color);
        font-size: 16px;
      }
    }

    // 月份分组节点样式（第二级）
    .tree-month-group {
      font-weight: 500;
      color: var(--art-text-gray-700);
      font-size: 14px;
      user-select: none;
      letter-spacing: 0.3px;
      display: flex;
      align-items: center;

      .iconfont {
        color: var(--art-text-gray-500);
        font-size: 14px;
      }
    }

    // 其他分组节点
    .tree-group {
      font-weight: 600;
      color: var(--art-text-gray-800);
      font-size: 14px;
      user-select: none;
      letter-spacing: 0.3px;
    }

    :deep(.el-tree) {
      background: transparent;

      .el-tree-node {
        margin-bottom: 4px;

        &__content {
          height: auto;
          min-height: 36px;
          padding: 4px 8px;
          border-radius: 8px;
          transition: all 0.2s ease;

          &:hover {
            background: var(--art-bg-color);
          }
        }

        &.is-current > .el-tree-node__content {
          background: linear-gradient(
            90deg,
            rgba(6, 182, 212, 0.15) 0%,
            rgba(8, 145, 178, 0.08) 100%
          );
          border-left: 3px solid #06b6d4;
          padding-left: 5px !important;
          box-shadow: 0 1px 3px rgba(6, 182, 212, 0.1);
          font-weight: 600;

          .tree-node {
            color: #06b6d4;

            .node-label {
              color: #06b6d4;
              font-weight: 600;
            }
          }
        }
      }

      .el-tree-node__expand-icon {
        margin-right: 8px;
        color: var(--art-text-gray-600);
        font-size: 14px;
      }
    }

    .tree-node {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 8px;

      .node-label {
        flex: 1;
        font-size: 14px;
        color: var(--art-text-gray-800);

        &.is-current-week {
          font-weight: 600;
          text-decoration: underline;
        }
      }
    }

    /* 右侧主内容区 */
    .main-col {
      flex: 1;
      min-width: 0;
      min-height: 0;
      padding: 0;
      background: transparent;
      display: flex;
      flex-direction: column;
      overflow: hidden;

      .week-detail-wrapper {
        flex: 0.95;
        min-height: 0;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        background: var(--art-main-bg-color);
        border: 1px solid var(--art-card-border);
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

        // 确保工作周详情卡片与导航栏对齐
        :deep(.work-log-week-detail) {
          height: 100%;
          display: flex;
          flex-direction: column;

          .table-card {
            flex: 1;
            min-height: 0;
            border: none;
            box-shadow: none;
            border-radius: 0;

            :deep(.el-card__header) {
              border-radius: 12px 12px 0 0;
            }
          }
        }
      }

      // 空状态样式优化
      :deep(.el-empty) {
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: var(--art-main-bg-color);
        border: 1px solid var(--art-card-border);
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        padding: 80px 0;

        .el-empty__description {
          font-size: 15px;
          color: var(--art-text-gray-600);
        }
      }
    }
  }

  // 批量管理对话框样式
  .batch-manage-container {
    .batch-filters {
      display: flex;
      align-items: center;
    }

    .batch-week-list {
      .batch-group {
        margin-bottom: 16px;

        &:last-child {
          margin-bottom: 0;
        }

        .batch-group-header {
          font-size: 13px;
          font-weight: 600;
          color: var(--art-text-gray-800);
          padding: 8px 12px;
          background: var(--art-bg-color);
          border-radius: 6px;
          margin-bottom: 8px;
          user-select: none;
        }
      }

      .batch-week-item {
        padding: 8px 12px;
        margin-bottom: 4px;
        border-radius: 6px;
        transition: all 0.2s ease;

        &:hover {
          background: var(--art-bg-color);
        }

        :deep(.el-checkbox) {
          width: 100%;

          .el-checkbox__label {
            width: 100%;
            display: flex;
            align-items: center;
          }
        }

        .week-item-compact {
          display: flex;
          align-items: center;
          justify-content: space-between;
          width: 100%;
          gap: 12px;

          .week-title {
            flex: 1;
            font-size: 14px;
            font-weight: 500;
            color: var(--art-text-gray-900);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            min-width: 0;
          }

          .week-info {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 13px;
            flex-shrink: 0;

            .week-date {
              color: var(--art-text-gray-600);
              font-size: 12px;
            }

            .week-entries {
              color: var(--art-text-gray-500);
              font-size: 12px;
            }
          }
        }
      }
    }
  }

  // ========================================
  // 夜间模式额外适配
  // ========================================
  html.dark {
    .work-log-page {
      // 树节点在夜间模式下的额外优化
      .tree-work-group .iconfont {
        opacity: 0.9;
      }

      // 确保卡片边框在夜间模式下可见
      .nav-panel,
      .main-col :deep(.work-log-week-detail .table-card) {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      }
    }
  }
</style>
