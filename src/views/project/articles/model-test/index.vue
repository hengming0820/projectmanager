<template>
  <div class="model-test-page">
    <el-container class="page-container">
      <!-- 顶部标题栏 -->
      <el-header height="auto" class="page-header-wrapper">
        <ArtPageHeader
          title="模型测试"
          description="沉淀每次阶段性测试的结论与结果"
          icon="🔬"
          badge="Test"
          theme="purple"
        >
          <template #actions>
            <el-button v-if="canManageArticles" @click="showBatchManageDialog = true">
              <el-icon><Setting /></el-icon>
              批量管理
            </el-button>
            <el-button @click="goCreatePage" type="primary">
              <el-icon><Plus /></el-icon>
              发布测试记录
            </el-button>
            <el-button @click="loadArticles">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </template>
        </ArtPageHeader>
      </el-header>

      <!-- 左右布局 -->
      <el-container class="page-body">
        <!-- 左侧导航 -->
        <el-aside width="320px" class="sidebar">
          <div class="nav-panel">
            <div class="filter-section">
              <el-input
                v-model="filterSearch"
                placeholder="搜索测试记录..."
                :prefix-icon="Search"
                clearable
              />
            </div>

            <!-- 导航栏操作按钮 -->
            <div class="nav-actions">
              <el-button
                v-if="canManageArticles"
                @click="showBatchManageDialog = true"
                size="small"
                style="flex: 1"
              >
                <el-icon><Setting /></el-icon>
                批量管理
              </el-button>
              <el-button @click="goCreatePage" type="primary" size="small" style="flex: 1">
                <el-icon><Plus /></el-icon>
                发布
              </el-button>
            </div>

            <el-tree
              ref="treeRef"
              :data="treeData"
              :props="{ label: 'label', children: 'children' }"
              :indent="8"
              :filter-node-method="filterNode"
              :expand-on-click-node="false"
              :default-expanded-keys="expandedKeys"
              :current-node-key="currentArticleId"
              highlight-current
              node-key="key"
              @node-click="onNodeClick"
            >
              <template #default="{ node, data }">
                <div
                  :class="['tree-node', data.isLeaf ? 'tree-leaf' : 'tree-group']"
                  @contextmenu.prevent="data.isLeaf ? handleNodeRightClick($event, data) : null"
                >
                  <!-- 文章图标 -->
                  <el-icon v-if="data.isLeaf" class="node-icon">
                    <Document />
                  </el-icon>

                  <!-- 第一级（部门）和第二级（日期）显示完全，第三级（文章标题）截断 -->
                  <el-tooltip
                    v-if="data.isLeaf"
                    :content="data.label"
                    placement="right"
                    :disabled="data.label.length <= 18"
                    :show-after="300"
                  >
                    <span class="node-label">{{ truncateLabel(data.label, 18) }}</span>
                  </el-tooltip>
                  <span v-else class="node-label">{{ data.label }}</span>
                </div>
              </template>
            </el-tree>
          </div>
        </el-aside>

        <!-- 右侧主内容 -->
        <el-main class="main-col">
          <!-- 文章详情 -->
          <div v-if="currentArticle" class="article-detail-wrapper">
            <el-card class="article-card" shadow="never">
              <template #header>
                <div class="article-header">
                  <div class="header-left">
                    <div class="header-info">
                      <h3>{{ currentArticle.title }}</h3>
                      <span class="meta-info">
                        <el-tag
                          v-if="currentArticle.category"
                          size="small"
                          :color="getCategoryColor(currentArticle.category)"
                          effect="light"
                        >
                          {{ currentArticle.category }}
                        </el-tag>
                        <span class="author-info">
                          <el-icon><User /></el-icon>
                          {{ currentArticle.author_name }}
                        </span>
                        <span class="date-info">
                          <el-icon><Clock /></el-icon>
                          {{ formatDate(currentArticle.updated_at) }}
                        </span>
                        <span class="view-info">
                          <el-icon><View /></el-icon>
                          {{ currentArticle.view_count || 0 }} 次浏览
                        </span>
                      </span>
                    </div>
                  </div>
                  <div class="header-actions">
                    <template v-if="!isEditing">
                      <el-dropdown trigger="click" @command="handleExportCommand">
                        <el-button>
                          <el-icon><Download /></el-icon>
                          导出
                          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item command="html">
                              <el-icon><Document /></el-icon>
                              导出为 HTML
                            </el-dropdown-item>
                            <el-dropdown-item command="pdf">
                              <el-icon><Printer /></el-icon>
                              导出为 PDF
                            </el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                      <el-button @click="openMetaDialog" v-if="canEdit">
                        <el-icon><Edit /></el-icon>
                        编辑信息
                      </el-button>
                      <el-button @click="startEdit" v-if="canEdit">
                        <el-icon><Document /></el-icon>
                        编辑内容
                      </el-button>
                      <el-button @click="showHistoryDrawer">
                        <el-icon><InfoFilled /></el-icon>
                        文章信息
                      </el-button>
                      <el-button type="danger" @click="deleteArticle" v-if="canDelete">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </template>
                    <template v-else>
                      <el-button @click="openImportMarkdown" size="default">
                        <el-icon><Upload /></el-icon>
                        导入 Markdown
                      </el-button>
                      <el-button @click="openImportWord" size="default">
                        <el-icon><Document /></el-icon>
                        导入 Word
                      </el-button>
                      <el-button @click="cancelEdit">取消</el-button>
                      <el-button type="primary" @click="saveEdit" :loading="saving"
                        >保存内容</el-button
                      >
                    </template>
                  </div>
                </div>
              </template>

              <div class="article-content">
                <!-- 查看模式 -->
                <template v-if="!isEditing">
                  <div class="article-body">
                    <ArtXnotePreview :content="currentArticle.content" height="100%" />
                  </div>
                </template>

                <!-- 编辑模式（使用编辑器默认工具栏，不再启用顶部静态工具栏） -->
                <template v-else>
                  <div class="content-editor" :class="{ 'editing-active': isEditing }">
                    <ArtTextbusEditor
                      v-model="editForm.content"
                      height="100%"
                    />
                  </div>
                </template>
              </div>
            </el-card>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <el-empty description="请从左侧选择一条测试记录">
              <el-button type="primary" @click="goCreatePage">
                <el-icon><Plus /></el-icon>
                发布第一条测试记录
              </el-button>
            </el-empty>
          </div>
        </el-main>
      </el-container>
    </el-container>

    <!-- 导入 Markdown 对话框（保持与发布文章页面一致） -->
    <el-dialog 
      v-model="showMdDialog" 
      title="导入 Markdown 文档" 
      width="520px"
      :z-index="10000000"
      :modal="true"
      append-to-body
    >
      <p class="dialog-tip">
        选择一个 .md/.markdown 文件，第一行作为标题，其余内容将转换为正文。
      </p>
      <el-upload
        :auto-upload="false"
        :show-file-list="false"
        accept=".md,.markdown,text/markdown,text/plain"
        :on-change="onMdSelected"
        drag
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">点击或拖拽 Markdown 文件到此处</div>
      </el-upload>
      <div v-if="mdFileName" class="file-selected">
        已选择：<strong>{{ mdFileName }}</strong>
      </div>
      <template #footer>
        <el-button @click="showMdDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 导入 Word 对话框（保持与发布文章页面一致） -->
    <el-dialog 
      v-model="showWordDialog" 
      title="导入 Word 文档" 
      width="520px"
      :z-index="10000000"
      :modal="true"
      append-to-body
    >
      <p class="dialog-tip">
        选择一个 .docx 文件（Word 2007及以上版本），内容将自动转换为HTML格式。
      </p>
      <el-upload
        :auto-upload="false"
        :show-file-list="false"
        accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        :on-change="onWordSelected"
        drag
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">点击或拖拽 Word 文件到此处</div>
      </el-upload>
      <div v-if="wordFileName" class="file-selected">
        已选文件：<strong>{{ wordFileName }}</strong>
      </div>
      <el-alert
        v-if="wordImporting"
        title="正在导入，请稍候..."
        type="info"
        :closable="false"
        style="margin-top: 12px"
      />
      <template #footer>
        <el-button @click="showWordDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 文章信息与历史抽屉 -->
    <el-drawer 
      v-model="historyDrawerVisible" 
      title="文章信息与历史" 
      direction="rtl" 
      size="550px"
      :z-index="10000000"
      :modal="true"
      append-to-body
    >
      <div class="drawer-content">
        <!-- 文章元信息区域 -->
        <div v-if="currentArticle" class="article-meta-section">
          <el-card shadow="never" class="meta-card">
            <template #header>
              <div class="meta-card-header">
                <el-icon><InfoFilled /></el-icon>
                <span>文章元信息</span>
              </div>
            </template>

            <div class="meta-content">
              <!-- 文章简介 -->
              <div v-if="currentArticle.summary" class="meta-item summary-item">
                <div class="meta-label">
                  <el-icon><Document /></el-icon>
                  <span>简介</span>
                </div>
                <div class="meta-value summary-text">
                  {{ currentArticle.summary }}
                </div>
              </div>

              <!-- 可编辑成员 -->
              <div v-if="currentArticle.editable_user_ids?.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><User /></el-icon>
                  <span>可编辑成员</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="userId in currentArticle.editable_user_ids"
                    :key="userId"
                    size="small"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ getUserRealName(userId) }}
                  </el-tag>
                  <span v-if="!currentArticle.editable_user_ids.length" class="empty-text"
                    >未设置</span
                  >
                </div>
              </div>

              <!-- 可编辑角色 -->
              <div v-if="currentArticle.editable_roles?.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><UserFilled /></el-icon>
                  <span>可编辑角色</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="role in currentArticle.editable_roles"
                    :key="role"
                    size="small"
                    type="success"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ getRoleName(role) }}
                  </el-tag>
                  <span v-if="!currentArticle.editable_roles.length" class="empty-text"
                    >未设置</span
                  >
                </div>
              </div>

              <!-- 所属部门 -->
              <div v-if="currentArticle.departments?.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><OfficeBuilding /></el-icon>
                  <span>所属部门</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="dept in currentArticle.departments"
                    :key="dept"
                    size="small"
                    type="warning"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ dept }}
                  </el-tag>
                  <span v-if="!currentArticle.departments.length" class="empty-text">未设置</span>
                </div>
              </div>

              <!-- 标签 -->
              <div v-if="currentArticle.tags && currentArticle.tags.length" class="meta-item">
                <div class="meta-label">
                  <el-icon><PriceTag /></el-icon>
                  <span>标签</span>
                </div>
                <div class="meta-value">
                  <el-tag
                    v-for="tag in currentArticle.tags"
                    :key="tag"
                    size="small"
                    effect="plain"
                    class="meta-tag"
                  >
                    {{ tag }}
                  </el-tag>
                  <span v-if="!currentArticle.tags.length" class="empty-text">未设置</span>
                </div>
              </div>

              <!-- 提示：无元信息 -->
              <el-empty
                v-if="
                  !currentArticle.editable_user_ids?.length &&
                  !currentArticle.editable_roles?.length &&
                  !currentArticle.departments?.length &&
                  (!currentArticle.tags || !currentArticle.tags.length)
                "
                description="暂无文章元信息"
                :image-size="80"
              />
            </div>
          </el-card>
        </div>

        <!-- 编辑历史区域 -->
        <div v-loading="loadingHistory" class="history-section">
          <el-card shadow="never" class="history-card">
            <template #header>
              <div class="history-card-header">
                <el-icon><Clock /></el-icon>
                <span>编辑历史</span>
              </div>
            </template>

            <el-timeline v-if="historyList.length > 0">
              <el-timeline-item
                v-for="item in historyList"
                :key="item.id"
                :timestamp="formatDate(item.created_at)"
                placement="top"
              >
                <div class="history-item">
                  <div class="history-editor">
                    <el-icon><User /></el-icon>
                    <span>{{ item.editor_name }}</span>
                  </div>
                  <div class="history-action">
                    <el-tag :type="getActionTagType(item.action)" size="small">
                      {{ getActionLabel(item.action) }}
                    </el-tag>
                  </div>
                  <div class="history-summary" v-if="item.changes_summary">
                    {{ item.changes_summary }}
                  </div>
                  <div class="history-version" v-if="item.version_after">
                    版本: v{{ item.version_before || 0 }} → v{{ item.version_after }}
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无编辑历史" :image-size="80" />
          </el-card>
        </div>
      </div>
    </el-drawer>

    <!-- 编辑元数据对话框 -->
    <el-dialog
      v-model="showMetaDialog"
      :close-on-click-modal="false"
      width="600px"
      class="meta-dialog"
    >
      <template #header>
        <div class="dialog-header">
          <div class="dialog-icon">
            <el-icon><Edit /></el-icon>
          </div>
          <div class="dialog-title">
            <h3>编辑测试记录信息</h3>
            <p>修改测试记录的标题、分类、标签等元数据</p>
          </div>
        </div>
      </template>

      <el-form :model="metaForm" label-width="90px" class="meta-form">
        <el-form-item label="标题" required>
          <el-input v-model="metaForm.title" placeholder="请输入测试标题" size="large" />
        </el-form-item>

        <el-form-item label="简介">
          <el-input
            v-model="metaForm.summary"
            type="textarea"
            :rows="3"
            placeholder="请输入测试简介"
          />
        </el-form-item>

        <el-form-item label="分类">
          <el-select v-model="metaForm.category" placeholder="选择分类" size="large">
            <el-option label="胸肺" value="胸肺" />
            <el-option label="泌尿" value="泌尿" />
            <el-option label="肝胆" value="肝胆" />
            <el-option label="盆腔" value="盆腔" />
          </el-select>
        </el-form-item>

        <el-form-item label="标签">
          <el-select
            v-model="metaForm.tags"
            multiple
            filterable
            allow-create
            placeholder="添加标签"
            size="large"
            class="tags-select"
          >
            <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>

        <el-form-item label="可编辑角色">
          <el-select
            v-model="metaForm.editable_roles"
            multiple
            filterable
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

        <el-form-item label="可编辑成员">
          <el-select
            v-model="metaForm.editable_user_ids"
            multiple
            filterable
            placeholder="选择人员"
            size="large"
          >
            <el-option v-for="u in userOptions" :key="u.value" :label="u.label" :value="u.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="所属部门">
          <el-select
            v-model="metaForm.departments"
            multiple
            filterable
            placeholder="选择部门"
            size="large"
          >
            <el-option v-for="d in deptOptions" :key="d" :label="d" :value="d" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showMetaDialog = false" size="large">取消</el-button>
          <el-button
            type="primary"
            @click="saveMeta"
            :loading="saving"
            size="large"
            class="save-btn"
          >
            <el-icon v-if="!saving"><Check /></el-icon>
            保存修改
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量管理对话框 -->
    <el-dialog
      v-model="showBatchManageDialog"
      title="批量管理模型测试"
      width="850px"
      :close-on-click-modal="false"
    >
      <div class="batch-manage-container">
        <el-alert type="info" :closable="false" style="margin-bottom: 20px">
          <template #title>
            <div style="display: flex; align-items: center; justify-content: space-between">
              <span
                >已选择 <strong>{{ selectedArticleIds.length }}</strong> 篇文章</span
              >
              <span style="font-size: 13px; color: #909399">支持批量删除、修改部门等操作</span>
            </div>
          </template>
        </el-alert>

        <!-- 筛选区 -->
        <div
          class="batch-filters"
          style="margin-bottom: 16px; display: flex; gap: 12px; flex-wrap: wrap"
        >
          <el-input
            v-model="batchSearchText"
            placeholder="搜索标题..."
            clearable
            style="width: 220px"
            :prefix-icon="Search"
          />
          <el-select
            v-model="batchDeptFilter"
            placeholder="筛选部门"
            clearable
            style="width: 160px"
          >
            <el-option v-for="dept in allDepartments" :key="dept" :label="dept" :value="dept" />
          </el-select>
          <el-select
            v-model="batchCategoryFilter"
            placeholder="筛选分类"
            clearable
            style="width: 160px"
          >
            <el-option label="功能测试" value="功能测试" />
            <el-option label="压力测试" value="压力测试" />
            <el-option label="对比测试" value="对比测试" />
          </el-select>
          <div style="flex: 1"></div>
          <el-button @click="clearBatchFilters" :icon="Refresh">重置</el-button>
        </div>

        <!-- 文章列表 -->
        <div class="batch-article-list">
          <el-checkbox
            v-model="selectAllArticles"
            @change="handleSelectAllArticles"
            style="margin-bottom: 12px; font-weight: 500"
          >
            全选 ({{ filteredArticlesForBatch.length }})
          </el-checkbox>

          <el-scrollbar max-height="450px">
            <el-checkbox-group v-model="selectedArticleIds">
              <div v-for="group in groupedArticlesForBatch" :key="group.label" class="batch-group">
                <div class="batch-group-header">
                  {{ group.label }}
                </div>
                <div v-for="article in group.articles" :key="article.id" class="batch-article-item">
                  <el-checkbox :label="article.id">
                    <div class="article-item-compact">
                      <span class="article-title">{{ article.title }}</span>
                      <div class="article-info">
                        <el-tag v-if="article.category" size="small" effect="plain">
                          {{ article.category }}
                        </el-tag>
                        <el-tag
                          v-for="dept in article.departments || []"
                          :key="dept"
                          size="small"
                          type="info"
                          effect="plain"
                        >
                          {{ dept }}
                        </el-tag>
                        <span class="article-date">{{
                          formatCompactDate(article.created_at)
                        }}</span>
                        <span class="article-author">{{ article.author_name }}</span>
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
              type="danger"
              :disabled="selectedArticleIds.length === 0"
              :loading="batchDeleting"
              @click="batchDeleteArticles"
            >
              删除选中 ({{ selectedArticleIds.length }})
            </el-button>
            <el-button
              type="primary"
              :disabled="selectedArticleIds.length === 0"
              @click="showBatchEditDialog = true"
            >
              批量编辑 ({{ selectedArticleIds.length }})
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 批量编辑对话框 -->
    <el-dialog
      v-model="showBatchEditDialog"
      title="批量编辑文章"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="batchEditForm" label-width="100px">
        <el-form-item label="修改分类">
          <el-select
            v-model="batchEditForm.category"
            placeholder="选择分类（留空则不修改）"
            clearable
          >
            <el-option label="功能测试" value="功能测试" />
            <el-option label="压力测试" value="压力测试" />
            <el-option label="对比测试" value="对比测试" />
          </el-select>
        </el-form-item>
        <el-form-item label="修改部门">
          <el-select
            v-model="batchEditForm.departments"
            multiple
            placeholder="选择部门（留空则不修改）"
            clearable
          >
            <el-option v-for="dept in allDepartments" :key="dept" :label="dept" :value="dept" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBatchEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="batchEditing" @click="batchEditArticles">
          确定修改
        </el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <teleport to="body">
      <div
        v-if="contextMenuVisible"
        class="context-menu"
        :style="{ left: contextMenuPosition.x + 'px', top: contextMenuPosition.y + 'px' }"
        @click.stop
      >
        <div class="menu-item" @click="copyArticleLink">
          <el-icon><Link /></el-icon>
          <span>复制文章链接</span>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    Plus,
    Refresh,
    Search,
    Edit,
    Delete,
    User,
    Clock,
    View,
    Document,
    Check,
    Download,
    ArrowDown,
    Printer,
    Upload,
    UploadFilled,
    Link,
    UserFilled,
    OfficeBuilding,
    Setting,
    PriceTag,
    InfoFilled
  } from '@element-plus/icons-vue'
  import { useUserStore } from '@/store/modules/user'
  import { articlesApi, type Article } from '@/api/articlesApi'
  import { userApi } from '@/api/userApi'
  import { roleApi } from '@/api/roleApi'
  import ArtTextbusEditor from '@/components/core/forms/art-textbus-editor/index.vue'
  import ArtXnotePreview from '@/components/core/forms/art-xnote-preview/index.vue'
  import ArtPageHeader from '@/components/layout/ArtPageHeader.vue'
  import mammoth from 'mammoth'
  import {
    markdownToHtml,
    parseMarkdownFile,
    validateMarkdownFile,
    readMarkdownFile
  } from '@/utils/markdown'

  const router = useRouter()
  const route = useRoute()
  const userStore = useUserStore()

  // 批量管理权限：管理员和审核员可以进行批量管理
  const canManageArticles = computed(() => {
    const role = userStore.currentUser?.role || ''
    return ['admin', 'reviewer'].includes(role)
  })

  // 当前选中的文章
  const currentArticleId = ref<string>('')
  const currentArticle = ref<Article | null>(null)

  // 树形导航数据
  const treeData = ref<any[]>([])
  const expandedKeys = ref<string[]>([])
  const navReady = ref(false)
  const treeRef = ref()
  const filterSearch = ref('')

  // 文章列表数据
  const articles = ref<Article[]>([])
  const loading = ref(false)

  // 批量管理相关
  const showBatchManageDialog = ref(false)
  const showBatchEditDialog = ref(false)
  const selectedArticleIds = ref<string[]>([])
  const selectAllArticles = ref(false)
  const batchSearchText = ref('')
  const batchDeptFilter = ref('')
  const batchCategoryFilter = ref('')
  const batchDeleting = ref(false)
  const batchEditing = ref(false)
  const batchEditForm = ref({
    category: '',
    departments: [] as string[]
  })

  // 编辑模式相关（仅内容）
  const isEditing = ref(false)
  const saving = ref(false)
  const editForm = ref({
    content: ''
  })

  // 右键菜单相关
  const contextMenuVisible = ref(false)
  const contextMenuPosition = ref({ x: 0, y: 0 })
  const rightClickedArticle = ref<any>(null)

  // 元数据编辑对话框
  const showMetaDialog = ref(false)
  const metaForm = ref({
    title: '',
    summary: '',
    category: '',
    tags: [] as string[],
    editable_roles: [] as string[],
    editable_user_ids: [] as string[],
    departments: [] as string[]
  })

  const availableTags = ref<string[]>([
    '性能测试',
    '准确率测试',
    '压力测试',
    'A/B测试',
    '回归测试',
    '集成测试'
  ])

  // 用户、部门和角色选项
  const userOptions = ref<Array<{ label: string; value: string }>>([])
  const deptOptions = ref<string[]>([])
  const roleOptions = ref<Array<{ label: string; value: string }>>([])

  // Markdown 导入相关
  const showMdDialog = ref(false)
  const mdFileName = ref('')

  // Word 导入相关
  const showWordDialog = ref(false)

  // 编辑历史抽屉
  const historyDrawerVisible = ref(false)
  const loadingHistory = ref(false)
  const historyList = ref<any[]>([])
  const wordFileName = ref('')
  const wordImporting = ref(false)

  // 权限判断
  const canEdit = computed(() => {
    if (!currentArticle.value || !userStore.currentUser) return false

    const currentUserId = userStore.currentUser.id
    const currentUserRole = userStore.currentUser.role

    // 1. 管理员可以编辑所有文章
    if (currentUserRole === 'admin') return true

    // 2. 作者可以编辑自己的文章
    if (currentArticle.value.author_id === currentUserId) return true

    // 3. 在可编辑用户列表中
    if (currentArticle.value.editable_user_ids?.includes(currentUserId)) return true

    // 4. 角色在可编辑角色列表中
    if (currentArticle.value.editable_roles?.includes(currentUserRole)) return true

    return false
  })

  const canDelete = computed(() => {
    if (!currentArticle.value || !userStore.currentUser) return false

    const currentUserId = userStore.currentUser.id
    const currentUserRole = userStore.currentUser.role

    // 只有管理员和作者可以删除
    return currentUserRole === 'admin' || currentArticle.value.author_id === currentUserId
  })

  // 加载文章列表
  const loadArticles = async () => {
    try {
      loading.value = true
      const response = await articlesApi.list({ page: 1, page_size: 200, type: 'model_test' })
      articles.value = response.items || []
      buildTree()
    } catch (error) {
      console.error('加载测试记录列表失败:', error)
      ElMessage.error('加载测试记录列表失败')
    } finally {
      loading.value = false
    }
  }

  // 构建树形数据结构（两层：部门 > 日期）
  const buildTree = () => {
    // 按创建时间倒序排序
    const sortedArticles = [...articles.value].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )

    // 第一层：按部门分组
    const departmentGroups: Record<string, any[]> = {}

    sortedArticles.forEach((article) => {
      const departments = article.departments || []

      // 如果文章没有部门，归到"其他"
      if (departments.length === 0) {
        if (!departmentGroups['其他']) {
          departmentGroups['其他'] = []
        }
        departmentGroups['其他'].push(article)
      } else {
        // 文章属于多个部门，在每个部门下都显示
        departments.forEach((dept: string) => {
          if (!departmentGroups[dept]) {
            departmentGroups[dept] = []
          }
          departmentGroups[dept].push(article)
        })
      }
    })

    // 构建两层树结构
    const departmentNames = Object.keys(departmentGroups).sort()
    treeData.value = departmentNames.map((deptName) => {
      const deptArticles = departmentGroups[deptName]

      // 第二层：按日期（年-月）分组
      const monthGroups: Record<string, any[]> = {}

      deptArticles.forEach((article) => {
        const date = new Date(article.created_at)
        const year = date.getFullYear()
        const month = date.getMonth() + 1
        const yearMonth = `${year}年${String(month).padStart(2, '0')}月`

        if (!monthGroups[yearMonth]) {
          monthGroups[yearMonth] = []
        }

        monthGroups[yearMonth].push({
          key: `${deptName}-${article.id}`, // 加上部门前缀确保唯一性
          label: article.title,
          isLeaf: true,
          category: article.category,
          created_at: article.created_at,
          article: article,
          articleId: article.id // 保存原始文章ID
        })
      })

      // 构建月份子节点（按时间倒序）
      const months = Object.keys(monthGroups).sort((a, b) => b.localeCompare(a))
      const monthNodes = months.map((yearMonth) => ({
        key: `${deptName}-${yearMonth}`,
        label: `📅 ${yearMonth}`,
        isDepartmentMonth: true,
        children: monthGroups[yearMonth]
      }))

      return {
        key: `dept-${deptName}`,
        label: `🏢 ${deptName}`,
        isDepartment: true,
        children: monthNodes
      }
    })

    // 默认展开第一个部门和它的前2个月
    if (expandedKeys.value.length === 0 && treeData.value.length > 0) {
      const firstDept = treeData.value[0]
      expandedKeys.value.push(firstDept.key)

      if (firstDept.children && firstDept.children.length > 0) {
        const firstTwoMonths = firstDept.children.slice(0, 2).map((m: any) => m.key)
        expandedKeys.value.push(...firstTwoMonths)
      }
    }

    // 如果还没有选中文章，选中第一个
    if (!currentArticleId.value && articles.value.length > 0) {
      currentArticleId.value = articles.value[0].id
      currentArticle.value = articles.value[0]
    }

    navReady.value = true
  }

  // 树节点点击（支持点击展开）
  const onNodeClick = (node: any) => {
    // 如果是叶子节点（文章），直接选中
    if (node.isLeaf) {
      const articleId = node.articleId || node.key
      // 使用原始文章ID进行匹配
      if (articleId !== currentArticleId.value) {
        currentArticleId.value = articleId
        currentArticle.value = node.article
        isEditing.value = false
      }
      return
    }

    // 如果是分组节点（部门或月份），切换展开/收起
    if (node.isDepartment || node.isDepartmentMonth) {
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

        // 如果是部门节点，自动展开第一个月份
        if (node.isDepartment && node.children && node.children.length > 0) {
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

  // 处理右键点击
  const handleNodeRightClick = (event: MouseEvent, data: any) => {
    if (!data.article) return

    rightClickedArticle.value = data.article
    contextMenuPosition.value = {
      x: event.clientX,
      y: event.clientY
    }
    contextMenuVisible.value = true
  }

  // 复制文章链接
  const copyArticleLink = async () => {
    if (!rightClickedArticle.value) return

    const baseUrl = window.location.origin
    const articleUrl = `${baseUrl}/login#/articles/model-test?articleId=${rightClickedArticle.value.id}`

    try {
      await navigator.clipboard.writeText(articleUrl)
      ElMessage.success('文章链接已复制到剪贴板')
    } catch (error) {
      // 降级方案：使用传统的复制方法
      const textarea = document.createElement('textarea')
      textarea.value = articleUrl
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      try {
        document.execCommand('copy')
        ElMessage.success('文章链接已复制到剪贴板')
      } catch (err) {
        ElMessage.error('复制失败，请手动复制')
      }
      document.body.removeChild(textarea)
    }

    contextMenuVisible.value = false
  }

  // 获取锁定者姓名
  const getLockedByUserName = (userId?: string) => {
    if (!userId || !currentArticle.value) return '其他用户'

    // 1. 检查是否是文章作者
    if (currentArticle.value.author_id === userId) {
      return currentArticle.value.author_name
    }

    // 2. 从用户选项中查找
    const userOption = userOptions.value.find((u) => u.value === userId)
    if (userOption) {
      return userOption.label.split(' (')[0] // 提取真实姓名部分
    }

    // 3. 默认返回
    return '其他用户'
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

  // 分类颜色
  const getCategoryColor = (category?: string) => {
    const map: Record<string, string> = {
      胸肺: '#409eff',
      泌尿: '#67c23a',
      肝胆: '#e6a23c',
      盆腔: '#f56c6c'
    }
    return map[category || ''] || '#909399'
  }

  // 获取分类标签类型（用于Element Plus的tag组件）
  const getCategoryTagType = (category?: string) => {
    if (!category) return 'info' // 默认返回 info，避免空字符串
    const map: Record<string, any> = {
      胸肺: 'primary', // 蓝色
      泌尿: 'success', // 绿色
      肝胆: 'warning', // 橙色
      盆腔: 'danger', // 红色
      骨骼: 'info', // 灰蓝色
      神经: 'info' // 灰蓝色（改为info）
    }
    return map[category] || 'info' // 默认返回 info
  }

  // 截断标签文本
  const truncateLabel = (label: string, maxLength: number = 14) => {
    if (!label) return ''
    if (label.length <= maxLength) return label
    return label.substring(0, maxLength) + '...'
  }

  // 格式化日期
  const formatDate = (date: string) => {
    const d = new Date(date)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  }

  // 格式化紧凑日期（用于批量管理）
  const formatCompactDate = (date: string) => {
    const d = new Date(date)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  // 跳转创建页面
  const goCreatePage = () => {
    router.push({ name: 'ArticleCreate', params: { type: 'model_test' } })
  }

  // 批量管理相关计算属性
  const allDepartments = computed(() => {
    const depts = new Set<string>()
    articles.value.forEach((article) => {
      ;(article.departments || []).forEach((dept: string) => depts.add(dept))
    })
    return Array.from(depts).sort()
  })

  const filteredArticlesForBatch = computed(() => {
    let filtered = [...articles.value]

    // 按搜索文本过滤
    if (batchSearchText.value) {
      const searchLower = batchSearchText.value.toLowerCase()
      filtered = filtered.filter((a) => a.title.toLowerCase().includes(searchLower))
    }

    // 按部门过滤
    if (batchDeptFilter.value) {
      filtered = filtered.filter((a) => (a.departments || []).includes(batchDeptFilter.value))
    }

    // 按分类过滤
    if (batchCategoryFilter.value) {
      filtered = filtered.filter((a) => a.category === batchCategoryFilter.value)
    }

    // 按创建时间倒序排序
    return filtered.sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  })

  const groupedArticlesForBatch = computed(() => {
    const groups: Record<string, any[]> = {}

    filteredArticlesForBatch.value.forEach((article) => {
      const date = new Date(article.created_at)
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      const yearMonth = `${year}年${String(month).padStart(2, '0')}月`

      if (!groups[yearMonth]) {
        groups[yearMonth] = []
      }
      groups[yearMonth].push(article)
    })

    // 按时间倒序排序
    const months = Object.keys(groups).sort((a, b) => b.localeCompare(a))
    return months.map((yearMonth) => ({
      label: yearMonth,
      articles: groups[yearMonth]
    }))
  })

  // 批量管理方法
  const handleSelectAllArticles = () => {
    if (selectAllArticles.value) {
      selectedArticleIds.value = filteredArticlesForBatch.value.map((a) => a.id)
    } else {
      selectedArticleIds.value = []
    }
  }

  const clearBatchFilters = () => {
    batchSearchText.value = ''
    batchDeptFilter.value = ''
    batchCategoryFilter.value = ''
  }

  const batchDeleteArticles = async () => {
    if (selectedArticleIds.value.length === 0) {
      ElMessage.warning('请先选择要删除的文章')
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${selectedArticleIds.value.length} 篇文章吗？此操作不可恢复。`,
        '批量删除确认',
        {
          type: 'warning',
          confirmButtonText: '确定删除',
          cancelButtonText: '取消'
        }
      )

      batchDeleting.value = true

      // 批量删除
      let successCount = 0
      let failCount = 0

      for (const articleId of selectedArticleIds.value) {
        try {
          await articlesApi.remove(articleId)
          successCount++
        } catch (e) {
          console.error(`删除文章 ${articleId} 失败:`, e)
          failCount++
        }
      }

      if (successCount > 0) {
        ElMessage.success(
          `成功删除 ${successCount} 篇文章` + (failCount > 0 ? `，失败 ${failCount} 篇` : '')
        )
        // 重新加载文章列表
        await loadArticles()
        selectedArticleIds.value = []
        selectAllArticles.value = false
        showBatchManageDialog.value = false
      } else {
        ElMessage.error('删除失败')
      }
    } catch (e: any) {
      if (e !== 'cancel') {
        ElMessage.error('删除失败')
      }
    } finally {
      batchDeleting.value = false
    }
  }

  const batchEditArticles = async () => {
    if (selectedArticleIds.value.length === 0) {
      ElMessage.warning('请先选择要编辑的文章')
      return
    }

    if (!batchEditForm.value.category && batchEditForm.value.departments.length === 0) {
      ElMessage.warning('请至少选择一个要修改的字段')
      return
    }

    try {
      batchEditing.value = true

      let successCount = 0
      let failCount = 0

      for (const articleId of selectedArticleIds.value) {
        try {
          const article = articles.value.find((a) => a.id === articleId)
          if (!article) continue

          const updateData: any = {}

          if (batchEditForm.value.category) {
            updateData.category = batchEditForm.value.category
          }

          if (batchEditForm.value.departments.length > 0) {
            updateData.departments = batchEditForm.value.departments
          }

          await articlesApi.update(articleId, updateData)
          successCount++
        } catch (e) {
          console.error(`编辑文章 ${articleId} 失败:`, e)
          failCount++
        }
      }

      if (successCount > 0) {
        ElMessage.success(
          `成功修改 ${successCount} 篇文章` + (failCount > 0 ? `，失败 ${failCount} 篇` : '')
        )
        // 重新加载文章列表
        await loadArticles()
        selectedArticleIds.value = []
        selectAllArticles.value = false
        showBatchEditDialog.value = false
        showBatchManageDialog.value = false
        batchEditForm.value.category = ''
        batchEditForm.value.departments = []
      } else {
        ElMessage.error('修改失败')
      }
    } catch (e) {
      ElMessage.error('修改失败')
    } finally {
      batchEditing.value = false
    }
  }

  // 监听批量管理对话框关闭，清空选中
  watch(
    () => showBatchManageDialog.value,
    (val) => {
      if (!val) {
        selectedArticleIds.value = []
        selectAllArticles.value = false
        batchSearchText.value = ''
        batchDeptFilter.value = ''
        batchCategoryFilter.value = ''
      }
    }
  )

  // 打开元数据编辑对话框
  const openMetaDialog = () => {
    if (!currentArticle.value) return

    const article = currentArticle.value as any
    metaForm.value = {
      title: article.title,
      summary: article.summary || '',
      category: article.category || '',
      tags: article.tags || [],
      editable_roles: article.editable_roles || [],
      editable_user_ids: article.editable_user_ids || [],
      departments: article.departments || []
    }
    showMetaDialog.value = true
  }

  // 保存元数据
  const saveMeta = async () => {
    if (!currentArticle.value || !metaForm.value.title.trim()) {
      ElMessage.warning('标题不能为空')
      return
    }

    try {
      saving.value = true
      await articlesApi.update(currentArticle.value.id, {
        title: metaForm.value.title,
        summary: metaForm.value.summary,
        category: metaForm.value.category,
        tags: metaForm.value.tags,
        editable_roles: metaForm.value.editable_roles,
        editable_user_ids: metaForm.value.editable_user_ids,
        departments: metaForm.value.departments,
        content: currentArticle.value.content, // 保持内容不变
        type: 'model_test'
      } as any)

      ElMessage.success('测试记录信息更新成功')
      showMetaDialog.value = false
      await loadArticles()

      // 重新选中当前文章
      currentArticle.value = articles.value.find((a) => a.id === currentArticle.value!.id) || null
    } catch (error) {
      console.error('更新测试记录信息失败:', error)
      ElMessage.error('更新测试记录信息失败')
    } finally {
      saving.value = false
    }
  }

  // 开始编辑内容
  const startEdit = async () => {
    if (!currentArticle.value) return

    // 先获取当前文章的最新状态（而不是重新加载整个列表）
    try {
      const refreshedArticle = await articlesApi.get(currentArticle.value.id)
      if (refreshedArticle) {
        currentArticle.value = refreshedArticle
        console.log(
          '✅ 文章状态已刷新，is_locked:',
          refreshedArticle.is_locked,
          'locked_by:',
          refreshedArticle.locked_by
        )
      }
    } catch (error) {
      console.error('获取文章最新状态失败:', error)
      // 继续执行，使用缓存的文章数据
    }

    // 检查是否被锁定
    if (
      currentArticle.value.is_locked &&
      currentArticle.value.locked_by !== userStore.currentUser?.id
    ) {
      const lockedByUser = getLockedByUserName(currentArticle.value.locked_by)
      ElMessage.warning({
        message: `文章正被 ${lockedByUser} 编辑中，请稍后再试`,
        duration: 3000
      })
      return
    }

    // 尝试锁定文章
    try {
      await articlesApi.lock(currentArticle.value.id)
      console.log('🔒 [模型测试] 文章已锁定:', currentArticle.value.id)

      editForm.value = {
        content: currentArticle.value.content
      }
      isEditing.value = true

      // 获取文章最新状态以更新锁定状态显示
      try {
        const refreshedArticle = await articlesApi.get(currentArticle.value.id)
        if (refreshedArticle) {
          currentArticle.value = refreshedArticle
        }
      } catch (error) {
        console.error('获取文章最新状态失败:', error)
      }
    } catch (error: any) {
      console.error('锁定文章失败:', error)
      if (error?.status === 423) {
        const lockedByUser = currentArticle.value
          ? getLockedByUserName(currentArticle.value.locked_by)
          : '其他用户'
        ElMessage.warning(`文章正被 ${lockedByUser} 编辑中，请稍后再试`)
      } else {
        ElMessage.error('无法开始编辑，请稍后重试')
      }
    }
  }

  // 取消编辑
  const cancelEdit = async () => {
    if (!currentArticle.value) return

    try {
      // 解锁文章
      await articlesApi.unlock(currentArticle.value.id)
      console.log('🔓 [模型测试] 文章已解锁:', currentArticle.value.id)
    } catch (error) {
      console.error('解锁文章失败:', error)
    }

    isEditing.value = false
    editForm.value = {
      content: ''
    }

    // 获取文章最新状态以更新锁定状态显示
    try {
      const refreshedArticle = await articlesApi.get(currentArticle.value.id)
      if (refreshedArticle) {
        currentArticle.value = refreshedArticle
      }
    } catch (error) {
      console.error('获取文章最新状态失败:', error)
    }
  }

  // 保存编辑内容
  const saveEdit = async () => {
    if (!currentArticle.value || !editForm.value.content.trim()) {
      ElMessage.warning('内容不能为空')
      return
    }

    try {
      saving.value = true

      await articlesApi.update(currentArticle.value.id, {
        content: editForm.value.content,
        // 保持其他字段不变
        title: currentArticle.value.title,
        summary: currentArticle.value.summary,
        category: currentArticle.value.category,
        tags: currentArticle.value.tags,
        type: 'model_test'
      })

      // 解锁文章
      try {
        await articlesApi.unlock(currentArticle.value.id)
        console.log('🔓 [模型测试] 文章已解锁（保存后）:', currentArticle.value.id)
      } catch (error) {
        console.error('解锁文章失败:', error)
      }

      ElMessage.success('测试记录内容更新成功')
      isEditing.value = false
      
      // 获取文章最新状态
      try {
        const refreshedArticle = await articlesApi.get(currentArticle.value.id)
        if (refreshedArticle) {
          currentArticle.value = refreshedArticle
        }
      } catch (error) {
        console.error('获取文章最新状态失败:', error)
      }
    } catch (error) {
      console.error('保存测试记录失败:', error)
      ElMessage.error('保存测试记录失败')
    } finally {
      saving.value = false
    }
  }

  // 删除文章
  const deleteArticle = async () => {
    if (!currentArticle.value) return

    try {
      await ElMessageBox.confirm('确定要删除这条测试记录吗？', '确认删除', {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      })

      await articlesApi.remove(currentArticle.value.id)
      ElMessage.success('测试记录已删除')

      currentArticleId.value = ''
      currentArticle.value = null
      await loadArticles()
    } catch (error: any) {
      if (error !== 'cancel') {
        console.error('删除测试记录失败:', error)
        ElMessage.error('删除测试记录失败')
      }
    }
  }

  // 显示编辑历史抽屉
  const showHistoryDrawer = async () => {
    if (!currentArticle.value) return

    historyDrawerVisible.value = true
    loadingHistory.value = true

    try {
      const history = await articlesApi.history(currentArticle.value.id)
      historyList.value = history
    } catch (error) {
      console.error('获取编辑历史失败:', error)
      ElMessage.error('获取编辑历史失败')
    } finally {
      loadingHistory.value = false
    }
  }

  // 获取操作类型对应的标签类型
  const getActionTagType = (action: string) => {
    const typeMap: Record<string, any> = {
      create: 'success',
      update: 'primary',
      delete: 'danger'
    }
    return typeMap[action] || 'info'
  }

  // 获取操作类型的文本
  const getActionLabel = (action: string) => {
    const labelMap: Record<string, string> = {
      create: '创建',
      update: '更新',
      delete: '删除'
    }
    return labelMap[action] || action
  }

  // 打开导入 Markdown 对话框
  const openImportMarkdown = () => {
    showMdDialog.value = true
    mdFileName.value = ''
  }

  // Markdown 文件选择处理
  const onMdSelected = async (file: any) => {
    try {
      const raw: File = file?.raw || file
      if (!raw) return

      mdFileName.value = raw.name

      // 验证文件
      const validation = validateMarkdownFile(raw)
      if (!validation.valid) {
        ElMessage.warning(validation.error || 'Markdown 文件无效')
        return
      }

      // 读取文件内容
      const content = await readMarkdownFile(raw)

      if (!content.trim()) {
        ElMessage.warning('Markdown 文件内容为空')
        return
      }

      // 转换 Markdown 为 HTML
      const html = markdownToHtml(content, {
        gfm: true,
        openLinksInNewWindow: true,
        sanitize: true
      })

      editForm.value.content = html
      showMdDialog.value = false
      ElMessage.success('Markdown 文档已导入')
    } catch (e: any) {
      console.error('Markdown 导入失败:', e)
      ElMessage.error(`Markdown 导入失败: ${e.message || '未知错误'}`)
    }
  }

  // 打开导入 Word 对话框
  const openImportWord = () => {
    showWordDialog.value = true
    wordFileName.value = ''
    wordImporting.value = false
  }

  // Word 文件选择处理
  const onWordSelected = async (file: any) => {
    try {
      const raw: File = file?.raw || file
      if (!raw) return

      wordFileName.value = raw.name
      wordImporting.value = true

      // 使用 mammoth 将 docx 转换为 HTML
      const arrayBuffer = await raw.arrayBuffer()
      const result = await mammoth.convertToHtml({ arrayBuffer })

      if (result.value) {
        editForm.value.content = result.value
        showWordDialog.value = false
        ElMessage.success('Word 文档已导入')

        // 如果有警告信息，显示给用户
        if (result.messages && result.messages.length > 0) {
          const warnings = result.messages.filter((m: any) => m.type === 'warning')
          if (warnings.length > 0) {
            console.warn('Word导入警告:', warnings)
          }
        }
      } else {
        ElMessage.warning('Word 文档内容为空')
      }
    } catch (e: any) {
      console.error('Word 导入失败:', e)
      ElMessage.error(`Word 导入失败: ${e.message || '未知错误'}`)
    } finally {
      wordImporting.value = false
    }
  }

  // 导出命令处理
  const handleExportCommand = (command: string) => {
    if (command === 'html') {
      exportHtml()
    } else if (command === 'pdf') {
      exportPdf()
    }
  }

  // 导出为 HTML
  const exportHtml = () => {
    if (!currentArticle.value) return
    const title = (currentArticle.value.title || 'article').replace(/[/\\:*?"<>|]/g, '_')
    const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${escapeHtml(title)}</title>
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial; margin:24px; color:#111827;}
    h1,h2,h3{margin-top:18px}
    p{line-height:1.8;margin:10px 0}
    img{max-width:100%;height:auto;border-radius:4px}
    blockquote{border-left:4px solid #e5e7eb;background:#f9fafb;padding:10px 12px;color:#374151}
    pre{background:#0b1020;color:#e5e7eb;padding:12px 14px;border-radius:6px;overflow:auto}
    code{background:#f3f4f6;padding:2px 6px;border-radius:4px}
    table{width:100%;border-collapse:collapse;margin:10px 0}
    th,td{border:1px solid #e5e7eb;padding:8px 10px;text-align:left}
  </style>
</head>
<body>
  <h1>${escapeHtml(currentArticle.value.title || '')}</h1>
  ${currentArticle.value.summary ? `<p>${escapeHtml(currentArticle.value.summary)}</p>` : ''}
  <div>${currentArticle.value.content || ''}</div>
</body>
</html>`
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('HTML 导出成功')
  }

  // HTML 转义函数
  function escapeHtml(s: string) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
  }

  // 导出为 PDF（通过浏览器打印）
  const exportPdf = () => {
    if (!currentArticle.value) return

    const title = currentArticle.value.title || 'article'

    // 获取当前日期
    const now = new Date()
    const dateStr = `${now.getFullYear()}年${String(now.getMonth() + 1).padStart(2, '0')}月${String(now.getDate()).padStart(2, '0')}日`

    const html = `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8" />
  <title>${escapeHtml(title)}</title>
  <style>
    @page { 
      size: A4; 
      margin: 12mm 12mm;
    }
    * {
      box-sizing: border-box;
    }
    body {
      font-family: "Microsoft YaHei", "微软雅黑", system-ui, -apple-system, sans-serif;
      color: #111827;
      margin: 0;
      padding: 0;
      position: relative;
    }
    /* 页眉样式 - 固定在顶部 */
    .page-header {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 0mm;
      border-bottom: 0.5pt solid #d1d5db;
      font-size: 9pt;
      color: #6b7280;
      background: white;
      z-index: 1000;
    }
    .page-header .company-name {
      font-weight: 600;
      color: #374151;
    }
    /* 页脚样式 - 固定在底部 */
    .page-footer {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 0mm;
      border-top: 0.5pt solid #d1d5db;
      font-size: 9pt;
      color: #6b7280;
      background: white;
      z-index: 1000;
    }
    .page-footer .company-name {
      color: #374151;
    }
    /* 内容区域 - 留出页眉页脚空间 */
    .page-content {
      margin-top: 40px;
      margin-bottom: 40px;
      padding: 0;
    }
    h1, h2, h3 { margin-top: 18px; }
    h1 { font-size: 24px; margin-bottom: 12px; }
    p { line-height: 1.8; margin: 10px 0; }
    img { max-width: 100%; height: auto; border-radius: 4px; }
    blockquote { border-left: 4px solid #e5e7eb; background: #f9fafb; padding: 10px 12px; color: #374151; margin: 10px 0; }
    pre { background: #0b1020; color: #e5e7eb; padding: 12px 14px; border-radius: 6px; overflow: auto; margin: 10px 0; }
    code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; }
    table { width: 100%; border-collapse: collapse; margin: 10px 0; }
    th, td { border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; }
    th { background: #f9fafb; font-weight: 600; }
  </style></head><body>
  <!-- 页眉 -->
  <div class="page-header">
    <span>${dateStr}</span>
    <span class="company-name">星像精准医疗科技（成都）有限公司</span>
  </div>
  
  <!-- 页脚 -->
  <div class="page-footer">
    <span class="company-name">星像精准医疗科技（成都）有限公司</span>
    <span class="page-number"></span>
  </div>
  
  <!-- 内容区域 -->
  <div class="page-content">
    <h1>${escapeHtml(currentArticle.value.title || '')}</h1>
    ${currentArticle.value.summary ? `<p><strong>摘要：</strong>${escapeHtml(currentArticle.value.summary)}</p>` : ''}
    <div>${currentArticle.value.content || ''}</div>
  </div>
  
  <script>
    // 自动添加页码
    window.onload = function() {
      var pageNumbers = document.querySelectorAll('.page-number');
      pageNumbers.forEach(function(el) {
        el.textContent = '第 ' + '1' + ' 页';
      });
      // 延迟打开打印对话框
      setTimeout(function() { 
        window.print(); 
      }, 300);
    };
  <\/script>
  </body></html>`

    const win = window.open('', '_blank')
    if (!win) {
      ElMessage.warning('无法打开新窗口，请检查浏览器弹窗拦截设置')
      return
    }
    win.document.open()
    win.document.write(html)
    win.document.close()
  }

  // 加载用户、部门和角色选项
  const loadUsersAndDepts = async () => {
    try {
      // 使用 getUsersBasic API（所有用户可访问）
      const res: any = await userApi.getUsersBasic({ status: 'active', size: 9999 })
      // 后端返回格式: {code: 200, msg: "成功", data: {list: [...], total: N}} 或 {data: {users: [...], total: N}}
      // 兼容两种字段名: list (旧) 和 users (新)
      const list: any[] = res?.data?.users || res?.data?.list || []
      userOptions.value = list.map((u) => ({
        label: `${u.real_name || u.username} (${u.username})`,
        value: u.id
      }))
      const sets = new Set<string>()
      list.forEach((u) => {
        if (u.department) sets.add(u.department)
      })
      deptOptions.value = Array.from(sets)

      // 获取角色列表（所有登录用户都可以访问）
      try {
        const roleRes: any = await roleApi.getRoles({ size: 9999 })
        const roleList: any[] = roleRes?.data?.list || roleRes?.data?.roles || []
        roleOptions.value = roleList.map((r) => ({
          label: r.name, // 中文显示名称
          value: r.role // 英文角色编码
        }))
      } catch (roleError) {
        console.error('[模型测试] 加载角色列表失败:', roleError)
        roleOptions.value = []
      }
    } catch (e) {
      userOptions.value = []
      deptOptions.value = []
      roleOptions.value = []
    }
  }

  // 根据角色名称获取显示名称
  const getRoleName = (role: string) => {
    const roleOption = roleOptions.value.find((r) => r.value === role)
    return roleOption?.label || role
  }

  // 根据用户ID获取真实姓名
  const getUserRealName = (userId: string) => {
    if (!userId) return '未知用户'

    // 先从 userOptions 中查找
    const userOption = userOptions.value.find((u) => u.value === userId)
    if (userOption) {
      // userOption.label 格式是 "真实姓名 (username)"
      const realName = userOption.label.split(' (')[0]
      return realName || userOption.label
    }

    // 如果是当前文章作者
    if (currentArticle.value && currentArticle.value.author_id === userId) {
      return currentArticle.value.author_name
    }

    // 如果是当前用户
    if (userStore.currentUser && userStore.currentUser.id === userId) {
      return userStore.currentUser.realName || userStore.currentUser.username
    }

    // 默认返回ID（当用户数据尚未加载时）
    console.warn(
      '[getUserRealName] 未找到用户信息:',
      userId,
      'userOptions长度:',
      userOptions.value.length
    )
    return userId
  }

  // 获取用户名称
  const getUserName = (userId: string) => {
    const user = userOptions.value.find((u) => u.value === userId)
    return user ? user.label : userId
  }

  onMounted(async () => {
    // 先加载用户数据，确保在显示文章前已经有用户信息
    await loadUsersAndDepts()
    await loadArticles()

    // 检查URL参数，如果有 articleId，自动跳转到该文章
    const articleIdFromUrl = route.query.articleId as string
    if (articleIdFromUrl && articles.value.length > 0) {
      const targetArticle = articles.value.find((a) => a.id === articleIdFromUrl)
      if (targetArticle) {
        currentArticleId.value = targetArticle.id
        currentArticle.value = targetArticle
        ElMessage.success(`已定位到文章：${targetArticle.title}`)

        // 清除URL参数
        router.replace({ query: {} })
      }
    }

    // 添加全局点击事件，用于关闭右键菜单
    document.addEventListener('click', () => {
      if (contextMenuVisible.value) {
        contextMenuVisible.value = false
      }
    })

    // 监听页面关闭事件
    window.addEventListener('beforeunload', handleBeforeUnload)
  })

  // 页面关闭前的清理函数
  const handleBeforeUnload = (event: BeforeUnloadEvent) => {
    if (isEditing.value && currentArticle.value) {
      // 尝试使用 sendBeacon（异步，不阻塞页面关闭）
      const apiUrl = `/api/articles/${currentArticle.value.id}/unlock`
      const token = localStorage.getItem('token') || sessionStorage.getItem('token')

      if (navigator.sendBeacon) {
        const blob = new Blob([JSON.stringify({})], { type: 'application/json' })
        const headers = token ? { Authorization: `Bearer ${token}` } : {}
        navigator.sendBeacon(apiUrl, blob)
        console.log('🔓 [模型测试] 使用 sendBeacon 解锁文章')
      } else {
        // 降级方案：同步 XHR（会阻塞，但更可靠）
        const xhr = new XMLHttpRequest()
        xhr.open('POST', apiUrl, false) // 同步请求
        if (token) {
          xhr.setRequestHeader('Authorization', `Bearer ${token}`)
        }
        xhr.setRequestHeader('Content-Type', 'application/json')
        xhr.send(JSON.stringify({}))
        console.log('🔓 [模型测试] 使用同步 XHR 解锁文章')
      }
    }
  }

  // 组件卸载前解锁
  onBeforeUnmount(async () => {
    // 移除 beforeunload 监听器
    window.removeEventListener('beforeunload', handleBeforeUnload)

    // 如果正在编辑，尝试解锁
    if (isEditing.value && currentArticle.value) {
      try {
        await articlesApi.unlock(currentArticle.value.id)
        console.log('🔓 [模型测试] 组件卸载时已解锁文章')
      } catch (error) {
        console.error('组件卸载时解锁文章失败:', error)
      }
    }
  })

  // 监听路由变化，支持动态跳转到文章
  watch(
    () => route.query.articleId,
    async (newArticleId) => {
      if (newArticleId && typeof newArticleId === 'string') {
        // 如果文章列表还没加载，先加载
        if (articles.value.length === 0) {
          await loadArticles()
        }

        const targetArticle = articles.value.find((a) => a.id === newArticleId)
        if (targetArticle) {
          currentArticleId.value = targetArticle.id
          currentArticle.value = targetArticle
          ElMessage.success(`已定位到文章：${targetArticle.title}`)

          // 清除URL参数
          router.replace({ query: {} })
        } else {
          ElMessage.warning('未找到指定的文章')
        }
      }
    }
  )
</script>

<style scoped lang="scss">
  .model-test-page {
    background: var(--art-bg-color);
    height: 100vh;
    overflow: hidden;

    .page-container {
      display: flex !important;
      flex-direction: column !important;
      height: 100% !important;
      padding: 10px;
      box-sizing: border-box;
      position: relative; /* 确保 z-index 生效 */
      z-index: 1; /* 设置较低的 z-index，确保抽屉遮罩层能覆盖 */
    }

    .page-header-wrapper {
      flex-shrink: 0;
      height: auto !important;
      padding: 0 !important;
      margin-bottom: 10px;
    }

    .page-body {
      flex: 0.95 !important;
      min-height: 0 !important;
      overflow: hidden !important;
      gap: 16px;
      height: auto !important;

      .sidebar {
        padding: 0;
        background: transparent;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        min-height: 0;
        position: relative; /* 确保 z-index 生效 */
        z-index: 1; /* 设置较低的 z-index，确保抽屉遮罩层能覆盖 */

        .nav-panel {
          padding: 16px;
          background: var(--art-main-bg-color);
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
          flex: 1;
          overflow-y: auto;
          overflow-x: hidden;

          // 美化滚动条
          &::-webkit-scrollbar {
            width: 6px;
          }

          &::-webkit-scrollbar-track {
            background: var(--art-bg-color);
            border-radius: 3px;
          }

          &::-webkit-scrollbar-thumb {
            background: var(--art-gray-400);
            border-radius: 3px;

            &:hover {
              background: var(--art-gray-500);
            }
          }
        }

        .filter-section {
          margin-bottom: 12px;

          :deep(.el-input__wrapper) {
            border-radius: 8px;
            box-shadow: 0 0 0 1px #e5e7eb inset;
            transition: all 0.2s;

            &:hover {
              box-shadow: 0 0 0 1px #9ca3af inset;
            }

            &.is-focus {
              box-shadow: 0 0 0 1px #3b82f6 inset;
            }
          }
        }

        .nav-actions {
          display: flex;
          gap: 8px;
          margin-bottom: 16px;

          .el-button {
            border-radius: 6px;
            font-size: 13px;
            height: 32px;

            .el-icon {
              font-size: 14px;
            }
          }
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

              &:hover {
                background: var(--art-bg-color);
              }
            }

            &.is-current > .el-tree-node__content {
              background: linear-gradient(
                90deg,
                rgba(102, 126, 234, 0.15) 0%,
                rgba(118, 75, 162, 0.08) 100%
              );
              border-left: 3px solid #3b82f6;
              padding-left: 5px !important;
              box-shadow: 0 1px 3px rgba(102, 126, 234, 0.1);
              font-weight: 600;

              .tree-node {
                color: #3b82f6;

                .node-icon {
                  color: #3b82f6;
                  transform: scale(1.1);
                }

                .node-label {
                  color: #3b82f6;
                  font-weight: 600;
                }
              }
            }
          }

          // 调整缩进大小，适应三层结构
          .el-tree-node__children {
            .el-tree-node__content {
              padding-left: 18px !important;
            }

            .el-tree-node__children {
              .el-tree-node__content {
                padding-left: 20px !important;
              }
            }
          }

          .el-tree-node__expand-icon {
            font-size: 14px;
            color: var(--art-text-gray-600);
            margin-right: 4px;

            &.is-leaf {
              color: transparent;
            }
          }
        }

        .tree-node {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 8px;

          .node-icon {
            flex-shrink: 0;
            font-size: 14px;
            color: var(--art-text-gray-600);
            transition: all 0.2s;
          }

          .node-label {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 13px;
            line-height: 1.5;
            text-align: left;
            min-width: 0;
          }
        }

        .tree-group {
          font-weight: 600;
          color: var(--art-text-gray-800);
          user-select: none;
        }
      }

      .main-col {
        display: flex;
        flex-direction: column;
        overflow: hidden;
        padding: 0;
        flex: 1;
        min-height: 0;

        .article-detail-wrapper {
          flex: 1;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          min-height: 0;

          .article-card {
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 0;

            :deep(.el-card__header) {
              padding: 20px 24px;
              background: var(--art-main-bg-color);
              border-bottom: 1px solid var(--art-card-border);
              flex-shrink: 0;
            }

            :deep(.el-card__body) {
              padding: 0;
              flex: 1;
              overflow: hidden;
              display: flex;
              flex-direction: column;
            }
          }

          .article-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 20px;

            .header-left {
              flex: 1;
              min-width: 0;

              .header-info {
                h3 {
                  margin: 0 0 12px 0;
                  font-size: 20px;
                  font-weight: 600;
                  color: var(--art-text-gray-900);
                  line-height: 1.4;
                }

                .meta-info {
                  display: flex;
                  flex-wrap: wrap;
                  gap: 12px;
                  align-items: center;
                  font-size: 13px;
                  color: var(--art-text-gray-600);

                  .author-info,
                  .date-info,
                  .view-info {
                    display: flex;
                    align-items: center;
                    gap: 4px;

                    .el-icon {
                      font-size: 14px;
                    }
                  }
                }

                // 可编辑成员和所属部门样式（参照协作文档）
                .article-collaborators {
                  margin-top: 8px;

                  .collaborators-inline {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    margin-top: 6px;
                    flex-wrap: wrap;

                    .collaborators-label {
                      display: flex;
                      align-items: center;
                      gap: 4px;
                      color: var(--art-text-gray-600);
                      font-size: 13px;
                      font-weight: 500;
                      min-width: auto;
                    }

                    .collaborator-tag-inline {
                      display: inline-flex;
                      align-items: center;
                      gap: 4px;
                      border-radius: 12px;
                      padding: 2px 10px;
                      font-size: 12px;
                      transition: all 0.3s ease;
                    }
                  }
                }
              }
            }

            .header-actions {
              display: flex;
              gap: 8px;
              flex-shrink: 0;

              .el-button {
                border-radius: 6px;
                font-weight: 500;

                .el-icon {
                  font-size: 14px;
                }
              }
            }
          }

          .article-content {
            padding: 24px;
            flex: 1;
            overflow-y: auto;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;

            // 自定义滚动条
            &::-webkit-scrollbar {
              width: 8px;
            }
            &::-webkit-scrollbar-track {
              background: var(--art-bg-color);
              border-radius: 4px;
            }
            &::-webkit-scrollbar-thumb {
              background: var(--art-gray-400);
              border-radius: 4px;

              &:hover {
                background: var(--art-gray-500);
              }
            }

            h4 {
              margin: 0 0 12px 0;
              color: var(--art-text-gray-800);
              font-size: 15px;
              font-weight: 600;
              display: flex;
              align-items: center;
              gap: 6px;
            }

            .article-body {
              flex: 1;
              min-height: 0;
              display: flex;
              flex-direction: column;

              .content-html {
                color: var(--art-text-gray-800);
                line-height: 1.8;

                :deep(img) {
                  max-width: 100%;
                  height: auto;
                  border-radius: 8px;
                  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                  margin: 12px 0;
                }

                :deep(p) {
                  margin: 12px 0;
                  color: var(--art-text-gray-800);
                }

                :deep(h1),
                :deep(h2),
                :deep(h3),
                :deep(h4),
                :deep(h5),
                :deep(h6) {
                  margin: 20px 0 12px 0;
                  font-weight: 600;
                  color: var(--art-text-gray-900);
                }

                :deep(ul),
                :deep(ol) {
                  margin: 12px 0;
                  padding-left: 24px;
                  color: var(--art-text-gray-800);
                }

                :deep(li) {
                  margin: 6px 0;
                  color: var(--art-text-gray-800);
                }

                :deep(code) {
                  padding: 2px 6px;
                  background: var(--art-bg-color);
                  border-radius: 4px;
                  font-family: 'Courier New', monospace;
                  font-size: 0.9em;
                  color: var(--art-primary-color);
                }

                :deep(pre) {
                  padding: 16px;
                  background: rgba(var(--art-gray-800-rgb, 31, 41, 55), 0.95);
                  border-radius: 8px;
                  overflow-x: auto;
                  margin: 16px 0;

                  code {
                    color: var(--art-text-gray-100);
                    background: transparent;
                    padding: 0;
                  }
                }
              }
            }

            .article-tags,
            .article-permissions {
              padding-top: 16px;
              border-top: 1px solid var(--art-card-border);
              margin-top: 16px;

              h4 {
                margin: 0 0 12px 0;
                color: var(--art-text-gray-800);
                font-size: 15px;
                font-weight: 600;
              }

              .tags-list,
              .permissions-list {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;

                .el-tag {
                  border-radius: 6px;
                }
              }
            }

            // 编辑模式的编辑器样式
            .content-editor {
              flex: 1;
              display: flex;
              flex-direction: column;
              background: var(--art-main-bg-color);
              min-height: 0;
              overflow: hidden; // Keep overflow hidden for the editor container
            }

            // 当存在编辑器时，禁用article-content的滚动并去除padding
            &:has(.content-editor.editing-active) {
              padding: 0;
              overflow: hidden;
            }
          }
        }

        .empty-state {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;

          :deep(.el-empty) {
            padding: 60px 0;

            .el-empty__image {
              width: 200px;
            }

            .el-empty__description {
              margin-top: 20px;
              font-size: 15px;
              color: var(--art-text-gray-600);
            }
          }
        }
      }
    }
  }

  /* 导入对话框样式（与发布文章页面保持一致） */
  .dialog-tip {
    color: var(--art-text-gray-600);
    margin-bottom: 16px;
    font-size: 14px;
    line-height: 1.6;
  }

  .upload-icon {
    font-size: 48px;
    color: #409eff;
    margin-bottom: 12px;
  }

  .upload-text {
    font-size: 14px;
    color: var(--art-text-gray-600);
  }

  .file-selected {
    margin-top: 16px;
    padding: 12px;
    background: var(--art-bg-color);
    border-radius: 6px;
    font-size: 13px;
    color: var(--art-text-gray-700);

    strong {
      color: var(--art-text-gray-900);
    }
  }

  // 文章信息与历史抽屉样式
  .drawer-content {
    padding: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 20px;

    // 文章元信息区域
    .article-meta-section {
      .meta-card {
        border: 1px solid var(--el-border-color-lighter) !important;
        border-radius: 8px;
        overflow: hidden;

        :deep(.el-card__header) {
          padding: 16px 20px;
          background: var(--el-fill-color-light);
          border-bottom: 1px solid var(--el-border-color-lighter);

          .meta-card-header {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--art-text-gray-900);
            font-weight: 600;
            font-size: 15px;

            .el-icon {
              font-size: 18px;
              color: var(--el-color-primary);
            }
          }
        }

        :deep(.el-card__body) {
          padding: 20px;
        }
      }

      .meta-content {
        .meta-item {
          margin-bottom: 20px;

          &:last-child {
            margin-bottom: 0;
          }

          .meta-label {
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
            color: var(--art-text-gray-900);
            margin-bottom: 10px;
            font-size: 14px;

            .el-icon {
              color: #3b82f6;
              font-size: 16px;
            }
          }

          .meta-value {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding-left: 22px;

            .meta-tag {
              margin: 0;
            }

            .empty-text {
              color: var(--art-text-gray-400);
              font-size: 13px;
              font-style: italic;
            }
          }
        }
      }
    }

    // 编辑历史区域
    .history-section {
      flex: 1;
      min-height: 0;

      .history-card {
        border: 1px solid var(--el-border-color-lighter) !important;
        border-radius: 8px;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;

        :deep(.el-card__header) {
          padding: 16px 20px;
          background: var(--el-fill-color-light);
          border-bottom: 1px solid var(--el-border-color-lighter);

          .history-card-header {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--art-text-gray-900);
            font-weight: 600;
            font-size: 15px;

            .el-icon {
              font-size: 18px;
              color: var(--el-color-primary);
            }
          }
        }

        :deep(.el-card__body) {
          padding: 20px;
          flex: 1;
          overflow-y: auto;
        }
      }

      .history-item {
        padding: 16px;
        background: var(--art-bg-color);
        border-radius: 8px;
        margin-bottom: 16px;
        border: 1px solid var(--el-border-color-lighter);
        transition: all 0.3s ease;

        &:hover {
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          border-color: var(--el-color-primary-light-7);
        }

        .history-editor {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 600;
          color: var(--art-text-gray-900);
          margin-bottom: 8px;

          .el-icon {
            color: #3b82f6;
          }
        }

        .history-action {
          margin-bottom: 8px;
        }

        .history-summary {
          color: var(--art-text-gray-600);
          font-size: 14px;
          margin-bottom: 8px;
          line-height: 1.6;
        }

        .history-version {
          font-size: 13px;
          color: var(--art-text-gray-500);
          font-family: monospace;
          background: var(--el-fill-color-light);
          padding: 4px 8px;
          border-radius: 4px;
          display: inline-block;
        }
      }
    }
  }

  // 元数据编辑对话框样式
  .meta-dialog {
    :deep(.el-dialog__header) {
      padding: 0;
      margin: 0;
      border-bottom: 1px solid #e5e7eb;
    }

    .dialog-header {
      display: flex;
      align-items: flex-start;
      gap: 16px;
      padding: 24px 24px 20px 24px;

      .dialog-icon {
        flex-shrink: 0;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);

        .el-icon {
          font-size: 24px;
          color: white;
        }
      }

      .dialog-title {
        flex: 1;

        h3 {
          margin: 0 0 6px 0;
          font-size: 20px;
          font-weight: 600;
          color: #111827;
          letter-spacing: 0.3px;
        }

        p {
          margin: 0;
          font-size: 13px;
          color: #6b7280;
          line-height: 1.5;
        }
      }
    }

    :deep(.el-dialog__body) {
      padding: 28px 24px;
    }

    .meta-form {
      :deep(.el-form-item) {
        margin-bottom: 24px;

        &:last-child {
          margin-bottom: 0;
        }
      }

      :deep(.el-form-item__label) {
        font-weight: 600;
        color: #374151;
        font-size: 14px;
        line-height: 32px;
      }

      :deep(.el-input__wrapper) {
        box-shadow: 0 0 0 1px #d1d5db inset;
        transition: all 0.2s;

        &:hover {
          box-shadow: 0 0 0 1px #9ca3af inset;
        }

        &.is-focus {
          box-shadow: 0 0 0 1px #3b82f6 inset;
        }
      }

      :deep(.el-textarea__inner) {
        box-shadow: 0 0 0 1px #d1d5db inset;
        transition: all 0.2s;

        &:hover {
          box-shadow: 0 0 0 1px #9ca3af inset;
        }

        &:focus {
          box-shadow: 0 0 0 1px #3b82f6 inset;
        }
      }

      .tags-select {
        width: 100%;

        :deep(.el-select__tags) {
          max-height: 120px;
          overflow-y: auto;
        }
      }
    }

    :deep(.el-dialog__footer) {
      padding: 16px 24px 24px 24px;
      border-top: 1px solid #e5e7eb;
    }

    .dialog-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;

      .el-button {
        min-width: 100px;
        font-weight: 500;
        border-radius: 8px;
        transition: all 0.2s;

        &:not(.save-btn) {
          border-color: #d1d5db;
          color: #6b7280;

          &:hover {
            border-color: #9ca3af;
            color: var(--art-text-gray-800);
            background: var(--art-bg-color);
          }
        }
      }

      .save-btn {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);

        &:hover {
          box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
          transform: translateY(-1px);
        }

        &:active {
          transform: translateY(0);
        }

        .el-icon {
          margin-right: 4px;
        }
      }
    }
  }

  // 右键菜单样式
  .context-menu {
    position: fixed;
    z-index: 9999;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    overflow: hidden;
    min-width: 180px;
    border: 1px solid #e4e7ed;

    .menu-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px 16px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 14px;
      color: #303133;
      white-space: nowrap;

      .el-icon {
        font-size: 16px;
        color: #606266;
      }

      &:hover {
        background: var(--art-bg-color);
        color: #409eff;

        .el-icon {
          color: #409eff;
        }
      }

      &:active {
        background: #e6f7ff;
      }
    }
  }

  // 批量管理对话框样式
  .batch-manage-container {
    .batch-filters {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .batch-article-list {
      .batch-group {
        margin-bottom: 16px;

        .batch-group-header {
          font-size: 13px;
          font-weight: 600;
          color: #6b7280;
          padding: 8px 12px;
          background: #f9fafb;
          border-radius: 6px;
          margin-bottom: 8px;
        }

        .batch-article-item {
          padding: 8px 12px;
          border-radius: 6px;
          transition: background 0.2s;

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

          .article-item-compact {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            gap: 12px;

            .article-title {
              flex: 1;
              font-size: 14px;
              color: var(--art-text-gray-900);
              font-weight: 500;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }

            .article-info {
              display: flex;
              align-items: center;
              gap: 8px;
              flex-shrink: 0;
              font-size: 12px;

              .article-date {
                color: #9ca3af;
              }

              .article-author {
                color: var(--art-text-gray-600);
              }
            }
          }
        }
      }
    }
  }
</style>
