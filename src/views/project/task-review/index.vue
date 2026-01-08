<template>
  <div class="task-review">
    <!-- 页面头部 -->
    <ArtPageHeader
      title="任务审核"
      description="审核团队成员提交的标注任务，确保标注质量"
      icon="✅"
      badge="Review"
      theme="orange"
    >
      <template #actions>
        <el-button type="success" @click="refreshTasks">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </template>
    </ArtPageHeader>

    <!-- 审核统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="5">
          <div class="stat-click" @click="quickFilterByStatus('submitted')">
            <ArtStatsCard
              :count="reviewStats.pending"
              title="待审核"
              description="等待审核的任务"
              icon="&#xe7c0;"
              icon-color="#f56c6c"
              icon-bg-color="#fef0f0"
            />
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-click" @click="quickFilterByStatus('skip_pending')">
            <ArtStatsCard
              :count="reviewStats.skipPending"
              title="跳过申请"
              description="申请跳过的任务"
              icon="&#xe7c3;"
              icon-color="#e6a23c"
              icon-bg-color="#fdf6ec"
            />
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-click" @click="quickFilterByStatus('approved')">
            <ArtStatsCard
              :count="reviewStats.approved"
              title="已通过"
              description="审核通过的任务"
              icon="&#xe7c1;"
              icon-color="#67c23a"
              icon-bg-color="#f0f9ff"
            />
          </div>
        </el-col>
        <el-col :span="5">
          <div class="stat-click" @click="quickFilterByStatus('rejected')">
            <ArtStatsCard
              :count="reviewStats.rejected"
              title="已驳回"
              description="审核驳回的任务"
              icon="&#xe7c2;"
              icon-color="#f56c6c"
              icon-bg-color="#fef0f0"
            />
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-click" @click="quickFilterByStatus('')">
            <ArtStatsCard
              :count="reviewStats.total"
              title="总计"
              description="所有任务数量"
              icon="&#xe721;"
              icon-color="#409eff"
              icon-bg-color="#ecf5ff"
            />
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 任务列表（包含搜索筛选） -->
    <el-card class="art-custom-card task-review-card">
      <template #header>
        <div class="card-header-with-filters">
          <div class="header-title">
            <span class="title-text">待审核任务</span>
            <span class="task-count">共 {{ projectStore.total }} 个任务</span>
          </div>

          <!-- 搜索筛选区域 -->
          <div class="filters-section">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索任务标题或描述"
              :prefix-icon="Search"
              clearable
              @input="handleSearch"
              style="width: 240px"
            />
            <el-select
              v-model="searchForm.projectId"
              placeholder="选择项目"
              clearable
              @change="handleSearch"
              style="width: 160px"
            >
              <el-option label="全部项目" value="" />
              <el-option
                v-for="project in projectStore.projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
            <el-select
              v-model="searchForm.status"
              placeholder="审核状态"
              clearable
              @change="handleSearch"
              style="width: 140px"
            >
              <el-option label="全部状态" value="" />
              <el-option label="待审核" value="submitted" />
              <el-option label="跳过申请" value="skip_pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已驳回" value="rejected" />
            </el-select>
            <el-select
              v-model="searchForm.assignedTo"
              placeholder="标注员"
              clearable
              filterable
              @change="handleSearch"
              style="width: 140px"
            >
              <el-option label="全部标注员" value="" />
              <el-option
                v-for="user in userList"
                :key="user.id"
                :label="displayUserLabel(user as any)"
                :value="user.id"
              />
            </el-select>
            <el-button @click="resetSearch" :icon="Refresh">重置</el-button>
            <el-button
              type="primary"
              @click="batchApprove"
              :disabled="selectedTasks.length === 0"
              :icon="CircleCheck"
            >
              批量通过
            </el-button>
            <el-button type="danger" @click="batchReject" :disabled="selectedTasks.length === 0">
              批量驳回
            </el-button>
          </div>
        </div>
      </template>
      <el-table
        v-loading="projectStore.loading"
        :data="tableTasks"
        stripe
        height="calc(100vh - 550px)"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" fixed />

        <!-- 任务标题 -->
        <el-table-column prop="title" label="任务标题" width="220" fixed>
          <template #default="{ row }">
            <div class="task-title-cell">
              <el-tooltip :content="row.title" placement="top" :show-after="500">
                <strong class="task-title-text">{{ row.title }}</strong>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

        <!-- 所属项目 -->
        <el-table-column prop="projectName" label="所属项目" min-width="180">
          <template #default="{ row }">
            <div class="project-name-cell">
              <el-icon class="project-icon"><Folder /></el-icon>
              <span
                v-if="row.projectName || row.project_name"
                class="project-name clickable"
                @click="navigateToProject(row)"
                style="
                  cursor: pointer;
                  color: #606266;
                  font-weight: 500;
                  text-decoration: underline;
                  text-decoration-color: rgba(0, 0, 0, 0.3);
                  text-underline-offset: 2px;
                "
              >
                {{ row.projectName || row.project_name }}
              </span>
              <span v-else class="text-gray-400">未指定项目</span>
            </div>
          </template>
        </el-table-column>

        <!-- 项目分类 -->
        <el-table-column prop="category" label="项目分类" width="140">
          <template #default="{ row }">
            <CategoryTag
              :category="getTaskProjectCategory(row).category"
              :sub-category="getTaskProjectCategory(row).subCategory"
              size="small"
            />
          </template>
        </el-table-column>

        <!-- 标注员 -->
        <el-table-column prop="assignedTo" label="标注员" min-width="120">
          <template #default="{ row }">
            <div class="annotator-cell">
              <span class="annotator-name">{{
                row.assignedToName || row.assigned_to_name || getUserName(row.assignedTo)
              }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- 影像URL -->
        <el-table-column prop="imageUrl" label="影像URL" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div v-if="row.imageUrl || row.image_url" class="image-url-cell">
              <a :href="row.imageUrl || row.image_url" target="_blank" class="image-url-link">
                {{ row.imageUrl || row.image_url }}
              </a>
            </div>
            <span v-else class="text-gray-400">未设置</span>
          </template>
        </el-table-column>

        <!-- 工时 -->
        <el-table-column label="工时" width="90">
          <template #default="{ row }">
            <div class="hours-info">
              <span>{{ row.actualHours || row.estimatedHours || 0 }}h</span>
            </div>
          </template>
        </el-table-column>

        <!-- 提交时间 -->
        <el-table-column label="提交时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.submittedAt) }}
          </template>
        </el-table-column>

        <!-- 任务状态 -->
        <el-table-column prop="status" label="状态" min-width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status) as any" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right" align="right">
          <template #default="{ row }">
            <!-- 待审核状态 - 显示审核按钮 -->
            <template v-if="row.status === 'submitted'">
              <el-button type="primary" size="small" @click="reviewTask(row)"> 审核 </el-button>
              <el-button type="info" size="small" text @click="viewTask(row)"> 查看详情 </el-button>
            </template>

            <!-- 已通过状态 - 只显示查看按钮 -->
            <template v-else-if="row.status === 'approved'">
              <el-button type="info" size="small" text @click="viewTask(row)"> 查看详情 </el-button>
            </template>

            <!-- 已驳回状态 - 显示查看按钮，等待重新提交 -->
            <template v-else-if="row.status === 'rejected'">
              <el-button type="info" size="small" text @click="viewTask(row)"> 查看详情 </el-button>
            </template>

            <!-- 跳过申请状态 - 显示跳过审核按钮 -->
            <template v-else-if="row.status === 'skip_pending'">
              <el-button type="warning" size="small" @click="reviewSkipRequest(row)">
                跳过审核
              </el-button>
              <el-button
                type="info"
                size="small"
                text
                @click="viewTask(row)"
                style="margin-left: 8px"
              >
                查看详情
              </el-button>
            </template>

            <!-- 其他状态 - 显示查看按钮 -->
            <template v-else>
              <el-button type="info" size="small" text @click="viewTask(row)"> 查看详情 </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="projectStore.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="showReviewDialog"
      :title="`审核任务：${currentTask?.title}`"
      width="90%"
      :close-on-click-modal="false"
    >
      <div v-if="currentTask" class="review-container">
        <!-- 任务信息 -->
        <div class="task-info-section">
          <h4>任务信息</h4>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="任务标题">
              {{ currentTask.title }}
            </el-descriptions-item>
            <el-descriptions-item label="所属项目">
              {{ currentTask.projectName || (currentTask as any).project_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="标注员">
              {{
                (currentTask as any).assignedToName ||
                (currentTask as any).assigned_to_name ||
                getUserName((currentTask as any).assignedTo)
              }}
            </el-descriptions-item>
            <el-descriptions-item label="任务优先级">
              <el-tag :type="getPriorityType(currentTask.priority) as any">
                {{ getPriorityText(currentTask.priority) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{
                (currentTask as any).createdAt
                  ? formatDateTime((currentTask as any).createdAt as any)
                  : (currentTask as any).created_at
                    ? formatDateTime((currentTask as any).created_at as any)
                    : '-'
              }}
            </el-descriptions-item>
            <el-descriptions-item label="提交时间">
              {{ currentTask.submittedAt ? formatDateTime(currentTask.submittedAt as any) : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="实际工时">
              {{ currentTask.actualHours || 0 }}小时
            </el-descriptions-item>
            <el-descriptions-item label="任务描述" :span="3">
              {{ currentTask.description || '无描述' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 员工上传的截图（按提交次数分组） -->
        <div class="image-section" v-if="groupedAnnotationImages.length > 0">
          <h4>员工提交的标注截图</h4>

          <!-- 分组显示截图 -->
          <div
            v-for="(group, gIdx) in groupedAnnotationImages"
            :key="'group-' + gIdx"
            class="submission-group"
          >
            <!-- 分组标题 -->
            <div class="group-header">
              <div class="group-badge">
                <span class="badge-icon">📤</span>
                <span class="badge-text">第 {{ group.submissionCount }} 次提交</span>
              </div>
              <div class="group-time">{{ formatDateTime(group.submissionTime as any) }}</div>
            </div>

            <!-- 分组截图 -->
            <div v-if="group.screenshots.length > 0" class="image-gallery">
              <div
                v-for="(image, index) in group.screenshots"
                :key="image.id || index"
                class="image-item"
              >
                <el-image
                  :src="rewriteFileUrl(image.url || image)"
                  fit="cover"
                  lazy
                  :preview-src-list="
                    group.screenshots.map((s) => rewriteFileUrl(s.url)).filter(Boolean) as string[]
                  "
                  :initial-index="index"
                  :preview-teleported="true"
                  :z-index="3000"
                  style="width: 100%; height: 150px"
                />
              </div>
            </div>

            <!-- 无截图提示 -->
            <div v-else class="no-images">
              <el-icon><Picture /></el-icon>
              <span>该次提交未上传截图</span>
            </div>
          </div>
        </div>

        <!-- 标注说明 -->
        <div class="annotation-section" v-if="annotationComment">
          <h4>标注说明</h4>
          <div class="annotation-content">
            <el-input
              v-model="annotationComment"
              type="textarea"
              :rows="4"
              readonly
              placeholder="无标注说明"
            />
          </div>
        </div>

        <!-- 审核表单 -->
        <div class="review-form-section">
          <h4>审核操作</h4>
          <el-form :model="reviewForm" :rules="reviewRules" ref="reviewFormRef" label-width="100px">
            <el-form-item label="审核结果" prop="approved">
              <el-radio-group v-model="reviewForm.approved">
                <el-radio :label="true">审核通过</el-radio>
                <el-radio :label="false">打回重标</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item v-if="reviewForm.approved" label="任务评分" prop="score">
              <el-rate
                v-model="reviewForm.score"
                :max="5"
                show-text
                text-color="#ff9900"
                :texts="['极差', '较差', '一般', '良好', '优秀']"
              />
            </el-form-item>

            <el-form-item v-if="!reviewForm.approved" label="上传截图">
              <el-upload
                ref="rejectUploadRef"
                :action="uploadAction"
                :auto-upload="false"
                :on-change="handleRejectImageChange"
                :on-remove="handleRejectImageRemove"
                :file-list="reviewForm.rejectImages"
                list-type="picture-card"
                multiple
                accept="image/*"
              >
                <el-icon><Plus /></el-icon>
                <div class="upload-text">点击上传截图</div>
              </el-upload>
              <div class="upload-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>请上传需要改进的截图示例（可选）</span>
              </div>
            </el-form-item>

            <el-form-item label="审核意见" prop="comment">
              <el-input
                v-model="reviewForm.comment"
                type="textarea"
                :rows="4"
                :placeholder="
                  reviewForm.approved ? '请填写审核通过的评价（可选）' : '请填写需要改进的意见'
                "
              />
              <span v-if="!reviewForm.approved" class="form-tip"
                >默认：审核意见已经在截图中标明</span
              >
            </el-form-item>
          </el-form>
        </div>
      </div>

      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button
          :type="reviewForm.approved ? 'success' : 'warning'"
          @click="submitReview"
          :loading="submitting"
        >
          {{ reviewForm.approved ? '审核通过' : '打回重标' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 跳过审核对话框 -->
    <el-dialog
      v-model="showSkipReviewDialog"
      :title="`跳过审核：${currentTask?.title}`"
      width="90%"
      :close-on-click-modal="false"
    >
      <div v-if="currentTask" class="skip-review-content">
        <!-- 任务基本信息 -->
        <el-card class="art-custom-card" style="margin-bottom: 20px">
          <template #header>
            <div class="card-header">
              <span>任务信息</span>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="任务标题">
              {{ currentTask.title }}
            </el-descriptions-item>
            <el-descriptions-item label="所属项目">
              {{ (currentTask as any).projectName }}
            </el-descriptions-item>
            <el-descriptions-item label="标注员">
              {{ (currentTask as any).assignedToName || (currentTask as any).assignedTo || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="申请时间">
              {{
                formatDateTime(
                  (currentTask as any).skip_requested_at || (currentTask as any).skipRequestedAt
                )
              }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 跳过申请原因 -->
        <el-card class="art-custom-card" style="margin-bottom: 20px">
          <template #header>
            <div class="card-header">
              <span>跳过原因</span>
            </div>
          </template>
          <div class="skip-reason">
            <p>{{ skipRequestReason || '无跳过原因说明' }}</p>
          </div>
        </el-card>

        <!-- 跳过申请截图 -->
        <el-card
          v-if="skipRequestImages.length > 0"
          class="art-custom-card"
          style="margin-bottom: 20px"
        >
          <template #header>
            <div class="card-header">
              <span>申请截图</span>
            </div>
          </template>
          <div class="skip-images">
            <div class="image-gallery">
              <div v-for="(img, index) in skipRequestImages" :key="index" class="image-item">
                <el-image
                  :src="rewriteFileUrl(img.url)"
                  fit="cover"
                  lazy
                  :preview-src-list="
                    skipRequestImages.map((i) => rewriteFileUrl(i.url)).filter(Boolean) as string[]
                  "
                  :initial-index="index"
                  :preview-teleported="true"
                  :z-index="3000"
                  :hide-on-click-modal="true"
                  class="skip-image"
                />
                <div class="image-name">{{ img.name }}</div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 审核决定 -->
        <el-card class="art-custom-card">
          <template #header>
            <div class="card-header">
              <span>审核决定</span>
            </div>
          </template>
          <el-form
            ref="skipReviewFormRef"
            :model="skipReviewForm"
            :rules="skipReviewRules"
            label-width="100px"
          >
            <el-form-item label="审核结果" prop="approved">
              <el-radio-group v-model="skipReviewForm.approved">
                <el-radio :label="true" size="large">
                  <el-icon color="#67c23a"><CircleCheck /></el-icon>
                  同意跳过
                </el-radio>
                <el-radio :label="false" size="large">
                  <el-icon color="#f56c6c"><CircleClose /></el-icon>
                  拒绝跳过
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="审核意见" prop="comment">
              <el-input
                v-model="skipReviewForm.comment"
                type="textarea"
                :rows="4"
                :placeholder="
                  skipReviewForm.approved ? '选填：同意跳过的补充说明' : '必填：拒绝跳过的原因'
                "
                maxlength="500"
                show-word-limit
              />
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <template #footer>
        <el-button @click="showSkipReviewDialog = false">取消</el-button>
        <el-button
          :type="skipReviewForm.approved ? 'success' : 'warning'"
          @click="submitSkipReview"
          :loading="submitting"
        >
          {{ skipReviewForm.approved ? '同意跳过' : '拒绝跳过' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="任务详情"
      width="92%"
      top="3vh"
      :close-on-click-modal="false"
      class="task-detail-dialog"
    >
      <div v-if="currentTask" class="detail-content">
        <!-- 已驳回任务的特殊提示 -->
        <div v-if="currentTask.status === 'rejected'" class="rejected-notice">
          <el-alert title="任务已被驳回" type="warning" :closable="false" show-icon>
            <template #default>
              <p>此任务已被审核人员驳回，需要标注员根据下方审核意见进行修改后重新提交。</p>
              <p
                ><strong>驳回时间：</strong
                >{{
                  currentTask.reviewedAt ? formatDateTime(currentTask.reviewedAt as any) : '-'
                }}</p
              >
              <p
                ><strong>审核人：</strong
                >{{ currentTask.reviewedBy ? getUserName(currentTask.reviewedBy as any) : '-' }}</p
              >
            </template>
          </el-alert>
        </div>

        <!-- 已通过任务的特殊提示 -->
        <div v-else-if="currentTask.status === 'approved'" class="approved-notice">
          <el-alert title="任务已通过审核" type="success" :closable="false" show-icon>
            <template #default>
              <p>此任务已通过审核，标注工作已完成。</p>
              <p
                ><strong>通过时间：</strong
                >{{
                  currentTask.reviewedAt ? formatDateTime(currentTask.reviewedAt as any) : '-'
                }}</p
              >
              <p
                ><strong>审核人：</strong
                >{{ currentTask.reviewedBy ? getUserName(currentTask.reviewedBy as any) : '-' }}</p
              >
              <p v-if="currentTask.score"
                ><strong>任务评分：</strong
                ><el-rate v-model="currentTask.score" disabled show-score text-color="#ff9900"
              /></p>
            </template>
          </el-alert>
        </div>

        <el-descriptions :column="2" border class="task-descriptions">
          <el-descriptions-item label="任务标题">
            {{ currentTask.title }}
          </el-descriptions-item>
          <el-descriptions-item label="所属项目">
            {{ (currentTask as any).projectName || (currentTask as any).project_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="标注员">
            {{
              (currentTask as any).assignedToName ||
              (currentTask as any).assigned_to_name ||
              getUserName((currentTask as any).assignedTo)
            }}
          </el-descriptions-item>
          <el-descriptions-item label="任务状态">
            <el-tag :type="getStatusType(currentTask.status) as any">
              {{ getStatusText(currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="影像URL" :span="2">
            <a
              v-if="(currentTask as any).imageUrl || (currentTask as any).image_url"
              :href="(currentTask as any).imageUrl || (currentTask as any).image_url"
              target="_blank"
              class="image-url-link"
            >
              {{ (currentTask as any).imageUrl || (currentTask as any).image_url }}
            </a>
            <span v-else class="text-gray-400">未设置</span>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime((currentTask as any).createdAt || (currentTask as any).created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{
              (currentTask as any).submittedAt || (currentTask as any).submitted_at
                ? formatDateTime(
                    ((currentTask as any).submittedAt || (currentTask as any).submitted_at) as any
                  )
                : '-'
            }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="(currentTask as any).reviewedAt || (currentTask as any).reviewed_at"
            label="审核时间"
          >
            {{
              (currentTask as any).reviewedAt || (currentTask as any).reviewed_at
                ? formatDateTime(
                    ((currentTask as any).reviewedAt || (currentTask as any).reviewed_at) as any
                  )
                : '-'
            }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="(currentTask as any).reviewedBy || (currentTask as any).reviewed_by_name"
            label="审核人"
          >
            {{
              (currentTask as any).reviewedByName ||
              (currentTask as any).reviewed_by_name ||
              getUserName((currentTask as any).reviewedBy as any)
            }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="currentTask.score && currentTask.status === 'approved'"
            label="任务评分"
          >
            <el-rate v-model="currentTask.score" disabled show-score text-color="#ff9900" />
          </el-descriptions-item>
          <el-descriptions-item label="任务描述" :span="2">
            {{ currentTask.description || '无描述' }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="(currentTask as any).reviewComment || (currentTask as any).review_comment"
            label="审核意见"
            :span="2"
          >
            <div
              class="review-comment"
              :class="{ 'rejected-comment': currentTask.status === 'rejected' }"
            >
              {{ (currentTask as any).reviewComment || (currentTask as any).review_comment }}
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 横向时间轴 -->
        <div class="timeline-section">
          <h4>任务生命周期</h4>
          <div
            v-if="(currentTask as any).timeline && (currentTask as any).timeline.length"
            class="timeline-wrapper"
          >
            <SimpleTimeline
              :timeline="(currentTask as any).timeline"
              :current-status="currentTask.status"
            />
          </div>
          <div v-else class="no-timeline">
            <el-empty description="暂无时间轴记录" />
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
  import {
    Refresh,
    Clock,
    CircleCheck,
    CircleClose,
    Document,
    Search,
    Picture,
    Plus,
    InfoFilled,
    Folder,
    User as UserIcon
  } from '@element-plus/icons-vue'
  import { taskApi as _taskApi } from '@/api/projectApi'
  import { useProjectStore } from '@/store/modules/project'
  import { useUserStore } from '@/store/modules/user'
  import type { Task, User } from '@/types/project'
  import ArtStatsCard from '@/components/core/cards/art-stats-card/index.vue'
  import SimpleTimeline from '@/components/custom/SimpleTimeline.vue'
  import CategoryTag from '@/components/project/CategoryTag.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'
  import {
    formatDateTime as formatDateTimeUtil,
    formatDate as formatDateUtil
  } from '@/utils/timeFormat'

  const projectStore = useProjectStore()
  const router = useRouter()

  // 跳转到项目管理
  const navigateToProject = (row: any) => {
    const projectId = row.projectId || row.project_id
    if (projectId) {
      router.push({
        path: '/project/management',
        query: { projectId }
      })
    } else {
      ElMessage.warning('项目ID不存在')
    }
  }

  // 响应式数据
  const showReviewDialog = ref(false)
  const showDetailDialog = ref(false)
  const showSkipReviewDialog = ref(false)
  const currentTask = ref<Task | null>(null)
  const submitting = ref(false)
  const selectedTasks = ref<Task[]>([])
  const userList = ref<User[]>([])
  // 组装标注员列表：合并用户接口与任务中出现的标注员去重
  const buildAnnotatorList = () => {
    console.log('🔨 [TaskReview] 构建标注员列表')
    console.log('📋 [TaskReview] projectStore.users:', projectStore.users)

    // 从用户接口获取标注员角色的用户
    const fromUsers = ((projectStore.users as any[]) || [])
      .filter((u) => {
        if (!u) return false
        const role = u.role || u.role_name
        // 只显示标注员角色
        return role === 'annotator'
      })
      .map((u) => ({
        id: u.id,
        realName: u.real_name || u.realName || u.username,
        role: u.role
      }))

    console.log('👥 [TaskReview] 从用户接口筛选的标注员:', fromUsers)

    // 从任务中提取实际分配的标注员
    const fromTasks = (allReviewableTasks.value as any[])
      .map((t) => ({
        id: t.assignedTo || t.assigned_to,
        realName: t.assignedToName || t.assigned_to_name,
        role: 'annotator' // 从任务中提取的用户默认标记为标注员
      }))
      .filter((u) => u.id && u.id !== '-')

    console.log('📝 [TaskReview] 从任务中提取的标注员:', fromTasks)

    // 合并去重（优先使用用户接口的数据，因为更完整准确）
    const map = new Map<string, any>()

    // 先添加从用户接口获取的数据（优先级高）
    for (const u of fromUsers) {
      const id = (u as any).id
      if (!id || id === '-') continue
      map.set(id, {
        id,
        realName: (u as any).realName,
        role: (u as any).role
      })
    }

    // 再添加从任务中提取的数据（作为补充）
    for (const u of fromTasks) {
      const id = (u as any).id
      if (!id || id === '-') continue
      // 只有在 map 中不存在时才添加
      if (!map.has(id)) {
        const name =
          (u as any).realName ||
          (u as any).real_name ||
          (u as any).name ||
          `用户${String(id).slice(-4)}`
        map.set(id, {
          id,
          realName: name,
          role: (u as any).role || 'annotator'
        })
      }
    }

    // 转换为数组并按姓名排序
    userList.value = Array.from(map.values()).sort((a, b) => {
      return a.realName.localeCompare(b.realName, 'zh-CN')
    })

    console.log('✅ [TaskReview] 最终标注员列表 (去重后):', {
      总数: userList.value.length,
      列表: userList.value
    })
  }

  const displayUserLabel = (u: any) =>
    u?.realName || u?.name || `用户${String(u?.id || '').slice(-4)}`

  const reviewFormRef = ref<FormInstance>()
  const skipReviewFormRef = ref<FormInstance>()
  // 统计用的全量任务（不受筛选影响）
  const allReviewableTasks = ref<Task[]>([])
  // 表格展示用任务（受筛选影响）
  const tableTasks = ref<Task[]>([])

  // 搜索表单
  const searchForm = reactive({
    keyword: '',
    projectId: '',
    status: '', // 默认显示所有可审核任务
    assignedTo: ''
  })

  // 分页
  const pagination = reactive({
    page: 1,
    pageSize: 20
  })

  // 审核表单
  const reviewForm = reactive({
    approved: true,
    score: 5,
    comment: '',
    rejectImages: [] as any[]
  })

  // 跳过审核表单
  const skipReviewForm = reactive({
    approved: true,
    comment: ''
  })

  // 表单验证规则
  const reviewRules = {
    approved: [{ required: true, message: '请选择审核结果', trigger: 'change' }],
    score: [
      {
        required: true,
        message: '请给任务评分',
        trigger: 'change',
        validator: (rule: any, value: any, callback: any) => {
          if (reviewForm.approved && (!value || value === 0)) {
            callback(new Error('请给任务评分'))
          } else {
            callback()
          }
        }
      }
    ]
    // ✅ 审核意见改为完全可选，不做验证（会使用默认值）
    // comment: [
    //   { validator: (rule: any, value: any, callback: any) => {
    //     if (!reviewForm.approved && !value.trim()) {
    //       callback(new Error('打回重标时必须填写改进意见'))
    //     } else {
    //       callback()
    //     }
    //   }}
    // ]
  }

  // 跳过审核表单验证规则
  const skipReviewRules = {
    comment: [
      {
        validator: (rule: any, value: any, callback: any) => {
          // 拒绝跳过时必须填写原因，同意跳过时可选
          if (!skipReviewForm.approved && !value.trim()) {
            callback(new Error('拒绝跳过时必须填写原因'))
          } else {
            callback()
          }
        }
      }
    ]
  }

  // 计算审核统计
  const reviewStats = computed(() => {
    const tasks = allReviewableTasks.value
    return {
      pending: tasks.filter((t) => t.status === 'submitted').length, // 待审核
      skipPending: tasks.filter((t) => t.status === 'skip_pending').length, // 跳过申请
      approved: tasks.filter((t) => t.status === 'approved').length, // 已通过
      rejected: tasks.filter((t) => t.status === 'rejected').length, // 已驳回
      total: tasks.length // 总计
    }
  })

  // 按提交次数分组的标注截图
  interface SubmissionGroup {
    submissionCount: number
    submissionTime: string
    screenshots: any[]
  }

  const groupedAnnotationImages = computed<SubmissionGroup[]>(() => {
    const task = currentTask.value as any
    if (!task || !task.timeline) {
      // 如果没有timeline，返回单组（兼容旧逻辑）
      return annotationImages.value.length > 0
        ? [
            {
              submissionCount: 1,
              submissionTime: task?.submittedAt || task?.submitted_at || '',
              screenshots: annotationImages.value
            }
          ]
        : []
    }

    // 从timeline中找到所有提交事件（降序：最新的在前）
    const submissionEvents = task.timeline
      .filter((event: any) => event.type === 'submitted')
      .sort((a: any, b: any) => new Date(b.time).getTime() - new Date(a.time).getTime())

    if (submissionEvents.length === 0) {
      return []
    }

    // 为每个提交事件匹配截图（使用时间最接近的策略）
    const totalSubmissions = submissionEvents.length
    const groups: SubmissionGroup[] = submissionEvents.map((event: any, index: number) => {
      const eventTime = new Date(event.time).getTime()
      const tolerance = 60 * 1000 // 60秒容差

      // 找到与该事件时间最接近的截图
      const matchedScreenshots = (task.attachments || [])
        .filter((att: any) => {
          if (att.attachment_type !== 'annotation_screenshot') return false
          if (!att.created_at) return false

          let attCreatedAt = att.created_at
          // 处理时区问题
          if (
            !attCreatedAt.includes('Z') &&
            !attCreatedAt.includes('+') &&
            !attCreatedAt.match(/-\d{2}:\d{2}$/)
          ) {
            attCreatedAt += 'Z'
          }

          const attTime = new Date(attCreatedAt).getTime()
          const timeDiff = Math.abs(attTime - eventTime)

          return timeDiff <= tolerance
        })
        .sort((a: any, b: any) => {
          // 按与事件时间的接近程度排序
          let aTime = a.created_at
          let bTime = b.created_at
          if (!aTime.includes('Z') && !aTime.includes('+') && !aTime.match(/-\d{2}:\d{2}$/))
            aTime += 'Z'
          if (!bTime.includes('Z') && !bTime.includes('+') && !bTime.match(/-\d{2}:\d{2}$/))
            bTime += 'Z'

          const aDiff = Math.abs(new Date(aTime).getTime() - eventTime)
          const bDiff = Math.abs(new Date(bTime).getTime() - eventTime)
          return aDiff - bDiff
        })

      // 去重
      const seen = new Set<string>()
      const uniqueScreenshots = matchedScreenshots
        .filter((att: any) => {
          const key = att.file_url || att.file_name || att.id
          if (key && !seen.has(key)) {
            seen.add(key)
            return true
          }
          return false
        })
        .map((attachment: any) => ({
          url: attachment.file_url,
          name: attachment.file_name,
          id: attachment.id,
          created_at: attachment.created_at
        }))

      return {
        submissionCount: totalSubmissions - index, // 降序后第一个是最新的
        submissionTime: event.time,
        screenshots: uniqueScreenshots
      }
    })

    return groups
  })

  // 标注图片展示 - 从 attachments 中获取标注截图（保留原有逻辑用于兼容）
  const annotationImages = computed(() => {
    if (!currentTask.value) return [] as any[]

    // 优先从 attachments 中获取标注截图
    const atts = (currentTask.value as any).attachments as Array<any> | undefined
    if (atts && Array.isArray(atts)) {
      const screenshots = atts
        .filter(
          (attachment: any) => attachment && attachment.attachment_type === 'annotation_screenshot'
        )
        .map((attachment: any) => ({
          url: attachment.file_url,
          name: attachment.file_name,
          id: attachment.id
        }))

      if (screenshots.length > 0) {
        console.log('📷 [TaskReview] 从 attachments 中找到标注截图:', screenshots)
        return screenshots
      }
    }

    // 兼容旧数据：从 annotationData.images 中获取
    if ((currentTask.value as any).annotationData) {
      try {
        const data =
          typeof (currentTask.value as any).annotationData === 'string'
            ? JSON.parse((currentTask.value as any).annotationData)
            : (currentTask.value as any).annotationData

        if (data.images && Array.isArray(data.images)) {
          console.log('📷 [TaskReview] 从 annotationData 中找到标注图片:', data.images)
          return data.images.map((img: any) => ({
            url: typeof img === 'string' ? img : img.url,
            name: typeof img === 'string' ? img.split('/').pop() : img.name
          }))
        }

        if (data.uploaded_images && Array.isArray(data.uploaded_images)) {
          console.log('📷 [TaskReview] 从 uploaded_images 中找到标注图片:', data.uploaded_images)
          return data.uploaded_images.map((url: string) => ({
            url,
            name: url.split('/').pop()
          }))
        }
      } catch (error) {
        console.error('❌ [TaskReview] 解析 annotationData 失败:', error)
      }
    }

    return []
  })

  // 预览列表（与会议记录封面预览一致使用 ElementPlus 预览能力）
  // URL 规范化：与文章封面预览一致，将 MinIO 直链改为后端代理路径，避免跨域/权限问题
  const rewriteFileUrl = (u?: string) =>
    u ? u.replace(/^https?:\/\/[^/]+\/medical-annotations\//, '/api/files/') : u
  const annotationPreviewList = computed(() =>
    (annotationImages.value || []).map((i: any) => rewriteFileUrl(i.url || i))
  )

  // 跳过申请图片展示
  const skipRequestImages = computed(() => {
    if (!currentTask.value) return [] as any[]

    const task = currentTask.value as any
    const images = task.skip_request_images || task.skipRequestImages

    if (images && Array.isArray(images)) {
      return images.map((img: any) => ({
        url: typeof img === 'string' ? img : img.url,
        name: typeof img === 'string' ? img.split('/').pop() : img.name
      }))
    }

    return []
  })

  // 跳过申请原因展示
  const skipRequestReason = computed(() => {
    if (!currentTask.value) return ''
    const task = currentTask.value as any
    return task.skip_request_reason || task.skipRequestReason || ''
  })

  // 标注说明展示
  const annotationComment = computed(() => {
    if (!currentTask.value || !(currentTask.value as any).annotationData) return ''

    try {
      const data =
        typeof (currentTask.value as any).annotationData === 'string'
          ? JSON.parse((currentTask.value as any).annotationData)
          : (currentTask.value as any).annotationData

      return data.comment || ''
    } catch (error) {
      return ''
    }
  })

  // 标注结果展示
  const annotationDisplay = computed(() => {
    if (!currentTask.value || !currentTask.value.annotationData) return ''

    try {
      if (typeof currentTask.value.annotationData === 'string') {
        return currentTask.value.annotationData
      } else {
        return JSON.stringify(currentTask.value.annotationData, null, 2)
      }
    } catch (error) {
      return currentTask.value.annotationData
    }
  })

  // 获取任务列表
  const fetchTasks = async () => {
    try {
      console.log('📋 [TaskReview] 获取任务列表开始')

      // 对于审核页面，确保只显示可审核的任务状态
      let statusArray: string[] | undefined
      if (searchForm.status === '') {
        // “总计”不传status，让后端返回全部，再在前端按接受状态本地筛选
        statusArray = undefined
      } else if (searchForm.status) {
        statusArray = [searchForm.status]
      } else {
        // 清空选择（null/undefined）时默认显示待审核
        statusArray = ['submitted']
      }

      const params: any = {
        page: pagination.page,
        pageSize: pagination.pageSize,
        keyword: searchForm.keyword || undefined,
        projectId: searchForm.projectId || undefined,
        status: statusArray,
        assignedTo: searchForm.assignedTo || undefined,
        // 添加审核页面标识
        isReviewPage: true
      }
      // 移除 undefined 字段，避免影响后端过滤
      Object.keys(params).forEach((k) => params[k] === undefined && delete params[k])

      console.log('📊 [TaskReview] 查询参数:', params)

      await projectStore.fetchTasks(params)
      // 直接使用后端筛选结果，避免分页错位
      let rows = [...projectStore.tasks]
      // 兜底修正：部分环境下后端对 skip_pending 返回过宽，前端再精确一次
      if (searchForm.status === 'skip_pending') {
        rows = rows.filter((t: any) => t.status === 'skip_pending')
      }
      tableTasks.value = rows
      // 同步刷新全量统计数据
      await fetchStatsTasks()
      // 构建标注员筛选数据
      buildAnnotatorList()

      const tasks = projectStore.tasks
      console.log('✅ [TaskReview] 任务列表获取成功', {
        任务数量: tasks.length,
        状态统计: {
          submitted: tasks.filter((t) => t.status === 'submitted').length,
          approved: tasks.filter((t) => t.status === 'approved').length,
          rejected: tasks.filter((t) => t.status === 'rejected').length,
          skip_pending: tasks.filter((t) => t.status === 'skip_pending').length,
          其他状态: tasks.filter(
            (t) => !['submitted', 'approved', 'rejected', 'skip_pending'].includes(t.status)
          ).length
        },
        示例任务: tasks.slice(0, 2).map((t) => ({
          id: t.id,
          title: t.title,
          status: t.status,
          projectName: (t as any).projectName || (t as any).project_name
        }))
      })

      // 检查是否有不应该在审核页面显示的任务
      const invalidStatusTasks = tasks.filter(
        (t) => !['submitted', 'approved', 'rejected', 'skip_pending'].includes(t.status)
      )
      if (invalidStatusTasks.length > 0) {
        console.warn(
          '⚠️ [TaskReview] 发现不应该在审核页面显示的任务:',
          invalidStatusTasks.map((t) => ({ id: t.id, status: t.status }))
        )
      }

      if (tasks.length === 0) {
        console.warn('⚠️ [TaskReview] 未获取到任何任务，可能的原因:')
        console.warn('1. 暂无需要审核的任务')
        console.warn('2. 筛选条件过于严格')
        console.warn('3. 后端 API 返回的数据为空')
      }
    } catch (error) {
      console.error('❌ [TaskReview] 获取任务列表失败:', error)
      ElMessage.error('获取任务列表失败')
      throw error
    }
  }

  // 获取不受筛选影响的全量审核相关任务（submitted/approved/rejected 全部）
  const fetchStatsTasks = async () => {
    try {
      const res: any = await _taskApi.getTasks({ page: 1, pageSize: 10000 })
      const list = (res && res.data && (res.data.list || res.data)) || []
      allReviewableTasks.value = list.filter((t: any) =>
        ['submitted', 'approved', 'rejected', 'skip_pending'].includes(t.status)
      )
      // 每次刷新统计数据后同步刷新标注员列表
      buildAnnotatorList()
    } catch (e) {
      console.error('获取统计任务失败:', e)
    }
  }

  // 获取项目列表
  const fetchProjects = async () => {
    await projectStore.fetchProjects({
      page: 1,
      pageSize: 100,
      status: ['active']
    })
  }

  // 获取用户列表
  const fetchUsers = async () => {
    try {
      console.log('📥 [TaskReview] 开始获取用户列表')
      await projectStore.fetchUsers({
        page: 1,
        pageSize: 200,
        role: 'annotator', // 只获取标注员角色
        status: 'active'
      })
      console.log('✅ [TaskReview] 用户列表获取完成，开始构建标注员列表')
      // 不直接赋值，使用 buildAnnotatorList 来构建完整的标注员列表
      buildAnnotatorList()
    } catch (error) {
      console.error('❌ [TaskReview] 获取用户列表失败:', error)
    }
  }

  // 刷新任务
  const refreshTasks = () => {
    fetchTasks()
  }

  // 搜索处理
  const handleSearch = () => {
    pagination.page = 1
    fetchTasks()
  }

  // 重置搜索
  const resetSearch = () => {
    searchForm.keyword = ''
    searchForm.projectId = ''
    searchForm.status = '' // 重置为全部
    searchForm.assignedTo = ''
    handleSearch()
  }

  // 分页处理
  const handlePageChange = (page: number) => {
    pagination.page = page
    fetchTasks()
  }

  const handlePageSizeChange = (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    fetchTasks()
  }

  // 选择处理
  const handleSelectionChange = (selection: Task[]) => {
    selectedTasks.value = selection
  }

  // 获取状态类型和文本
  const getStatusType = (status: string) => {
    // 确保status不为空
    if (!status || status.trim() === '') {
      return 'info'
    }

    const types = {
      submitted: 'warning',
      approved: 'success',
      rejected: 'danger',
      assigned: 'info',
      in_progress: 'primary',
      pending: 'info'
    }
    return types[status as keyof typeof types] || 'info'
  }

  const getStatusText = (status: string) => {
    const texts = {
      submitted: '待审核',
      skip_pending: '跳过申请',
      approved: '已通过',
      rejected: '已驳回',
      skipped: '已跳过',
      assigned: '已分配',
      in_progress: '进行中',
      pending: '待分配'
    }
    return texts[status as keyof typeof texts] || status
  }

  // 获取优先级类型和文本
  const getPriorityType = (priority: string) => {
    // 确保priority不为空
    if (!priority || priority.trim() === '') {
      return 'info'
    }

    const types = {
      low: 'info',
      medium: 'primary',
      high: 'warning',
      urgent: 'danger'
    }
    return types[priority as keyof typeof types] || 'info'
  }

  const getPriorityText = (priority: string) => {
    const texts = {
      low: '低',
      medium: '中',
      high: '高',
      urgent: '紧急'
    }
    return texts[priority as keyof typeof texts] || priority
  }

  // 格式化日期时间（修复UTC时间8小时时差问题）
  const formatDateTime = (date: string) => {
    return formatDateTimeUtil(date, 'datetime')
  }

  const formatDate = (date: string) => {
    return formatDateUtil(date)
  }

  // 时间轴类型与标题
  const getTimelineType = (type: string): 'info' | 'primary' | 'success' | 'warning' | 'danger' => {
    const map: Record<string, string> = {
      created: 'primary',
      claimed: 'info',
      submitted: 'warning',
      reviewed: 'success',
      restarted: 'primary'
    }
    return (map[type] as any) || 'info'
  }

  const getTimelineTitle = (type: string) => {
    const map: Record<string, string> = {
      created: '创建任务',
      claimed: '领取任务',
      started: '开始标注',
      submitted: '提交审核',
      reviewed: '审核结果',
      restarted: '重新开始'
    }
    return map[type] || type
  }

  // 获取用户名
  const getUserName = (userId?: string) => {
    if (!userId) return '-'
    const user = userList.value.find((u) => u.id === userId)
    return user ? user.realName : `用户${userId.slice(-4)}`
  }

  // 获取任务对应的项目分类
  const getTaskProjectCategory = (task: any) => {
    const project = projectStore.projects.find((p) => p.id === task.projectId)
    return {
      category: project?.category || '',
      subCategory: project?.subCategory || ''
    }
  }

  // 审核任务
  const reviewTask = (task: Task) => {
    currentTask.value = task
    // 重置审核表单
    reviewForm.approved = true
    reviewForm.score = 5
    reviewForm.comment = ''
    reviewForm.rejectImages = []
    showReviewDialog.value = true
  }

  // ✅ 监听审核结果变化，当选择驳回时设置默认审核意见
  watch(
    () => reviewForm.approved,
    (newValue) => {
      if (!newValue && !reviewForm.comment) {
        // 选择驳回且审核意见为空时，设置默认值
        reviewForm.comment = '审核意见已经在截图中标明'
      } else if (newValue && reviewForm.comment === '审核意见已经在截图中标明') {
        // 切换回通过时，如果是默认值则清空
        reviewForm.comment = ''
      }
    }
  )

  // 审核跳过申请
  const reviewSkipRequest = async (task: Task) => {
    try {
      console.log('🔍 [TaskReview] 审核跳过申请:', task.id)

      // 获取完整的任务详情，包括跳过申请信息
      const result = await _taskApi.getTask(task.id)
      const taskDetail: any = (result as any).data || result

      console.log('📋 [TaskReview] 跳过申请任务详情:', {
        id: taskDetail.id,
        title: taskDetail.title,
        skip_request_reason: taskDetail.skip_request_reason,
        skip_request_images: taskDetail.skip_request_images,
        skip_requested_by: taskDetail.skip_requested_by,
        skip_requested_at: taskDetail.skip_requested_at
      })

      const projectName =
        taskDetail.projectName ||
        taskDetail.project_name ||
        projectStore.projects.find(
          (p) => p.id === (taskDetail.project_id || (task as any).projectId)
        )?.name
      currentTask.value = {
        ...task,
        ...taskDetail,
        projectName,
        assignedTo: taskDetail.assignedTo || taskDetail.assigned_to || (task as any).assignedTo,
        assignedToName:
          taskDetail.assignedToName || taskDetail.assigned_to_name || (task as any).assignedToName,
        skip_request_reason: taskDetail.skip_request_reason,
        skip_request_images: taskDetail.skip_request_images,
        skip_requested_by: taskDetail.skip_requested_by,
        skip_requested_at: taskDetail.skip_requested_at
      } as any

      // 重置跳过审核表单
      skipReviewForm.approved = true
      skipReviewForm.comment = ''
      showSkipReviewDialog.value = true
    } catch (error) {
      console.error('❌ [TaskReview] 获取跳过申请详情失败:', error)
      ElMessage.error('获取跳过申请详情失败')
      // 如果获取详情失败，使用原有数据
      currentTask.value = task
      skipReviewForm.approved = true
      skipReviewForm.comment = ''
      showSkipReviewDialog.value = true
    }
  }

  // 查看任务详情
  const viewTask = async (task: Task) => {
    try {
      console.log('🔍 [TaskReview] 查看任务详情:', task.id)

      // 获取完整的任务详情，包括timeline
      const result = await _taskApi.getTask(task.id)
      const taskDetail: any = (result as any).data || result

      console.log('📋 [TaskReview] 任务详情获取成功:', taskDetail)
      console.log('⏰ [TaskReview] 时间轴数据:', taskDetail.timeline)
      console.log('📊 [TaskReview] Timeline事件数量:', taskDetail.timeline?.length || 0)

      // 为每个timeline事件添加attachments引用，以便显示对应阶段的截图
      if (taskDetail.timeline && taskDetail.timeline.length > 0) {
        taskDetail.timeline = taskDetail.timeline.map((event: any) => ({
          ...event,
          attachments: taskDetail.attachments || []
        }))

        taskDetail.timeline.forEach((event: any, index: number) => {
          console.log(`📅 [TaskReview] Timeline事件 ${index + 1}:`, {
            type: event.type,
            time: event.time,
            user_name: event.user_name,
            comment: event.comment,
            attachments_count: event.attachments?.length || 0
          })
        })
      } else {
        console.warn('⚠️ [TaskReview] Timeline数据为空或未定义')
      }

      // 合并列表中的已映射字段，补全缺失信息
      const base: any =
        (tableTasks.value as any[]).find((t: any) => t.id === (task as any).id) || {}
      const projectName =
        taskDetail.projectName ||
        taskDetail.project_name ||
        taskDetail.project?.name ||
        projectStore.projects.find((p) => p.id === (taskDetail.project_id || base.projectId))
          ?.name ||
        base.projectName
      currentTask.value = {
        ...taskDetail,
        projectName,
        assignedTo: taskDetail.assignedTo || taskDetail.assigned_to || base.assignedTo,
        assignedToName:
          taskDetail.assignedToName || taskDetail.assigned_to_name || base.assignedToName,
        createdAt: taskDetail.createdAt || taskDetail.created_at || base.createdAt,
        reviewedByName:
          taskDetail.reviewedByName || taskDetail.reviewed_by_name || base.reviewedByName,
        attachments: taskDetail.attachments || base.attachments || [],
        reviewComment: taskDetail.reviewComment || taskDetail.review_comment || base.reviewComment
      } as any
      showDetailDialog.value = true
    } catch (error) {
      console.error('❌ [TaskReview] 获取任务详情失败:', error)
      ElMessage.error('获取任务详情失败')
      // 如果获取详情失败，使用原有数据
      currentTask.value = task
      showDetailDialog.value = true
    }
  }

  // 提交审核
  const submitReview = async () => {
    if (!reviewFormRef.value || !currentTask.value) return

    try {
      await reviewFormRef.value.validate()
      submitting.value = true

      // 如果是打回重标且有截图，先上传截图到 MinIO
      let uploadedRejectImages: string[] = []
      if (!reviewForm.approved && reviewForm.rejectImages.length > 0) {
        try {
          console.log('📤 [TaskReview] 开始上传审核截图到MinIO:', reviewForm.rejectImages.length)
          const imageFiles = reviewForm.rejectImages
            .filter((img) => img.raw) // 只上传新的文件
            .map((img) => img.raw as File)

          if (imageFiles.length > 0) {
            const uploadResult = await projectStore.uploadReviewImages(
              currentTask.value.id,
              imageFiles
            )
            uploadedRejectImages = uploadResult.urls || []
            console.log('✅ [TaskReview] 审核截图上传成功:', uploadedRejectImages)
          }
        } catch (uploadError) {
          console.error('❌ [TaskReview] 审核截图上传失败:', uploadError)
          ElMessage.error('截图上传失败，请重试')
          return
        }
      }

      // ✅ 如果是驳回且没有填写审核意见，使用默认值
      const finalComment =
        reviewForm.comment.trim() || (!reviewForm.approved ? '审核意见已经在截图中标明' : '')

      const reviewData = {
        approved: reviewForm.approved,
        comment: finalComment,
        score: reviewForm.approved ? reviewForm.score : undefined,
        reject_images: uploadedRejectImages.length > 0 ? uploadedRejectImages : undefined
      }

      console.log('📋 [TaskReview] 准备提交审核:', {
        taskId: currentTask.value.id,
        approved: reviewForm.approved,
        comment: finalComment,
        originalComment: reviewForm.comment,
        rejectImages: uploadedRejectImages,
        reviewData
      })

      await projectStore.reviewTask(
        currentTask.value.id,
        reviewForm.approved ? 'approve' : 'reject',
        finalComment,
        reviewForm.score,
        uploadedRejectImages
      )

      ElMessage.success(reviewForm.approved ? '审核通过' : '已打回重标')
      showReviewDialog.value = false

      // 重置表单
      reviewForm.approved = true
      reviewForm.score = 5
      reviewForm.comment = ''
      reviewForm.rejectImages = []

      fetchTasks()
    } catch (error) {
      console.error('❌ [TaskReview] 审核失败:', error)
      ElMessage.error('审核失败')
    } finally {
      submitting.value = false
    }
  }

  // 提交跳过审核
  const submitSkipReview = async () => {
    if (!currentTask.value) return

    try {
      submitting.value = true

      const { taskApi } = await import('@/api/projectApi')
      await taskApi.reviewSkipRequest(currentTask.value.id, {
        approved: skipReviewForm.approved,
        comment:
          skipReviewForm.comment || (skipReviewForm.approved ? '同意跳过申请' : '拒绝跳过申请')
      })

      ElMessage.success(skipReviewForm.approved ? '已同意跳过' : '已拒绝跳过')
      showSkipReviewDialog.value = false

      // 重置表单
      skipReviewForm.approved = true
      skipReviewForm.comment = ''

      fetchTasks()
      fetchStatsTasks()
    } catch (error) {
      console.error('❌ [TaskReview] 跳过审核失败:', error)
      ElMessage.error('跳过审核失败')
    } finally {
      submitting.value = false
    }
  }

  // 批量审核通过
  const batchApprove = async () => {
    if (selectedTasks.value.length === 0) {
      ElMessage.warning('请选择要审核的任务')
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要批量通过选中的 ${selectedTasks.value.length} 个任务吗？`,
        '确认批量审核',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }
      )

      // 这里应该调用批量审核API
      const promises = selectedTasks.value.map((task) =>
        projectStore.reviewTask(task.id, 'approve', '批量审核通过')
      )

      await Promise.all(promises)
      ElMessage.success('批量审核成功')
      selectedTasks.value = []
      fetchTasks()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('批量审核失败')
      }
    }
  }

  // 批量审核驳回
  const batchReject = async () => {
    if (selectedTasks.value.length === 0) {
      ElMessage.warning('请选择要驳回的任务')
      return
    }

    try {
      const { value: rejectReason } = await ElMessageBox.prompt(
        `确定要批量驳回选中的 ${selectedTasks.value.length} 个任务吗？请输入驳回原因：`,
        '确认批量驳回',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputPattern: /.+/,
          inputErrorMessage: '请输入驳回原因',
          inputPlaceholder: '请输入驳回原因'
        }
      )

      // 这里应该调用批量审核API
      const promises = selectedTasks.value.map((task) =>
        projectStore.reviewTask(task.id, 'reject', rejectReason)
      )

      await Promise.all(promises)
      ElMessage.success('批量驳回成功')
      selectedTasks.value = []
      fetchTasks()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('批量驳回失败')
      }
    }
  }

  // 同意跳过申请
  const approveSkip = async (task: Task) => {
    try {
      await ElMessageBox.confirm(`确定要同意跳过任务"${task.title}"吗？`, '确认同意跳过', {
        confirmButtonText: '同意',
        cancelButtonText: '取消',
        type: 'info'
      })

      // 调用同意跳过API
      const { taskApi } = await import('@/api/projectApi')
      await taskApi.reviewSkipRequest(task.id, {
        approved: true,
        comment: '同意跳过申请'
      })

      ElMessage.success('已同意跳过申请')
      fetchTasks()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('❌ [TaskReview] 同意跳过失败:', error)
        ElMessage.error('同意跳过失败')
      }
    }
  }

  // 拒绝跳过申请
  const rejectSkip = async (task: Task) => {
    try {
      const { value: rejectReason } = await ElMessageBox.prompt(
        `确定要拒绝跳过任务"${task.title}"吗？请输入拒绝原因：`,
        '确认拒绝跳过',
        {
          confirmButtonText: '拒绝',
          cancelButtonText: '取消',
          inputPattern: /.+/,
          inputErrorMessage: '请输入拒绝原因',
          inputPlaceholder: '请输入拒绝原因'
        }
      )

      // 调用拒绝跳过API
      const { taskApi } = await import('@/api/projectApi')
      await taskApi.reviewSkipRequest(task.id, {
        approved: false,
        comment: rejectReason
      })

      ElMessage.success('已拒绝跳过申请')
      fetchTasks()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('❌ [TaskReview] 拒绝跳过失败:', error)
        ElMessage.error('拒绝跳过失败')
      }
    }
  }

  // 上传相关
  const rejectUploadRef = ref()
  const uploadAction = '#'

  // 处理打回重标的图片上传
  const handleRejectImageChange = (file: any, fileList: any[]) => {
    reviewForm.rejectImages = fileList
  }

  // 处理打回重标的图片删除
  const handleRejectImageRemove = (file: any, fileList: any[]) => {
    reviewForm.rejectImages = fileList
  }

  // 支持粘贴板图片上传（微信/QQ 截图后粘贴）
  const handlePasteToReject = (e: ClipboardEvent) => {
    try {
      const items = e.clipboardData?.items
      if (!items || items.length === 0) return
      const files: File[] = []
      for (const it of items as any) {
        if (it.type && it.type.startsWith('image/')) {
          const blob = it.getAsFile?.() as File
          if (blob) {
            const file = new File([blob], `paste_${Date.now()}.png`, {
              type: blob.type || 'image/png'
            })
            files.push(file)
          }
        }
      }
      if (files.length > 0) {
        files.forEach((f) => {
          const objUrl = URL.createObjectURL(f)
          ;(reviewForm.rejectImages as any[]).push({ name: f.name, url: objUrl, raw: f })
        })
        // 阻止默认粘贴到输入框
        e.preventDefault()
      }
    } catch {}
  }

  watch(showReviewDialog, (val) => {
    if (val) window.addEventListener('paste', handlePasteToReject)
    else window.removeEventListener('paste', handlePasteToReject)
  })

  // 预览图片
  const previewImage = (url: string) => {
    // 这里可以实现图片预览功能
    console.log('预览图片:', url)
  }

  // 初始化
  onMounted(async () => {
    try {
      console.log('🚀 [TaskReview] 开始初始化任务审核页面')

      // 检查用户权限
      const userStore = useUserStore()

      console.log('🔍 [TaskReview] 检查用户状态:', {
        isLogin: userStore.isLogin,
        hasCurrentUser: !!userStore.currentUser,
        userId: userStore.currentUser?.id,
        userRole: userStore.currentUser?.role
      })

      if (!userStore.isLogin) {
        console.warn('⚠️ [TaskReview] 用户未登录')
        ElMessage.warning('请先登录')
        return
      }

      if (!userStore.currentUser?.id) {
        console.warn('⚠️ [TaskReview] 用户信息缺失')
        ElMessage.warning('用户信息获取中，请稍候...')
        return
      }

      // 统一权限系统已通过路由守卫验证，无需额外检查
      const userRole = userStore.currentUser.role?.toLowerCase()
      console.log('✅ [TaskReview] 用户已通过权限验证，角色:', userRole)

      console.log('👑 [TaskReview] 用户信息:', {
        user: userStore.currentUser,
        role: userRole
      })

      // 并行初始化数据，但不因权限问题而完全阻止
      try {
        await Promise.all([
          fetchProjects().catch((err) => {
            console.error('获取项目列表失败:', err)
            return []
          }),
          fetchUsers().catch((err) => {
            console.error('获取用户列表失败:', err)
            return []
          }),
          fetchTasks().catch((err) => {
            console.error('获取任务列表失败:', err)
            return []
          })
        ])
        // 确保初始也构建一次标注员筛选
        buildAnnotatorList()
      } catch (error) {
        console.error('初始化数据失败:', error)
      }

      console.log('✅ [TaskReview] 任务审核页面初始化完成', {
        projects: projectStore.projects.length,
        users: userList.value.length,
        tasks: projectStore.tasks.length
      })
    } catch (error: any) {
      console.error('❌ [TaskReview] 初始化失败:', error)
      ElMessage.error(`任务审核页面初始化失败: ${error?.message || error}`)
    }
  })

  // 快速按统计卡片筛选
  const quickFilterByStatus = (status: string) => {
    searchForm.status = status
    pagination.page = 1
    fetchTasks()
  }
</script>

<style scoped lang="scss">
  .task-review {
    padding: 10px;
    background: var(--art-bg-color);
    min-height: 100vh;

    // ✅ 头部样式已移至 ArtPageHeader 组件 */

    .stats-section {
      margin-top: 0px;

      .stat-click {
        cursor: pointer;
        transition: transform 0.2s;

        &:hover {
          transform: translateY(-2px);
        }
      }

      .stat-card {
        background: var(--art-main-bg-color);
        border: 1px solid var(--art-card-border);
        border-radius: calc(var(--custom-radius) + 4px);
        padding: 20px;
        display: flex;
        align-items: center;

        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 15px;

          .el-icon {
            font-size: 24px;
            color: white;
          }

          &.pending {
            background: #e6a23c;
          }

          &.approved {
            background: #67c23a;
          }

          &.rejected {
            background: #f56c6c;
          }

          &.total {
            background: #409eff;
          }
        }

        .stat-content {
          flex: 1;

          .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #303133;
            margin-bottom: 5px;
          }

          .stat-label {
            color: #909399;
            font-size: 14px;
          }
        }
      }
    }

    // 任务审核卡片样式
    .task-review-card {
      :deep(.el-card__header) {
        padding: 20px 24px;
        border-bottom: 1px solid var(--el-border-color-lighter);
      }

      // 影像URL单元格样式
      .image-url-cell {
        .image-url-link {
          color: var(--art-primary-color);
          text-decoration: none;
          word-break: break-all;

          &:hover {
            text-decoration: underline;
          }
        }
      }

      .card-header-with-filters {
        display: flex;
        flex-direction: column;
        gap: 16px;

        .header-title {
          display: flex;
          align-items: center;
          gap: 12px;

          .title-text {
            font-size: 16px;
            font-weight: 600;
            color: var(--art-text-gray-900);
          }

          .task-count {
            display: inline-flex;
            align-items: center;
            padding: 2px 10px;
            background: linear-gradient(
              135deg,
              var(--el-color-warning-light-9) 0%,
              var(--el-color-warning-light-8) 100%
            );
            color: var(--el-color-warning);
            font-size: 12px;
            font-weight: 500;
            border-radius: 12px;
          }
        }

        .filters-section {
          display: flex;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;

          .el-button {
            margin-left: auto;

            &:not(:first-of-type) {
              margin-left: 12px;
            }
          }
        }
      }
    }

    .table-section {
      // 任务标题单元格
      .task-title-cell {
        .task-title-text {
          display: block;
          font-weight: 600;
          color: var(--art-text-gray-900);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          cursor: pointer;

          &:hover {
            color: var(--art-primary-color);
          }
        }
      }

      // 项目名称单元格
      :deep(.project-name-cell) {
        display: flex;
        align-items: center;
        gap: 6px;

        .project-icon {
          color: var(--el-color-warning);
          font-size: 16px;
        }

        span.project-name {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      // 可点击的项目名称 hover 效果
      :deep(.project-name-cell .project-name.clickable:hover) {
        color: #409eff !important;
        text-decoration-color: #409eff !important;
      }

      // 标注员单元格
      .annotator-cell {
        .annotator-name {
          display: inline-block;
          padding: 2px 8px;
          background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
          color: #0284c7;
          font-size: 13px;
          font-weight: 500;
          border-radius: 4px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          max-width: 100%;
        }
      }

      // 保留旧样式以防其他地方使用
      .assigned-user {
        display: flex;
        align-items: center;
        gap: 8px;

        .user-avatar {
          background: var(--el-color-primary-light-9);
          color: var(--el-color-primary);
        }

        .user-name {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .task-title {
        display: flex;
        align-items: center;
        gap: 8px;

        .status-tag {
          margin-left: auto;
        }
      }

      .action-buttons {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;

        .status-tag {
          display: flex;
          align-items: center;
          gap: 4px;
          margin-right: 8px;

          .el-icon {
            font-size: 12px;
          }
        }

        .el-button {
          min-width: auto;

          &.el-button--small {
            --el-button-size: 24px;
            font-size: 12px;
            padding: 4px 8px;
          }
        }
      }

      .hours-info {
        font-weight: 500;
      }

      .score-info {
        .el-rate {
          font-size: 14px;
        }
      }

      .no-score {
        color: #c0c4cc;
      }

      .pagination-wrapper {
        margin-top: 20px;
        display: flex;
        justify-content: center;
      }
    }

    .review-container {
      display: flex;
      flex-direction: column;
      gap: 20px;

      .task-info-section,
      .image-section,
      .annotation-section,
      .review-form-section {
        h4 {
          margin: 0 0 15px 0;
          color: #303133;
          font-size: 16px;
          font-weight: 600;
        }
      }

      .image-section {
        .image-viewer {
          border: 1px solid var(--art-card-border);
          border-radius: calc(var(--custom-radius) + 2px);
          padding: 20px;
          text-align: center;
          background: var(--art-main-bg-color);

          .no-image {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            color: #909399;
            padding: 40px;

            .el-icon {
              font-size: 48px;
            }
          }
        }

        .image-gallery {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 15px;
          margin-top: 15px;

          .image-item {
            border: 1px solid #dcdfe6;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            transition: transform 0.2s;

            &:hover {
              transform: scale(1.05);
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }

            img {
              width: 100%;
              height: 150px;
              object-fit: cover;
              display: block;
            }
          }
        }
      }

      .annotation-section {
        .annotation-content {
          border: 1px solid var(--art-card-border);
          border-radius: calc(var(--custom-radius) + 2px);
          background: var(--art-main-bg-color);
        }
      }

      .review-form-section {
        border-top: 1px solid #ebeef5;
        padding-top: 20px;
      }
    }

    .detail-content {
      .rejected-notice,
      .approved-notice {
        margin-bottom: 20px;

        .el-alert {
          border-radius: 8px;
        }
      }

      .task-descriptions {
        margin-top: 10px;
      }

      .review-comment {
        line-height: 1.5;
        padding: 10px;
        background: var(--art-main-bg-color);
        border: 1px solid var(--art-card-border);
        border-radius: calc(var(--custom-radius) + 2px);
        color: var(--art-gray-600);

        &.rejected-comment {
          background: var(--art-main-bg-color);
          border: 1px solid #f56c6c;
          color: #f56c6c;
          font-weight: 500;
        }
      }

      .timeline-section {
        margin-top: 20px;

        h4 {
          margin-bottom: 10px;
          color: var(--art-text-gray-900);
          font-weight: 600;
          font-size: 14px;
        }

        .timeline-wrapper {
          background: var(--art-main-bg-color);
          border-radius: calc(var(--custom-radius) + 4px);
          padding: 0 20px;
          border: 1px solid var(--art-card-border);
          overflow: visible !important;
          position: relative;
        }

        .no-timeline {
          text-align: center;
          padding: 40px 0;
        }
      }
    }

    // 跳过审核对话框样式
    .skip-review-content {
      .skip-reason {
        p {
          margin: 0;
          padding: 12px;
          background: #f8f9fa;
          border-radius: 6px;
          border-left: 4px solid #e6a23c;
          color: #606266;
          line-height: 1.6;
          word-wrap: break-word;
        }
      }

      .skip-images {
        .image-gallery {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 16px;
          margin-top: 12px;

          .image-item {
            display: flex;
            flex-direction: column;
            align-items: center;

            .skip-image {
              width: 200px;
              height: 150px;
              border-radius: 8px;
              cursor: pointer;
              transition: all 0.3s ease;

              &:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
              }
            }

            .image-name {
              margin-top: 8px;
              font-size: 12px;
              color: #909399;
              text-align: center;
              word-break: break-all;
              max-width: 200px;
            }
          }
        }
      }

      .el-radio-group {
        .el-radio {
          margin-right: 24px;
          font-size: 16px;

          .el-radio__label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
          }
        }
      }
    }

    // 提交分组样式
    .image-section {
      .submission-group {
        margin-bottom: 20px;
        border: 1px solid var(--art-card-border);
        border-radius: 10px;
        overflow: hidden;
        background: var(--art-card-bg-color);

        &:last-child {
          margin-bottom: 0;
        }

        // 分组标题
        .group-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 16px;
          background: linear-gradient(
            135deg,
            rgba(var(--art-primary-rgb), 0.08) 0%,
            rgba(var(--art-primary-rgb), 0.03) 100%
          );
          border-bottom: 1px solid var(--art-card-border);

          .group-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            font-size: 14px;
            font-weight: 700;
            color: var(--art-primary-color);
            background: rgba(var(--art-primary-rgb), 0.15);
            border-radius: 14px;

            .badge-icon {
              font-size: 16px;
            }

            .badge-text {
              line-height: 1;
            }
          }

          .group-time {
            font-size: 13px;
            font-weight: 600;
            color: var(--art-text-gray-600);
            font-family: 'Courier New', monospace;
          }
        }

        // 图片网格
        .image-gallery {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
          gap: 12px;
          padding: 16px;

          .image-item {
            position: relative;
            border: 2px solid var(--art-card-border);
            border-radius: 8px;
            overflow: hidden;
            cursor: zoom-in;
            transition: all 0.3s ease;

            &:hover {
              border-color: var(--art-primary-color);
              box-shadow: 0 4px 12px rgba(var(--art-primary-rgb), 0.25);
              transform: translateY(-2px);
            }

            :deep(.el-image) {
              display: block;
              width: 100%;
              height: 100%;
            }
          }
        }

        // 无截图提示
        .no-images {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 32px;
          color: var(--art-text-gray-500);

          .el-icon {
            font-size: 48px;
            margin-bottom: 8px;
            opacity: 0.5;
          }

          span {
            font-size: 14px;
          }
        }
      }
    }
  }
</style>

<style lang="scss">
  // 图片查看器全局样式（修复亮度和显示问题）
  .el-image-viewer__mask {
    background-color: rgba(0, 0, 0, 0.3) !important; // 降低遮罩不透明度，让图片更亮
  }

  // 查看器容器
  .el-image-viewer__wrapper {
    background-color: rgba(0, 0, 0, 0.3) !important;
  }

  // 画布容器 - 允许滚动
  .el-image-viewer__canvas {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: auto !important; // 允许滚动

    img {
      // 确保图片正常显示，不受滤镜影响
      filter: none !important;
      opacity: 1 !important;
      // 允许图片超出容器（缩放后可滚动查看）
      max-width: none !important;
      max-height: none !important;
      // 默认适应屏幕
      width: auto !important;
      height: auto !important;
      // 图片居中
      margin: auto !important;
      display: block !important;
      object-fit: contain !important;
    }
  }

  // 修复图片容器样式
  .el-image-viewer__img {
    // 确保图片显示正常
    filter: none !important;
    opacity: 1 !important;
    // 允许图片超出容器
    max-width: none !important;
    max-height: none !important;
  }

  // 确保图片在缩放后可以滚动查看
  .el-image-viewer__canvas::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  .el-image-viewer__canvas::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
  }

  .el-image-viewer__canvas::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px;

    &:hover {
      background: rgba(255, 255, 255, 0.5);
    }
  }
</style>
