# 🏥 星像精准研发部管理系统

> 🎯 **专业的医学影像标注全流程管理平台**  
> 集成项目管理、任务分配、标注审核、绩效统计、团队协作于一体的现代化内部管理系统

<p align="center">
  <a href="https://vuejs.org/"><img src="https://img.shields.io/badge/Vue-3.5.12-brightgreen.svg" alt="Vue"></a>
  &nbsp;&nbsp;
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.104.1-009688.svg" alt="FastAPI"></a>
  &nbsp;&nbsp;
  <a href="https://element-plus.org/"><img src="https://img.shields.io/badge/Element%20Plus-2.8.0-409EFF.svg" alt="Element Plus"></a>
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/PostgreSQL-12+-336791.svg" alt="PostgreSQL">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/Redis-6.0+-DC382D.svg" alt="Redis">
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/MinIO-7.2.0-C72E49.svg" alt="MinIO">
  &nbsp;&nbsp;
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"></a>
</p>

---

## 📖 目录

- [项目简介](#-项目简介)
- [核心功能](#-核心功能)
- [技术架构](#-技术架构)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [功能详解](#-功能详解)
- [部署指南](#-部署指南)
- [开发规范](#-开发规范)

---

## 🎯 项目简介

医学影像标注管理系统是一个基于 **Vue 3 + TypeScript + FastAPI** 的全栈企业级应用，专为医学影像标注工作流程设计。系统经过大型重构，提供了完整的项目全生命周期管理、灵活的权限控制、高效的任务流转、智能的绩效分析等功能。

### ✨ 系统特色

- 🎨 **现代化 UI**：基于 Element Plus 的精美界面，响应式布局适配多端
- 🔐 **灵活权限**：完善的 RBAC 权限系统，支持角色与菜单动态配置
- 📊 **智能统计**：多维度绩效分析，ECharts 可视化展示
- 🚀 **高效协作**：实时协作编辑，WebSocket 消息通知
- 📝 **知识管理**：多类型文章发布，支持 Markdown/Word 导入
- 🔄 **流程优化**：完整的任务生命周期，跳过申请审批机制
- 🔔 **实时通知**：WebSocket + Redis Pub/Sub 实时消息推送，支持离线通知
- ⚡ **高性能缓存**：Redis 全面集成，支持 Token 管理、消息队列、离线通知存储

---

## 🆕 最近更新 (v3.5+)

> 🗓️ **最近更新**: 2026-01-09  
> 🚀 **核心修复与增强**: 重点修复了文档编辑器体验、通知重复问题，并增强了工作日志功能。

### 1️⃣ 文档与编辑器优化 📝

- **动态角色加载**：文章发布页移除硬编码角色，完全同步后端角色配置。
- **智能成员筛选**：选择"可编辑角色"后，自动联动筛选"可编辑成员"，提升操作效率。
- **布局重构**：文章详情页采用固定侧边栏 + 自适应内容区，解决双滚动条问题。
- **预览组件升级**：全站统一使用 `ArtWangPreview` 组件，提供一致的文档阅读体验。

### 2️⃣ 通知系统增强 🔔

- **定时下班提醒**：集成了 APScheduler，每天 17:10 准时推送温馨提醒。
- **重复通知修复**：彻底解决了 WebSocket 重连导致的通知重复弹窗问题。
- **离线消息优化**：增强 Redis 离线消息存储策略，确保不丢失任何重要通知。

### 3️⃣ 工作日志改进 📅

- **时区问题修复**：彻底修复工作周创建时的日期偏移问题（UTC vs 本地时间）。
- **按部门选人**：创建/编辑工作周时，支持一键选择整个部门员工，并支持多部门叠加。
- **导出功能升级**：PDF 导出支持更灵活的时间范围和图表展示。

### 4️⃣ 其他重要更新 ✨

- **登录页动画**：新增"星像"品牌动画，提升视觉体验。
- **Token 管理**：优化 Token 过期处理机制，支持服务器端灵活配置过期时间。
- **性能优化**：优化了 Redis 缓存策略，提升系统响应速度。

---

## 🚀 核心功能

### 1️⃣ 项目管理系统

#### 📂 项目仪表板

- **概览统计**：项目进度、任务分布、月度绩效排行
- **智能分析**：任务状态分布（饼图+柱状图），标注员参与度分析
- **数据过滤**：排除已完结项目，支持多维度筛选

#### 📋 项目列表（树形导航）

**子页面功能**：

- **项目创建**：项目基本信息、任务导入、成员分配
- **项目详情**：项目信息编辑、任务统计图表、完结管理
- **任务导入**：批量CSV导入、文件夹扫描、任务分配策略
- **项目分类管理**：动态分类配置、图标设置、权限控制

**核心功能**：

- **三级导航结构**
  - **一级**：项目（显示状态标签、时间、任务统计）
  - **二级**：项目详情 + 动态文章分类（会议记录、模型测试等）
  - **三级**：具体文章列表
- **项目详情页**
  - 项目基本信息展示
  - 任务统计图表（状态分布、进度、标注员完成情况）
  - 项目完结功能（支持批量操作）
- **动态分类管理**
  - 每个项目默认包含"会议记录"和"模型测试"
  - 支持自定义添加新分类（需求文档、协作文档等）
  - 自定义分类图标和类型标识
- **批量任务导入**
  - 支持文件/文件夹选择
  - 自动生成 CSV 任务清单
  - 灵活的任务分配策略

#### 📄 文章管理

- **多类型支持**：会议记录、模型测试、需求文档、协作文档等
- **项目关联**：文章可归属于具体项目，也可作为公共文章
- **导入功能**：支持 Markdown (.md) 和 Word (.docx) 文档导入
- **批量管理**：批量删除、批量修改分类/部门
- **三级导航**：部门 → 月份 → 文章，快速定位
- **富文本编辑**：WangEditor 5.x（常规文档）/ XNote（Textbus + Yjs，多人协作）

---

### 2️⃣ 标注任务系统

#### 🎯 任务池（Task Pool）

**子页面功能**：

- **任务筛选**：按状态、项目、分配人、时间范围筛选
- **批量操作**：批量分配、批量导出、批量状态更新
- **任务详情**：任务信息查看、历史记录、相关文件

**核心功能**：

- **智能筛选卡片**（v3.3+）
  - 待领取、待审核、已跳过、已通过、全部
  - 点击卡片快速筛选任务
  - 实时统计数量显示
  - 统一视觉风格
- **快速操作**：一键领取、批量分配、导出任务
- **CSV 导出功能**（v3.3+）
  - 支持导出选中任务或全部任务
  - 自动格式化时间字段（避免 Excel `#####` 问题）
  - 包含任务标题、所属项目、状态、影像URL等完整信息
  - 智能文件命名（日期 + 数量）
  - UTF-8 BOM 编码确保中文正常显示
- **影像URL显示**（v3.3+）
  - 任务列表显示影像URL，可直接点击在新标签页打开
  - 详情弹窗同步显示影像URL
  - 长URL自动换行，不撑破列宽
- **横向时间轴**（v3.3+）
  - 直观展示任务生命周期
  - 每个阶段关联对应截图
  - 支持查看详细事件信息
- **视图切换**：列表/卡片视图，支持排序和分页

#### 💼 我的工作台（My Workspace）

**子页面功能**：

- **任务详情**：标注界面、文件预览、进度跟踪
- **成果提交**：截图上传、标注文件提交、质量自检
- **跳过申请**：申请理由填写、截图证明上传

**核心功能**：

- **个人任务中心**：我的待办、进行中、已提交任务
- **智能筛选卡片**（v3.3+）
  - 进行中、待审核、已完成、已驳回、总计
  - 点击卡片快速筛选任务
  - 实时统计数量显示
  - 一键定位到特定任务状态
- **快速操作**：开始标注、提交成果、申请跳过
- **截图上传**：支持标注截图批量上传（MinIO）
- **驳回原因查看**（v3.3+）
  - 精美的驳回记录弹窗
  - 按驳回次数分组显示截图
  - 降序排列（最新的驳回记录在前）
  - 紧凑的布局设计
  - 支持截图预览和放大
- **影像URL显示**（v3.3+）
  - 任务列表显示影像URL
  - 详情弹窗同步显示影像URL
- **任务生命周期时间轴**（v3.3+）
  - 横向时间轴展示任务流转全过程
  - 每个节点关联对应阶段截图
  - 智能时间匹配算法（60秒容差）
  - 支持查看节点详情和截图预览

#### 🔍 任务审核（Task Review）

**子页面功能**：

- **审核详情**：任务内容查看、标注结果检查、质量评估
- **审核历史**：已审核任务归档、审核统计、质量分析
- **跳过审批**：跳过申请审核、理由评估、决策记录

**核心功能**：

- **智能筛选卡片**（默认）
  - 待审核、待跳过审批、全部任务
  - 实时显示任务数量统计
  - 一键快速筛选
- **多次提交截图分组**（v3.3+）
  - 按提交时间自动分组显示截图
  - 清晰区分每次提交的内容
  - 最新提交在前，方便快速查看
  - 支持展开/收起每组截图
- **影像URL显示**（v3.3+）
  - 任务列表显示影像URL
  - 详情弹窗同步显示影像URL
- **跳过审核优化**（v3.3+）
  - 跳过申请弹窗支持截图预览
  - 图片预览层级优化（z-index: 3000）
  - 支持点击放大和关闭
- **横向时间轴**（v3.3+）
  - 完整展示任务审核历史
  - 每个审核节点关联对应截图
  - 支持查看详细审核意见

#### 🔄 完整的任务生命周期

```
待分配 → 已分配 → 进行中 → 已提交 → 审核中 → 已通过/已驳回
                                       ↓
                                   跳过申请 → 审核 → 已跳过/已拒绝
```

- **审核队列**：待审核任务列表，按提交时间排序
- **审核操作**
  - 通过：质量评分（1-5分）+ 审核意见
  - 驳回：详细驳回理由 + 问题截图上传
  - 跳过审批：审核标注员的跳过申请
- **历史记录**：已审核任务归档，支持重新审核

#### 🚫 跳过申请机制

- **申请流程**：标注员发起 → 审核员审批 → 状态更新
- **申请原因**：必填原因说明 + 可选截图证明
- **审批结果**：同意跳过/拒绝并说明理由
- **状态追踪**：`skip_pending` → `skipped` / `in_progress`

#### 📸 横向时间轴组件（v3.3+）

**功能特性**：

- **可视化时间线**
  - 横向展示任务从创建到完成的全流程
  - 圆形节点标识不同事件类型（创建、分配、提交、审核等）
  - 渐变色彩和阴影效果，视觉层次清晰
  - 动态图标（✓ 通过 / ✗ 驳回）
- **智能截图关联**
  - 基于时间戳自动匹配每个阶段的相关截图
  - 60秒容差的"最近时间匹配"算法
  - 自动去重，避免重复显示
  - 支持多次提交/驳回时准确分组
- **节点卡片信息**
  - 操作人头像和姓名
  - 操作时间（大字体突出显示）
  - 操作类型标签（审核通过/驳回/提交等）
  - 相关截图缩略图（最多显示 4 张）
- **交互体验**
  - 点击节点卡片查看详情
  - 点击截图支持预览和放大
  - 图片预览 z-index 优化，避免遮挡
  - 全局统一的图片查看器样式
- **响应式设计**
  - 容器高度 380px，自动横向滚动
  - 适配不同屏幕尺寸
  - 节点间距和布局自动调整

---

### 3️⃣ 工作日志系统

#### 📅 工作周管理

**子页面功能**：

- **工作周创建**：智能标题生成、工作组选择、时间范围设置、按部门选择员工
- **工作周详情**：日志条目管理、统计报表、员工覆盖管理
- **批量管理**：按月归档、批量删除、状态批量更新

**核心功能**：

- **三级导航**：工作组 → 年月 → 工作周
- **工作组支持**：标注组、算法组、开发组、行政组（可自定义）
- **归档过滤**（v3.2+）
  - 切换开关控制是否显示已归档工作周
  - 默认隐藏已归档，保持界面整洁
  - 一键查看历史记录
  - 智能处理选中状态
- **智能创建**
  - 自动生成标题（如：`2025W51标注组工作计划`）
  - 智能周序号（基于组内最新周）
  - 批量创建工作周（支持连续创建 2-12 周）
  - **按部门选择员工**（v3.2+）
    - 一键选择整个部门的所有员工
    - 支持多部门批量选择
    - 显示部门人数统计
    - 员工列表按部门分组显示
  - **智能日期计算**（v3.2+）
    - 修复时区问题，正确显示本地日期
    - 支持跨月、跨年工作周
    - 任何时间点创建都准确无误
- **批量管理**：按月分组，支持筛选、归档、删除

#### 📝 工作记录（v3.3.1+）

**子页面功能**：

- **记录创建**：工作记录基本信息、内容编辑、分类选择、部门设置
- **记录管理**：按部门/员工/时间筛选、批量删除、搜索功能
- **记录详情**：富文本预览、编辑/删除、权限控制

**核心功能**：

- **五级树形导航结构**（v3.3.1+）
  - 部门（第一级）→ 员工（第二级）→ 月份（第三级）→ 日期（第四级）→ 文章（第五级）
  - 点击节点展开/收起，无需点击箭头
  - 默认展开前两个部门，快速浏览
- **页面布局优化**（v3.3.1+）
  - 左侧导航栏固定 320px 宽度
  - 右侧文章详情区域自适应
  - 左右高度 100% 对齐，各自独立滚动
  - 无双滚动条问题
- **文章展示功能**（v3.3.1+）
  - 大标题显示（26px）
  - Meta 信息（作者、时间、浏览量）
  - 所属部门标签
  - 编辑/删除按钮（权限控制）
- **批量管理功能**（v3.3.1+）
  - 批量删除工作记录
  - 按部门/分类/搜索筛选
  - 支持批量操作确认
- **Markdown/Word 导入**（v3.3.1+）
  - 支持 Markdown (.md) 文件导入
  - 支持 Word (.docx) 文件导入
  - 自动提取标题和内容
  - 智能格式转换
- **自动定位最新记录**（v3.3.1+）
  - 进入页面自动选中当前用户的最新工作记录
  - 自动展开到对应位置
  - 提升用户体验

#### 📝 工作日志条目管理

**子页面功能**：

- **日志编辑**：工作内容录入、工作类型选择、工时统计
- **员工管理**：覆盖员工选择、部门筛选、批量添加
- **统计报表**：工时分析、完成率统计、工作类型分布
- **PDF导出**：多维度报告导出、自定义时间范围

**核心功能**：

- **日志条目**
  - 工作内容、工作类型、工作时长、计划时长
  - 支持周一至周日（含周末加班）
  - 请假类型自动识别（病假、年假等）
- **工作标题快速选择（v3.2+）**
  - **常用标签模式**（默认）：18+ 预定义标签，Emoji 图标可视化
    - 日常工作：日常标注、算法研发、模型训练、代码开发等
    - 会议相关：会议、招聘面试、客户沟通
    - 外出相关：出差、外出、培训学习
    - 其他类型：文档编写、技术调研、项目部署、日常维护
  - **关联项目模式**：快速关联到具体项目任务
  - 双模式互斥选择，Radio 按钮快速切换
  - 支持自定义输入，灵活扩展
  - 智能识别：编辑时自动判断标题类型
- **覆盖员工管理**
  - 分部门选择员工
  - 自定义用户选择器（替代 el-transfer）
- **工作周统计**
  - 计划工时（默认 40 小时，5天\*8h）
  - 实际工时（含周末加班）
  - 工作类型分布
  - 完成率分析
- **统计报表**
  - 按员工汇总：堆叠柱状图显示工作类型分布
  - 计划 vs 实际工时对比

#### 📊 工作日志导出功能（v3.2+）

**导出类型**：

- **单周报告**：导出当前查看的工作周详细报告
- **月度报告**：汇总指定月份内所有工作周
- **季度报告**：汇总指定季度内所有工作周
- **年度报告**：汇总指定年份内所有工作周

**报告内容**：

- **工作周信息**：时间范围、状态、统计概览
- **整体工时统计**：参与人数、计划工时、实际工时、完成率
- **工作类型分布**：饼图展示各类型工作占比
- **工时对比分析**：柱状图对比计划与实际工时
- **用户详细统计**：每人的工作量、完成率、类型分布表格

**导出特性**：

- 🎨 **专业PDF格式**：ReportLab 生成高质量PDF报告
- 📊 **可视化图表**：Matplotlib 生成饼图、柱状图
- 📅 **灵活时间范围**：支持自定义年份、月份、季度选择
- 🔢 **精确统计**：自动聚合多个工作周数据
- 📝 **中文字体支持**：完美显示中文内容

---

### 4️⃣ 知识与文章系统

#### 📚 会议记录

**子页面功能**：

- **记录创建**：会议基本信息、参会人员、会议纪要
- **记录管理**：按部门分类、按时间筛选、批量操作
- **记录详情**：富文本查看、附件下载、评论互动

**导航栏优化**（v3.4+）：

- **三级导航结构**：部门 → 月份 → 文章
- **统一头部组件**：使用 `ArtPageHeader` 组件，与其他页面保持一致
- **选中样式**：使用 Element Plus 内置 `highlight-current` 机制，渐变背景、左侧边框、主题色高亮
- **文章图标**：每个文章项显示文档图标，提升视觉识别度
- **标题截断**：支持显示最多 18 个字符，超出部分用省略号显示

**分类管理**：

- **考核**：绩效考核会议、评估会议记录
- **评估**：项目评估、技术评估会议
- **对外**：客户会议、合作伙伴沟通
- **对内**：团队会议、部门例会

#### 🧪 模型测试

**子页面功能**：

- **测试报告创建**：测试环境、测试数据、结果分析
- **测试管理**：按模型分类、测试历史、结果对比
- **测试详情**：测试参数、性能指标、问题记录

**导航栏优化**（v3.4+）：

- **三级导航结构**：部门 → 月份 → 文章
- **统一头部组件**：使用 `ArtPageHeader` 组件，与其他页面保持一致
- **选中样式**：使用 Element Plus 内置 `highlight-current` 机制，渐变背景、左侧边框、主题色高亮
- **文章图标**：每个文章项显示文档图标，提升视觉识别度
- **标题截断**：支持显示最多 18 个字符，超出部分用省略号显示

**分类管理**：

- **胸肺**：胸部、肺部相关模型测试
- **泌尿**：泌尿系统模型测试
- **肝胆**：肝胆系统模型测试
- **盆腔**：盆腔相关模型测试

#### 🤝 团队协作

**子页面功能**：

- **协作文档创建**：实时编辑、版本控制、权限管理
- **协作管理**：在线用户、编辑历史、冲突解决
- **文档分享**：链接分享、权限设置、访问统计

**核心功能**：

- **实时协作文档**（WebSocket）
- **版本控制**：文档历史记录，版本号追踪
- **权限管理**：可编辑角色/成员配置

**编辑器与协作引擎**：

- **编辑器**：`@textbus/xnote`（封装组件：`src/components/core/forms/art-textbus-editor/index.vue`）
- **协作引擎**：Yjs + y-websocket（服务端：`yjs-collab-server/server.js`，路径：`/api/collaboration/yjs/{documentId}`）
- **后端能力**：FastAPI 提供协作文档的创建/更新/协作者管理与内容保存（`backend/app/api/collaboration.py`），内置 OT-lite WebSocket 端点（`/ws/{document_id}`）作为降级方案。

**使用示例（前端）**：

```vue
<ArtTextbusEditor
  v-model="content"
  :height="editorHeight"
  placeholder="开始编写你的文档..."
  :collaboration-enabled="true"
  :document-id="documentId"
  :current-user="{ id: user.id, username: user.username, color: '#4ade80' }"
/>
```

**新建/编辑页面**：

- 创建页：`src/views/collaboration/create/index.vue`，两列布局（左侧设置面板 + 右侧编辑器），支持在线成员显示、标签设置、统计信息展示。
- 编辑页：`src/views/collaboration/edit/index.vue`，支持自动保存（默认 30 秒）、Markdown/Word 导入、静态工具栏切换、在线用户列表。

**页面布局优化**：

- 左侧面板固定宽度 `320px`，右侧编辑器区域自适应。
- 响应式断点：`1200px`/`992px` 下自动切换为纵向布局，左侧面板最大高度限制为 `400px`。
- 编辑器容器使用 `overflow: visible`，确保工具栏气泡与悬浮面板正常展示。

**协作服务器（开发环境）**：

```bash
cd yjs-collab-server
npm install
node server.js
```

启动后默认监听 `http://localhost:1234`，前端连接路径为 `/api/collaboration/yjs/{documentId}`。

**生产部署建议**：

- 使用 `pm2` 守护进程或 Docker 部署 `yjs-collab-server`。
- Nginx 配置 WebSocket 反向代理，启用 `Upgrade`/`Connection: upgrade` 头。

**后端 API 速览**：

- 文档创建：`POST /collaboration/documents`
- 文档更新：`PUT /collaboration/documents/{document_id}`
- 协作者添加：`POST /collaboration/documents/{document_id}/collaborators`
- 协作者角色更新：`PUT /collaboration/documents/{document_id}/collaborators/{user_id}`
- 文档内容保存：`PUT /collaboration/documents/{document_id}/content`

#### 📝 文章发布系统

**通用功能**：

- **创建页面**
  - 标题、摘要、正文（富文本编辑器）
  - 封面图片上传
  - 分类选择（根据文章类型动态加载）
  - **归属项目选择**（可选，不选则为公共文章）
  - 可编辑角色/成员配置
  - 所属部门设置
- **导入功能**（v3.3.1+）
  - **Markdown 导入优化**
    - 使用成熟的 `marked.js` 库替代自定义解析器
    - 完整支持 CommonMark 规范
    - 支持扩展语法（GFM）
    - 使用 DOMPurify 进行 HTML 清理，防止 XSS 攻击
    - 自动提取第一行为标题（可选）
    - 智能处理 BOM 标记和字符编码
    - 统一的工具函数 `src/utils/markdown.ts`
  - **Word 文档导入**
    - Word (.docx)：使用 mammoth 转换为 HTML
    - 保持原始格式和样式
- **预览功能**（v3.3.1+）
  - **ArtWangPreview 组件**
    - 基于 WangEditor 的只读预览组件
    - 与编辑器样式完全一致，无需维护两套样式
    - 支持所有 WangEditor 格式（代码块、表格、待办列表等）
    - 隐藏工具栏，专注于内容展示
    - 增强的滚动条样式，打印友好
    - 全面替换所有页面的 `v-html` 预览方式
- **批量操作**
  - 按部门/分类/搜索筛选
  - 批量删除、批量修改分类/部门

---

### 5️⃣ 标注绩效系统

#### 📊 个人绩效

**子页面功能**：

- **绩效概览**：个人统计卡片、趋势分析图表
- **任务记录**：详细任务列表、完成情况、质量评分
- **绩效导出**：个人绩效PDF报告、数据导出

**核心功能**：

- **核心指标卡片**
  - 总任务数、本周任务数、进行中任务
  - 今日完成、入职时间（大字体突出）
- **趋势分析**
  - 任务完成趋势（周/月视图）
  - 质量评分趋势
- **详细记录**：任务记录表，支持查看详情

#### 🏆 团队绩效

**子页面功能**：

- **绩效排行**：多维度排行榜、筛选条件、导出功能
- **项目统计**：按项目分析、完成情况对比
- **绩效分析**：团队趋势、个人对比、质量分析

**核心功能**：

- **排行榜**：支持当日/本周/本月/本年筛选
- **项目分类统计**
  - 按项目筛选
  - 仅显示已完成任务分类
- **标注员完成统计**
  - 按项目筛选完成数量
  - 柱状图可视化展示

#### 📈 项目仪表板（见项目管理）

- 项目进度概览（排除已完结项目）
- 任务状态分布（饼图 + 柱状图）
- 标注员参与度分析（堆叠柱状图）

---

### 6️⃣ 实时通知系统（v3.3+）

#### 🔔 WebSocket 实时通知

**功能特性**：

- **实时推送**
  - 任务提交、审核、驳回即时通知
  - 跳过申请、跳过审批实时提醒
  - 下班提醒定时推送（17:10）
- **多端同步**
  - 浏览器内 `ElMessage` 弹窗通知
  - 系统级桌面通知（需浏览器权限）
  - 自动请求通知权限
- **智能重连**
  - 网络断开自动重连（最多 10 次）
  - 指数退避算法（延迟递增）
  - 心跳机制检测连接状态（30 秒间隔）
- **消息去重**
  - 3 秒窗口内相同消息自动过滤
  - 避免重复通知干扰用户

#### 📡 Redis Pub/Sub 订阅系统

**架构设计**：

```
后端 FastAPI WebSocket
   ↓
Redis Pub/Sub（消息分发）
   ├─ notify:user:{user_id}     # 用户私有频道
   ├─ notify:role:{role}         # 角色频道（admin/reviewer/annotator）
   ├─ notify:project:{project_id} # 项目频道
   └─ notify:global              # 全局广播频道
   ↓
前端 WebSocket 客户端
   ├─ ElMessage 通知
   ├─ ElNotification 通知
   └─ 系统桌面通知
```

**核心功能**：

- **智能路由**
  - 用户级通知：精准推送到特定用户
  - 角色级通知：广播到所有相同角色用户
  - 项目级通知：推送到项目成员
  - 全局通知：所有在线用户
- **离线消息存储**
  - Redis List 存储离线通知（7 天 TTL）
  - 每用户最多 50 条通知（自动 LTRIM）
  - 登录时自动恢复未读通知
  - 支持标记已读和批量删除
- **消息优先级**
  - urgent：紧急消息（需用户交互）
  - high：重要消息（警告样式）
  - normal：普通消息（信息样式）
  - low：低优先级消息

#### 🔧 通知 API

**前端 API**：

```typescript
// 获取未读通知
notificationApi.getNotifications()

// 获取未读数量
notificationApi.getUnreadCount()

// 标记单条已读
notificationApi.markAsRead(notificationId)

// 标记全部已读
notificationApi.markAllAsRead()

// 删除通知
notificationApi.deleteNotification(notificationId)

// 清除所有已读
notificationApi.clearReadNotifications()
```

**后端 Redis 操作**：

```python
# 保存通知
save_notification(user_id, notification_data)

# 获取未读通知
get_unread_notifications(user_id)

# 标记已读（从 Redis List 移除）
mark_as_read(user_id, notification_id)

# 标记全部已读（删除整个 List）
mark_all_as_read(user_id)
```

#### 🎯 通知触发场景

| 事件         | 接收人        | 通知类型            | 优先级 |
| ------------ | ------------- | ------------------- | ------ |
| 任务提交审核 | 管理员/审核员 | `task_submitted`    | high   |
| 任务审核通过 | 标注员        | `task_approved`     | normal |
| 任务审核驳回 | 标注员        | `task_rejected`     | high   |
| 申请跳过     | 管理员/审核员 | `skip_requested`    | high   |
| 跳过申请通过 | 标注员        | `skip_approved`     | normal |
| 跳过申请拒绝 | 标注员        | `skip_rejected`     | normal |
| 下班提醒     | 全体用户      | `work_end_reminder` | normal |

#### 💡 通知最佳实践

**前端集成**：

```typescript
// 1. 登录后自动连接 WebSocket
userStore.connectNotifyWS()

// 2. 监听消息（自动处理）
// userStore 内部已集成，无需额外代码

// 3. 登录时显示离线通知
const unreadNotifications = await notificationApi.getNotifications()
unreadNotifications.forEach((notif) => {
  ElNotification({
    title: notif.title,
    message: notif.content,
    type: notif.priority === 'high' ? 'warning' : 'info'
  })
})
```

**后端集成**：

```python
from app.services.notification_ws import ws_manager

# 发送用户通知
await ws_manager.send_to_user_id(
    user_id=user.id,
    message={
        "type": "task_approved",
        "content": "您的任务已通过审核",
        "task_id": task.id
    }
)

# 角色广播
await ws_manager.broadcast_to_role(
    role="admin",
    message={
        "type": "task_submitted",
        "content": f"标注员提交了任务：{task.title}",
        "pending": pending_count
    }
)

# 全局广播
await ws_manager.broadcast_to_all(
    message={
        "type": "work_end_reminder",
        "title": "下班提醒",
        "content": "请及时保存文件，填写工作日志，关闭电脑",
        "priority": "normal"
    }
)
```

---

### 7️⃣ 系统管理

#### 👥 用户管理

**子页面功能**：

- **用户创建**：基本信息录入、角色分配、部门设置
- **用户编辑**：信息修改、角色调整、状态管理
- **用户详情**：用户信息查看、操作日志、权限详情

**核心功能**：

- **用户信息**：用户名、真实姓名、部门、入职日期、联系方式
- **角色分配**：支持多角色（admin、reviewer、annotator、algorithm 等）
- **状态管理**：启用/停用用户
- **智能删除**
  - 自动转移数据所有权给系统管理员
  - 区分处理进行中/已完成任务
  - 保留绩效数据作为历史记录
- **头像管理**：支持头像上传和预览

#### 🎭 角色管理

**子页面功能**：

- **角色创建**：角色信息设置、权限配置、状态管理
- **权限配置**：可视化权限树、批量权限设置
- **角色详情**：角色信息、权限详情、关联用户

**核心功能**：

- **角色配置**：角色名称、代码、描述、状态
- **菜单权限**：可视化的树形权限配置界面
- **权限继承**：支持权限批量分配和继承
- **动态加载**：权限实时生效，无需重启

#### 🔐 权限控制

- **前端权限**：菜单显示、按钮权限、路由守卫
- **后端权限**：API 接口权限验证（`require_permission`）
- **细粒度控制**：页面级、功能级、按钮级权限
- **权限示例**

  ```typescript
  // 前端
  userStore.hasPermission('ProjectManagement')

  // 后端
  @require_permission("TaskReview")
  ```

#### 🎛️ 菜单管理

**子页面功能**：

- **菜单配置**：菜单结构设置、权限绑定、图标配置
- **动态菜单**：基于权限的菜单生成、实时更新

**核心功能**：

- **后端控制模式**：菜单配置存储在后端
- **动态加载**：根据用户权限动态返回可访问菜单
- **菜单结构**
  ```
  ├─ 首页
  ├─ 项目管理
  │  ├─ 项目仪表板
  │  └─ 项目列表
  ├─ 标注任务
  │  ├─ 任务池
  │  ├─ 我的工作台
  │  └─ 任务审核
  ├─ 工作日志
  │  └─ 周列表
  ├─ 知识与文章
  │  ├─ 会议记录
  │  ├─ 模型测试
  │  └─ 团队协作
  ├─ 标注绩效
  │  ├─ 个人绩效
  │  └─ 团队绩效
  └─ 系统管理
     ├─ 用户管理
     └─ 角色管理
  ```

#### 📱 主题与个性化

- **主题切换**：亮色/暗色主题
- **语言切换**：国际化支持（i18n）
- **响应式设计**：移动端适配

---

## 🛠️ 系统架构

### 🏗️ 整体架构设计

本系统采用前后端分离架构，基于现代化的技术栈构建，具备高性能、高可用、易扩展的特点。

```
┌─────────────────────────────────────────────────────────┐
│                    前端层 (Vue 3 + TS)                   │
│  ┌──────────┬──────────┬──────────┬──────────┐        │
│  │ 项目管理 │ 标注任务 │ 工作日志 │ 知识文章 │        │
│  │ 标注绩效 │ 系统管理 │ 权限控制 │ 实时协作 │        │
│  └──────────┴──────────┴──────────┴──────────┘        │
│           Pinia Store + Vue Router + Element Plus       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket/JWT
┌────────────────────┴────────────────────────────────────┐
│                  API 网关 (FastAPI)                      │
│  ┌──────────┬──────────┬──────────┬──────────┐        │
│  │ JWT认证  │ RBAC权限 │ 业务逻辑 │ 数据验证 │        │
│  │ 中间件   │ 装饰器   │ 路由处理 │ Pydantic │        │
│  └──────────┴──────────┴──────────┴──────────┘        │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
   PostgreSQL     Redis        MinIO    WebSocket
   (业务数据)   (缓存/Token)  (文件存储)  (实时通信)
```

### 🔐 权限管理体系 (RBAC)

#### 权限架构设计

```
用户 (User) ──1:1──→ 角色 (Role) ──1:N──→ 权限 (Permissions)
    │                    │                      │
    ├─ 用户信息          ├─ 角色名称            ├─ 菜单权限
    ├─ 登录凭证          ├─ 角色编码            ├─ 按钮权限
    └─ 状态管理          └─ 权限JSON            └─ API权限
```

#### 权限控制层级

1. **前端权限控制**

   - 菜单显示控制：`userStore.hasPermission('ProjectManagement')`
   - 按钮权限控制：`v-permission="['UserManagement']"`
   - 路由守卫：动态路由生成

2. **后端权限控制**
   - API接口权限：`@require_permission("TaskReview")`
   - 数据权限：基于用户角色过滤数据
   - 操作权限：细粒度的功能权限控制

#### 内置角色权限

| 角色          | 权限范围 | 主要功能                     |
| ------------- | -------- | ---------------------------- |
| **admin**     | 全部权限 | 系统管理、用户管理、角色管理 |
| **reviewer**  | 审核权限 | 任务审核、绩效查看、项目管理 |
| **annotator** | 标注权限 | 任务标注、个人绩效、工作日志 |
| **algorithm** | 算法权限 | 模型测试、技术文档、项目参与 |

### 🕐 登录有效时间管理

#### Token 配置

- **默认有效期**：30分钟 (`ACCESS_TOKEN_EXPIRE_MINUTES=30`)
- **自动续期**：剩余5分钟时自动续期 (`TOKEN_RENEW_THRESHOLD_MINUTES=5`)
- **存储方式**：Redis缓存 + 前端LocalStorage
- **安全机制**：JWT签名 + 过期检测 + 自动刷新

#### 配置方式

```python
# 方式1：修改配置文件 backend/app/config.py
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1小时

# 方式2：环境变量 backend/.env
ACCESS_TOKEN_EXPIRE_MINUTES=120  # 2小时
```

### 前端技术栈

| 技术         | 版本   | 说明                            |
| ------------ | ------ | ------------------------------- |
| Vue          | 3.5.12 | 渐进式 JavaScript 框架          |
| TypeScript   | 5.6.3  | JavaScript 的超集，提供类型安全 |
| Vite         | 6.1.0  | 新一代前端构建工具              |
| Element Plus | 2.8.0  | 基于 Vue 3 的组件库             |
| Pinia        | 3.0.2  | Vue 官方状态管理库              |
| Vue Router   | 4.4.2  | 官方路由管理器                  |
| Axios        | 1.7.5  | HTTP 客户端                     |
| ECharts      | 5.6.0  | 数据可视化图表库                |
| WangEditor   | 5.1.23 | 轻量级富文本编辑器              |
| Mammoth      | 1.8.0  | Word 文档解析库                 |
| Marked       | 14.1.3 | Markdown 解析器                 |
| SCSS         | -      | CSS 预处理器                    |
| Vue I18n     | 9.14.0 | 国际化插件                      |

### 后端技术栈

| 技术              | 版本     | 说明                                                 |
| ----------------- | -------- | ---------------------------------------------------- |
| FastAPI           | 0.104.1  | 现代高性能 Web 框架                                  |
| Uvicorn           | 0.24.0   | ASGI 服务器                                          |
| SQLAlchemy        | 2.0.23   | Python ORM 框架                                      |
| Alembic           | 1.12.1   | 数据库迁移工具                                       |
| PostgreSQL        | 12+      | 关系型数据库                                         |
| **Redis**         | **6.0+** | **缓存、Token 管理、Pub/Sub 消息队列、离线通知存储** |
| MinIO             | 7.2.0    | 对象存储服务                                         |
| Python-Jose       | 3.3.0    | JWT Token 处理                                       |
| Passlib           | 1.7.4    | 密码加密                                             |
| Pydantic          | 2.5.0    | 数据验证                                             |
| Pydantic-Settings | 2.1.0    | 配置管理                                             |
| APScheduler       | 3.10.4   | 定时任务调度                                         |
| ReportLab         | 4.0+     | PDF 报告生成                                         |
| Matplotlib        | 3.8+     | 数据可视化（图表生成）                               |

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端层 (Vue 3)                      │
│  ┌──────────┬──────────┬──────────┬──────────┐        │
│  │ 项目管理 │ 任务系统 │ 绩效统计 │ 知识文章 │        │
│  └──────────┴──────────┴──────────┴──────────┘        │
│       Pinia Store  +  Vue Router  +  WebSocket         │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket (JSON)
┌────────────────────┴────────────────────────────────────┐
│                    API 网关 (FastAPI)                    │
│  ┌──────────┬──────────┬──────────┬──────────┐        │
│  │ JWT认证  │ RBAC权限 │ 业务逻辑 │ WebSocket │        │
│  │ 中间件   │ 装饰器   │ 路由处理 │ 通知管理  │        │
│  └──────────┴──────────┴──────────┴──────────┘        │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
   PostgreSQL     Redis        MinIO    APScheduler
   (业务数据)   (多功能)    (文件存储)  (定时任务)
                    │
        ┌───────────┼───────────┬───────────┐
        │           │           │           │
   Token管理   Pub/Sub     离线通知   会话缓存
   (白名单)    (实时消息)  (List存储)  (临时数据)
```

### Redis 全面集成架构（v3.3+）

```
Redis（统一缓存层）
├─ Token 管理
│  ├─ Token 白名单（SET）
│  ├─ Token 有效期控制（TTL）
│  └─ 多端登录检测
│
├─ Pub/Sub 消息队列
│  ├─ notify:user:{user_id}     → 用户私有通知
│  ├─ notify:role:{role}         → 角色广播通知
│  ├─ notify:project:{project_id} → 项目通知
│  └─ notify:global              → 全局广播
│
├─ 离线通知存储
│  ├─ notifications:user:{user_id} (LIST)
│  ├─ 7 天 TTL 自动过期
│  ├─ 最多 50 条自动裁剪
│  └─ 登录时自动恢复
│
└─ 会话缓存（可选）
   ├─ 用户权限缓存
   ├─ 项目统计缓存
   └─ 临时数据存储
```

---

## 🚀 快速开始

### 环境要求

| 软件       | 版本要求  | 说明              |
| ---------- | --------- | ----------------- |
| Node.js    | >= 16.0.0 | JavaScript 运行时 |
| Python     | >= 3.8    | 后端语言          |
| PostgreSQL | >= 12     | 数据库            |
| Redis      | >= 6.0    | 缓存服务          |
| MinIO      | 最新版    | 文件存储（可选）  |

### 1️⃣ 克隆项目

```bash
git clone <repository-url>
cd project_manager
```

### 2️⃣ 前端设置

```bash
# 安装依赖
npm install
# 或使用 pnpm（推荐）
pnpm install

# 创建环境变量文件
cp .env.example .env.development

# 启动开发服务器
npm run dev

# 访问: http://localhost:3008
```

#### 前端环境变量配置 (`.env.development`)

```env
# 端口
VITE_PORT=3008

# 基础路径
VITE_BASE_URL=/

# 后端 API 代理地址
VITE_API_PROXY_URL=http://localhost:8000

# 版本
VITE_VERSION=dev

# 访问模式（backend/frontend）
VITE_ACCESS_MODE=backend
```

### 3️⃣ 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量示例
cp env_example.txt .env

# 编辑 .env 文件，配置数据库等信息
```

#### 后端环境变量配置 (`.env`)

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis 配置
REDIS_URL=redis://localhost:6379

# JWT 配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
TOKEN_RENEW_THRESHOLD_MINUTES=5

# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=medical-annotations

# CORS 配置
ALLOWED_ORIGINS=["http://localhost:3008"]
```

### 4️⃣ 数据库初始化

```bash
# 在 backend 目录下执行
python scripts/init_db.py
```

这将创建数据库表并初始化以下默认账户：

| 用户名     | 密码         | 角色      | 说明       |
| ---------- | ------------ | --------- | ---------- |
| admin      | admin123     | admin     | 系统管理员 |
| annotator1 | annotator123 | annotator | 标注员1    |
| annotator2 | annotator123 | annotator | 标注员2    |
| annotator3 | annotator123 | annotator | 标注员3    |

### 5️⃣ 启动服务

```bash
# 在 backend 目录下
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用简化命令
python -m app.main
```

访问：

- **前端**: http://localhost:3008
- **API 文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📁 项目结构

```
project_manager/
├── backend/                          # 后端代码（FastAPI）
│   ├── app/
│   │   ├── api/                      # API 路由
│   │   │   ├── auth.py               # 认证：登录、注册
│   │   │   ├── users.py              # 用户管理
│   │   │   ├── roles.py              # 角色管理
│   │   │   ├── menu.py               # 菜单配置
│   │   │   ├── projects.py           # 项目管理
│   │   │   ├── project_categories.py # 项目分类
│   │   │   ├── tasks.py              # 任务管理
│   │   │   ├── performance.py        # 绩效统计
│   │   │   ├── work_logs.py          # 工作日志
│   │   │   ├── collaboration.py      # 团队协作
│   │   │   ├── articles.py           # 文章发布
│   │   │   ├── upload.py             # 文件上传
│   │   │   └── files.py              # 文件代理
│   │   ├── models/                   # SQLAlchemy 模型
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   ├── project.py
│   │   │   ├── task.py
│   │   │   ├── article.py
│   │   │   ├── work_log.py
│   │   │   ├── performance.py
│   │   │   └── collaboration.py
│   │   ├── schemas/                  # Pydantic 模型（请求/响应）
│   │   ├── services/                 # 业务逻辑
│   │   ├── middleware/               # 中间件
│   │   │   └── logging.py            # 请求日志
│   │   ├── utils/                    # 工具函数
│   │   │   ├── security.py           # JWT、密码加密
│   │   │   ├── permissions.py        # 权限检查
│   │   │   ├── datetime_utils.py     # UTC 时间工具（v3.1+）
│   │   │   ├── minio_client.py       # MinIO 客户端
│   │   │   ├── redis_client.py       # Redis 客户端
│   │   │   └── token_manager.py      # Token 管理
│   │   ├── services/                 # 业务逻辑
│   │   │   ├── notification_ws.py    # WebSocket 通知服务
│   │   │   ├── scheduler_service.py  # 定时任务服务（v3.1+）
│   │   │   └── pdf_export_service.py # PDF 导出服务（v3.2+）
│   │   ├── config.py                 # 配置管理
│   │   ├── database.py               # 数据库连接
│   │   └── main.py                   # 应用入口
│   ├── scripts/                      # 脚本
│   │   └── init_db.py                # 数据库初始化
│   ├── migrations/                   # SQL 迁移文件
│   ├── logs/                         # 日志文件
│   ├── uploads/                      # 上传文件（开发环境）
│   ├── requirements.txt              # Python 依赖
│   ├── docker-compose.yml            # Docker 配置
│   └── Dockerfile
│
├── src/                              # 前端代码（Vue 3）
│   ├── api/                          # API 封装
│   │   ├── articlesApi.ts
│   │   ├── collaborationApi.ts
│   │   ├── menuApi.ts
│   │   ├── projectApi.ts
│   │   ├── roleApi.ts
│   │   ├── userApi.ts
│   │   ├── usersApi.ts
│   │   └── workLogApi.ts
│   ├── components/                   # 公共组件
│   │   ├── core/                     # 核心组件库
│   │   │   ├── buttons/
│   │   │   ├── cards/
│   │   │   ├── charts/               # ECharts 封装
│   │   │   ├── dialogs/
│   │   │   ├── forms/
│   │   │   │   ├── art-wang-editor/  # 富文本编辑器
│   │   │   │   └── art-wang-preview/ # 富文本预览组件（v3.3.1+）
│   │   │   ├── tables/
│   │   │   └── ...
│   │   ├── custom/                   # 自定义组件
│   │   ├── layout/                   # 布局组件
│   │   └── project/                  # 项目相关组件
│   ├── views/                        # 页面视图
│   │   ├── index/                    # 首页
│   │   ├── project/                  # 项目模块
│   │   │   ├── dashboard/            # 项目仪表板
│   │   │   ├── management/           # 项目列表
│   │   │   │   └── components/
│   │   │   │       ├── ArticleDetailView.vue
│   │   │   │       └── ProjectDetailView.vue
│   │   │   ├── task-pool/            # 任务池
│   │   │   ├── my-workspace/         # 我的工作台
│   │   │   ├── task-review/          # 任务审核
│   │   │   ├── articles/             # 文章管理
│   │   │   │   ├── meeting/          # 会议记录
│   │   │   │   ├── model-test/       # 模型测试
│   │   │   │   ├── create/           # 发布页面
│   │   │   │   └── detail/           # 详情页面
│   │   │   └── performance/          # 绩效统计
│   │   │       ├── personal.vue
│   │   │       └── team.vue
│   │   ├── work-log/                 # 工作日志
│   │   │   ├── index.vue             # 周列表
│   │   │   ├── records/              # 工作记录（v3.3.1+）
│   │   │   │   └── index.vue         # 工作记录页面
│   │   │   ├── week-detail.vue       # 周详情
│   │   │   └── components/
│   │   │       ├── WorkLogEntryCell.vue
│   │   │       └── WorkLogStatistics.vue
│   │   ├── collaboration/            # 团队协作
│   │   │   ├── index.vue
│   │   │   ├── create/
│   │   │   └── document/
│   │   ├── system/                   # 系统管理
│   │   │   ├── user/                 # 用户管理
│   │   │   └── role/                 # 角色管理
│   │   └── login/                    # 登录页
│   ├── store/                        # Pinia 状态管理
│   │   └── modules/
│   │       ├── user.ts               # 用户状态
│   │       ├── menu.ts               # 菜单状态
│   │       ├── project.ts            # 项目状态
│   │       └── ...
│   ├── router/                       # 路由配置
│   │   ├── index.ts
│   │   ├── routes.ts
│   │   └── permission.ts             # 路由守卫
│   ├── utils/                        # 工具函数
│   │   ├── http/                     # HTTP 封装
│   │   ├── timeFormat.ts             # 时间格式化工具（v3.1+）
│   │   ├── storage.ts                # 本地存储
│   │   ├── format.ts                 # 格式化工具
│   │   └── ...
│   ├── assets/                       # 静态资源
│   │   ├── styles/                   # 全局样式
│   │   ├── icons/                    # 图标
│   │   └── img/                      # 图片
│   ├── config/                       # 配置文件
│   ├── directives/                   # 自定义指令
│   ├── enums/                        # 枚举定义
│   ├── types/                        # TypeScript 类型
│   ├── locales/                      # 国际化
│   ├── mock/                         # Mock 数据
│   └── main.ts                       # 入口文件
│
├── deploy/                           # 部署配置
│   ├── docker-compose.yml
│   ├── nginx/
│   └── db-init/
│
├── dist/                             # 构建输出
├── public/                           # 公共静态文件
│
├── docs/                             # 技术文档
│   ├── ROOT_CAUSE_FIX_SUMMARY.md     # 时区根源修复总结（v3.1）
│   ├── BACKEND_TIME_FIX.md           # 后端时间修复详解（v3.1）
│   ├── TIME_FIX_COMPLETE.md          # 完整修复方案（v3.1）
│   ├── DATABASE_TIME_STORAGE.md      # 数据库时间存储说明（v3.1）
│   ├── FIX_TIME_ZONE_ISSUE.md        # 前端时区修复（v3.1）
│   ├── FIX_REJECT_DIALOG_ISSUES.md   # 驳回弹窗优化（v3.1）
│   ├── SCHEDULED_NOTIFICATION_GUIDE.MD # 定时通知指南（v3.1）
│   ├── WORK_WEEK_IMPROVEMENTS.md     # 工作周管理优化（v3.2）
│   ├── WORK_LOG_EXPORT_FEATURE.md    # 工作日志导出功能（v3.2）
│   ├── WORK_LOG_ADVANCED_EXPORT.md   # 高级导出功能（v3.2）
│   ├── USER_CENTER_AVATAR_REFRESH_FIX.md # 个人中心刷新优化（v3.2）
│   ├── ARTICLE_EDITOR_TOOLBAR_STICKY_FIX.md # 编辑器工具栏固定优化（v3.2）
│   ├── WORK_LOG_EXPORT_YEAR_FIX.md   # 年份选择器修复（v3.2）
│   ├── WORK_LOG_EXPORT_JOINEDLOAD_FIX.md  # SQLAlchemy错误修复（v3.2）
│   ├── WORK_LOG_EXPORT_YEAR_ATTRIBUTE_FIX.md # Year属性错误修复（v3.2）
│   ├── WORK_LOG_SUBJECT_TAG_FEATURE.md   # 工作标题快速选择功能（v3.2）
│   └── QUICK_REFERENCE.md            # 快速参考（v3.1）
├── .env.development                  # 开发环境变量
├── .env.production                   # 生产环境变量
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json                     # TypeScript 配置
├── vite.config.ts                    # Vite 配置
├── eslint.config.mjs                 # ESLint 配置
└── README.md
```

---

## 🔍 功能详解

### 项目管理详解

#### 1. 项目创建

```typescript
// 支持的字段
{
  name: string // 项目名称
  description: string // 项目描述
  status: 'active' | 'completed' | 'paused' // 状态
  priority: 'high' | 'medium' | 'low' // 优先级
  category: string // 分类
  start_date: string // 开始日期
  end_date: string // 结束日期（可选）
}
```

#### 2. 批量任务导入

- **步骤1**：选择文件或文件夹
- **步骤2**：系统生成 CSV 清单
- **步骤3**：编辑任务信息（可选）
- **步骤4**：分配标注员
- **步骤5**：确认导入

#### 3. 动态分类

```typescript
// 创建自定义分类
{
  name: string // 分类名称（如：需求文档）
  type: string // 类型标识（如：requirement）
  icon: string // 图标（可选）
  order: number // 排序
}
```

### 任务流程详解

#### 任务状态转换

```mermaid
graph LR
    A[待分配] --> B[已分配]
    B --> C[进行中]
    C --> D[已提交]
    D --> E[已通过]
    D --> F[已驳回]
    F --> C
    C --> G[跳过申请]
    G --> H[已跳过]
    G --> C
```

#### API 示例

```python
# 领取任务
POST /tasks/{task_id}/claim

# 开始任务
POST /tasks/{task_id}/start

# 提交任务
POST /tasks/{task_id}/submit
{
  "annotation_data": {...},
  "comment": "标注说明",
  "organ_count": 3
}

# 审核任务
POST /tasks/{task_id}/review
{
  "action": "approve",  # 或 "reject"
  "score": 4,
  "comment": "审核意见"
}

# 申请跳过
POST /tasks/{task_id}/request-skip
{
  "reason": "图像质量问题",
  "images": ["http://..."]
}

# 审核跳过申请
POST /tasks/{task_id}/review-skip
{
  "approved": true,
  "comment": "同意跳过"
}
```

### 权限系统详解

#### 权限层级

```
Menu (菜单权限)
  └─ Button (按钮权限)
      └─ API (接口权限)
```

#### 权限配置示例

```typescript
// 前端：检查按钮权限
<el-button v-if="userStore.hasPermission('ProjectManagement')">
  新建项目
</el-button>

// 后端：API 权限验证
@router.post("/projects/")
def create_project(
    data: ProjectCreate,
    current_user: User = Depends(require_permission("ProjectManagement"))
):
    ...
```

#### 常用权限标识

| 权限标识            | 说明         | 适用角色                   |
| ------------------- | ------------ | -------------------------- |
| `Dashboard`         | 查看仪表板   | 所有                       |
| `ProjectManagement` | 项目管理     | admin, reviewer            |
| `TaskPool`          | 任务池访问   | admin, reviewer, annotator |
| `TaskReview`        | 任务审核     | admin, reviewer            |
| `WorkLogManagement` | 工作周管理   | admin, reviewer            |
| `WorkLogReview`     | 工作日志审核 | admin, reviewer            |
| `UserManagement`    | 用户管理     | admin                      |
| `RoleManagement`    | 角色管理     | admin                      |

---

## 🐳 部署指南

### Docker 部署（推荐）

#### 1. 使用 Docker Compose

```bash
# 进入部署目录
cd deploy-local

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 2. 服务说明

```yaml
services:
  backend: # FastAPI 后端
    ports: 8000:8000

  frontend: # Vue 前端
    ports: 3008:80

  postgres: # PostgreSQL 数据库
    ports: 5432:5432

  redis: # Redis 缓存
    ports: 6379:6379

  minio: # MinIO 对象存储
    ports: 9000:9000, 9001:9001

  nginx: # Nginx 反向代理
    ports: 80:80, 443:443
```

### 生产环境部署

#### 1. 前端构建

```bash
# 安装依赖
npm install

# 构建生产版本
npm run build

# 输出目录：dist/
```

#### 2. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # 前端静态文件
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket 代理
    location /collaboration/ws/ {
        proxy_pass http://localhost:8000/collaboration/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 3. 后端部署（Systemd）

```ini
# /etc/systemd/system/medical-annotation.service
[Unit]
Description=Medical Annotation API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl enable medical-annotation
sudo systemctl start medical-annotation
sudo systemctl status medical-annotation
```

### 数据库备份

```bash
# 备份
pg_dump -U username -h localhost -d dbname > backup_$(date +%Y%m%d).sql

# 恢复
psql -U username -h localhost -d dbname < backup_20250117.sql
```

---

## 📋 开发规范

### 代码规范

#### 前端

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format

# 样式检查
npm run lint:stylelint

# 类型检查
npm run type-check
```

#### 后端

```bash
# 代码格式化
black app/

# 代码检查
flake8 app/

# 类型检查
mypy app/
```

### Git 提交规范

使用 Commitizen 进行规范化提交：

```bash
# 使用交互式提交
npm run commit

# 提交类型
feat:     新功能
fix:      修复 Bug
docs:     文档更新
style:    代码格式调整
refactor: 重构
perf:     性能优化
test:     测试相关
chore:    构建/工具相关
```

### 分支管理

```
main        # 主分支，生产环境
develop     # 开发分支
feature/*   # 功能分支
hotfix/*    # 紧急修复
release/*   # 发布分支
```

### 代码审查

- Pull Request 需至少1人审核
- 通过所有测试用例
- 无 Lint 错误
- 有必要的注释和文档

---

## 📚 API 文档

### Swagger UI

启动后端后访问：**http://localhost:8000/docs**

### 核心 API 列表

#### 认证相关

```
POST   /auth/login              # 用户登录
POST   /auth/register           # 用户注册
GET    /auth/current-user       # 获取当前用户
POST   /auth/change-password    # 修改密码
```

#### 项目管理

```
GET    /projects/               # 获取项目列表
POST   /projects/               # 创建项目
GET    /projects/{id}           # 获取项目详情
PUT    /projects/{id}           # 更新项目
DELETE /projects/{id}           # 删除项目
POST   /projects/{id}/complete  # 完结项目
GET    /projects/{id}/categories # 获取项目分类
POST   /projects/{id}/categories # 创建项目分类
```

#### 任务管理

```
GET    /tasks/                  # 获取任务列表
POST   /tasks/                  # 创建任务
POST   /tasks/import            # 批量导入任务
POST   /tasks/{id}/claim        # 领取任务
POST   /tasks/{id}/start        # 开始任务
POST   /tasks/{id}/submit       # 提交任务
POST   /tasks/{id}/review       # 审核任务
POST   /tasks/{id}/request-skip # 申请跳过
POST   /tasks/{id}/review-skip  # 审核跳过申请
```

#### 绩效统计

```
GET    /performance/dashboard   # 仪表板数据
GET    /performance/personal    # 个人绩效
GET    /performance/team        # 团队绩效
GET    /performance/ranking     # 排行榜
```

#### 工作日志

```
GET    /work-logs/weeks         # 获取工作周列表
POST   /work-logs/weeks         # 创建工作周
GET    /work-logs/weeks/{id}    # 获取工作周详情
POST   /work-logs/entries       # 创建日志条目
PUT    /work-logs/entries/{id}  # 更新日志条目
DELETE /work-logs/entries/{id}  # 删除日志条目（v3.2+）
GET    /work-logs/statistics    # 获取统计数据
GET    /work-logs/export        # 导出工作日志PDF报告（v3.2+）
                                 # 参数：report_type, week_id, year, month, quarter
```

#### 文章管理

```
GET    /articles/               # 获取文章列表
POST   /articles/               # 创建文章
GET    /articles/{id}           # 获取文章详情
PUT    /articles/{id}           # 更新文章
DELETE /articles/{id}           # 删除文章
GET    /articles/{id}/history   # 文章历史版本
```

---

## ❓ 常见问题

### Q1: Redis 连接失败？

**A:** 检查 Redis 服务是否运行：

```bash
# Linux/Mac
redis-cli ping

# Windows
redis-server --service-start
```

如果 Redis 不可用，系统会自动降级为仅 JWT 模式。

### Q2: MinIO 上传失败？

**A:** 确认 MinIO 配置正确：

```python
# backend/app/config.py
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET_NAME = "medical-annotations"
```

### Q3: 数据库迁移失败？

**A:** 重置数据库并重新初始化：

```bash
cd backend
python scripts/init_db.py --reset
```

### Q4: 权限配置不生效？

**A:**

1. 清除浏览器缓存
2. 退出重新登录
3. 检查角色权限配置

### Q5: WebSocket 连接失败？

**A:** 检查 Nginx 配置，确保支持 WebSocket 升级：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

---

## 🔄 更新日志

### v3.3.0 (2025-11-03) - Redis 全面集成 & 实时通知系统

#### 🔔 实时通知系统

- ✅ **WebSocket + Redis Pub/Sub 通知架构**
  - 四级通知频道：用户、角色、项目、全局
  - 智能消息路由和分发
  - 前端自动重连机制（最多 10 次）
  - 心跳检测（30 秒间隔 ping/pong）
  - 3 秒窗口消息去重
- ✅ **离线通知存储**
  - Redis List 存储离线消息（7 天 TTL）
  - 每用户最多 50 条通知（自动裁剪）
  - 登录时自动恢复未读通知
  - 支持标记已读和批量删除
- ✅ **系统级通知**
  - PWA Manifest 配置应用名称
  - 系统桌面通知支持
  - 个性化通知标题（包含用户姓名）
  - 自动请求通知权限
- ✅ **通知 API**
  - 前端 `notificationApi` 完整封装
  - 后端 Redis 离线通知服务
  - 通知优先级支持（urgent/high/normal/low）

#### 📸 横向时间轴组件

- ✅ **可视化时间线**
  - 圆形节点标识不同事件类型
  - 渐变色彩和阴影效果
  - 动态图标（✓ 通过 / ✗ 驳回）
- ✅ **智能截图关联**
  - 60 秒容差的"最近时间匹配"算法
  - 自动去重，避免重复显示
  - 支持多次提交/驳回时准确分组
  - 时区兼容性处理
- ✅ **节点卡片优化**
  - 去除评分显示
  - 时间字段加粗突出
  - 美化操作标签
  - 头像文字可见性优化
- ✅ **交互体验**
  - 点击节点卡片查看详情
  - 截图预览和放大
  - z-index 层级优化（9999/10000/10001）
  - 图片查看器全局样式统一

#### 🎯 任务三页面优化

- ✅ **智能筛选卡片**
  - 任务池：待领取、待审核、已跳过、已通过、全部
  - 我的工作台：进行中、待审核、已完成、已驳回、总计
  - 任务审核：待审核、待跳过审批、全部任务
  - 点击卡片快速筛选，实时统计数量
- ✅ **CSV 导出功能**（任务池）
  - 支持导出选中任务或全部任务
  - 自动格式化时间字段（`YYYY-MM-DD HH:mm`）
  - UTF-8 BOM 编码确保中文正常显示
  - 智能文件命名（日期 + 数量）
- ✅ **影像URL显示**
  - 三个任务页面列表统一显示影像URL
  - 详情弹窗同步显示影像URL
  - 可点击链接在新标签页打开
  - 长URL自动换行，不撑破列宽
- ✅ **驳回原因弹窗优化**（我的工作台）
  - 按驳回次数分组显示截图
  - 降序排列（最新驳回记录在前）
  - 紧凑的布局设计
  - 减少红色使用，美化视觉效果
- ✅ **多次提交截图分组**（任务审核）
  - 按提交时间自动分组显示截图
  - 清晰区分每次提交的内容
  - 最新提交在前，方便快速查看
- ✅ **跳过审核优化**（任务审核）
  - 截图预览层级优化（z-index: 3000）
  - 支持点击放大和关闭
  - 图片查看器全局样式统一

#### ⚡ Redis 全面集成

- ✅ **Token 管理**
  - Token 白名单机制（SET 数据结构）
  - Token 有效期控制（TTL）
  - 登录持久化支持（localStorage）
- ✅ **Pub/Sub 消息队列**
  - 四级通知频道架构
  - 智能消息路由和分发
  - 支持用户、角色、项目、全局广播
- ✅ **离线通知存储**
  - Redis List 存储（7 天 TTL）
  - 自动裁剪（最多 50 条）
  - 登录时自动恢复
- ✅ **优雅降级**
  - Redis 不可用时自动切换为纯 JWT 模式
  - WebSocket 自动重连
  - 通知推送优先级处理

#### 🐛 Bug 修复

- ✅ 修复任务时间轴截图显示错误问题
- ✅ 修复图片预览z-index冲突和闪烁
- ✅ 修复图片查看器亮度过暗和裁剪问题
- ✅ 修复 CSV 导出时间显示 `#####` 问题
- ✅ 修复通知重复推送问题（前端+后端双重去重）
- ✅ 修复离线通知不显示问题
- ✅ 修复 WebSocket 连接断开后不重连问题

#### 📝 技术文档

- ✅ 新增 `TIMELINE_SCREENSHOTS_FEATURE.md` - 时间轴截图功能文档
- ✅ 新增 `TIMELINE_Z_INDEX_FIX.md` - z-index 层级优化文档
- ✅ 新增 `TIMELINE_IMAGE_DEDUPLICATION.md` - 图片去重文档
- ✅ 新增 `TIMELINE_TIME_BASED_IMAGE_MATCHING.md` - 时间匹配算法文档
- ✅ 新增 `WEBSOCKET_REDIS_NOTIFICATION_UPGRADE.md` - WebSocket 升级文档
- ✅ 新增 `FIX_NOTIFICATION_DUPLICATE.md` - 前端通知去重文档
- ✅ 新增 `FIX_BACKEND_NOTIFICATION_DUPLICATE.md` - 后端通知去重文档
- ✅ 新增 `REDIS_OFFLINE_NOTIFICATION.md` - Redis 离线通知文档
- ✅ 新增 `MIGRATION_TO_REDIS_NOTIFICATION.md` - 通知迁移指南
- ✅ 新增 `SYSTEM_NOTIFICATION_OPTIMIZATION.md` - 系统通知优化文档
- ✅ 新增 `MY_WORKSPACE_FILTER_ENHANCEMENT.md` - 我的工作台筛选优化
- ✅ 新增 `TASK_POOL_FILTER_ENHANCEMENT.md` - 任务池筛选优化
- ✅ 新增 `TASK_POOL_EXPORT_FEATURE.md` - 任务池导出功能
- ✅ 新增 `TASK_IMAGE_URL_DISPLAY_ENHANCEMENT.md` - 影像URL显示优化

---

### v3.4.0 (2025-11-06) - 文章页面导航栏重构与UI优化

#### 🎨 会议记录与模型测试页面重构

- ✅ **导航栏选中样式修复**
  - 使用 Element Plus 内置 `highlight-current` 和 `:current-node-key` 机制
  - 替换手动绑定的选中类名为框架自动管理的 `.is-current` 类
  - 使用 `:deep(.el-tree)` 样式穿透，确保选中样式正确应用
  - 选中节点显示渐变背景、左侧边框、主题色文字和图标放大效果
- ✅ **头部组件统一**
  - 会议记录和模型测试页面头部替换为 `ArtPageHeader` 组件
  - 统一视觉风格，与其他页面保持一致
  - 简化代码，删除约 190 行自定义头部样式代码
  - 使用组件 props 传递标题、描述、图标等信息
- ✅ **导航栏样式重构**
  - 完全照搬工作记录页面的成功实现
  - 添加文章图标（`<el-icon><Document /></el-icon>`）
  - 增加文章标题截断长度（从 10 到 18 个字符）
  - 优化缩进和间距，提升可读性
- ✅ **移除导航栏标签**
  - 移除会议记录和模型测试页面导航栏文章项的标签显示
  - 清理不再需要的 `.node-meta-tag` CSS 样式
  - 界面更加简洁，突出文章标题

#### 🔧 技术改进

- ✅ **使用框架官方 API**
  - 不再手动管理选中状态，使用 Element Plus 的内置机制
  - 提高代码可维护性和稳定性
  - 避免样式冲突和浏览器缓存问题
- ✅ **代码质量提升**
  - 统一组件使用，减少重复代码
  - 优化样式结构，提高可读性
  - 完善的技术文档记录

#### 📝 技术文档

- ✅ 新增 `NAVIGATION_STYLE_FIX_AND_HEADER_REPLACEMENT.md` - 导航栏样式修复和头部组件替换文档
- ✅ 新增 `NAVIGATION_REFACTOR_MEETING_AND_MODEL.md` - 导航栏重构详解文档

#### 🐛 Bug 修复

- ✅ 修复会议记录页面选中样式不生效问题
- ✅ 修复模型测试页面选中样式不生效问题
- ✅ 修复头部组件样式不一致问题

---

### v3.3.1 (2025-11-05) - 工作记录功能与内容预览重构

#### 📝 工作记录功能（新增）

- ✅ **五级树形导航结构**
  - 部门（第一级）→ 员工（第二级）→ 月份（第三级）→ 日期（第四级）→ 文章（第五级）
  - 点击节点展开/收起，无需点击箭头
  - 默认展开前两个部门，快速浏览
- ✅ **页面布局优化**
  - 左侧导航栏固定 320px 宽度
  - 右侧文章详情区域自适应
  - 左右高度 100% 对齐，各自独立滚动
  - 无双滚动条问题
- ✅ **文章展示功能**
  - 大标题显示（26px）
  - 分类标签彩色显示
  - Meta 信息（作者、时间、浏览量）
  - 所属部门标签
  - 编辑/删除按钮（权限控制）
- ✅ **批量管理功能**
  - 批量删除工作记录
  - 按部门/分类/搜索筛选
  - 支持批量操作确认
- ✅ **Markdown/Word 导入**
  - 支持 Markdown (.md) 文件导入
  - 支持 Word (.docx) 文件导入
  - 自动提取标题和内容
  - 智能格式转换
- ✅ **自动定位最新记录**
  - 进入页面自动选中当前用户的最新工作记录
  - 自动展开到对应位置
  - 提升用户体验

#### 🎨 ArtWangPreview 预览组件（新增）

- ✅ **基于 WangEditor 的只读预览组件**
  - 与编辑器样式完全一致，无需维护两套样式
  - 使用 `readOnly: true` 配置，双重禁用保护
  - 隐藏工具栏，专注于内容展示
- ✅ **丰富的格式支持**
  - 代码块高亮自动支持
  - 表格样式自动支持
  - 待办列表自动支持
  - 所有 WangEditor 支持的格式
- ✅ **优化的预览体验**
  - 增强的滚动条样式
  - 打印友好
  - 响应式设计
  - 可选全屏模式
- ✅ **全面替换 v-html**
  - 工作记录页面：替换 `v-html` 为 `ArtWangPreview`
  - 会议记录页面：替换 `v-html` 为 `ArtWangPreview`
  - 项目文档页面：替换 `v-html` 为 `ArtWangPreview`
  - 模型测试页面：替换 `v-html` 为 `ArtWangPreview`
  - 团队协作页面：替换 `v-html` 为 `ArtWangPreview`
  - 协作文档页面：替换 `v-html` 为 `ArtWangPreview`

#### 📄 Markdown 导入功能重构（优化）

- ✅ **使用成熟的 marked.js 库**
  - 替换自定义的 `simpleMdToHtml` 函数
  - 完整支持 CommonMark 规范
  - 支持扩展语法（GFM）
  - 更好的性能和稳定性
- ✅ **增强的安全性**
  - 使用 DOMPurify 进行 HTML 清理
  - 防止 XSS 攻击
  - 安全的链接处理
- ✅ **优化的导入流程**
  - 自动提取第一行为标题（可选）
  - 智能处理 BOM 标记
  - 支持多种字符编码
  - 详细的错误提示
- ✅ **统一的工具函数**
  - 提取为公共工具函数 `src/utils/markdown.ts`
  - 统一的导入逻辑
  - 便于维护和扩展

#### 📝 技术文档

- ✅ 新增 `WORK_RECORDS_FEATURE_FINAL.md` - 工作记录功能完整文档
- ✅ 新增 `ART_WANG_PREVIEW_COMPONENT.md` - ArtWangPreview 组件文档
- ✅ 新增 `REPLACE_VHTML_WITH_PREVIEW.md` - v-html 替换文档
- ✅ 新增 `MARKDOWN_IMPORT_FEATURE.md` - Markdown 导入功能文档
- ✅ 新增 `MARKDOWN_IMPORT_OPTIMIZATION.md` - Markdown 导入优化文档

#### 🐛 Bug 修复

- ✅ 修复工作记录页面导航栏不刷新问题
- ✅ 修复文章链接跳转不准确问题
- ✅ 修复项目列表导航栏缩进不对齐问题
- ✅ 修复预览组件内容不更新问题

---

### v3.3.0 (2025-11-03) - Redis 全面集成 & 实时通知系统

---

### v3.2.0 (2025-10-27) - 工作周管理优化

#### 🕐 工作周日期时区修复

- ✅ **修复日期计算错误**
  - 修复工作周创建时日期偏差 1 天的问题
  - 周一创建工作周现在正确显示周一（之前显示为周日）
  - 解决 `toISOString()` 导致的 UTC 时区转换问题
- ✅ **优化日期工具函数**
  - `src/api/workLogApi.ts` 修复 5 个日期相关函数
  - `src/views/work-log/index.vue` 修复 `getWeekDateRange()` 函数
  - 统一使用本地时区格式化日期（YYYY-MM-DD）
  - 解析日期时添加 `T00:00:00` 确保本地时区
- ✅ **跨时段稳定性**
  - 解决凌晨 0-8 点时间计算问题
  - 支持跨月、跨年工作周正确计算
  - 所有时间点均返回正确的本地日期

#### 👥 按部门选择员工功能

- ✅ **创建工作周增强**
  - 新增"按部门选择"功能，一键选择整个部门员工
  - 支持多部门批量选择
  - 显示每个部门的人数统计（如"开发部 8人"）
  - 员工列表按部门分组显示
  - 智能合并：部门选择追加而非覆盖已选人员
- ✅ **编辑工作周优化**
  - 同样支持按部门快速添加人员
  - 一键清空所有已选人员
  - 实时显示"已选择 X 人"
- ✅ **UI 交互优化**
  - 部门下拉框显示人数标签
  - 员工选择器按部门分组
  - 过滤搜索功能增强
  - 响应式数据自动更新

#### 📊 工作日志导出功能

- ✅ **多维度导出支持**
  - 单周报告：导出当前工作周详细数据
  - 月度报告：汇总整月工作周统计
  - 季度报告：季度工作量分析
  - 年度报告：年度工作总结
- ✅ **专业PDF生成**
  - ReportLab 生成高质量PDF
  - Matplotlib 图表可视化
  - 工作类型分布饼图
  - 计划vs实际工时柱状图
  - 用户详细统计表格
- ✅ **灵活的时间选择**
  - 自定义年份、月份、季度
  - 智能日期范围计算
  - 自动聚合多周数据
- ✅ **完善的错误处理**
  - 修复 WorkWeek.year 属性错误
  - 修复 work_type 字段访问错误
  - 修复 SQLAlchemy joinedload 错误
  - 前端年份选择器类型修正

#### 📋 工作标题快速选择功能

- ✅ **双模式选择系统**
  - **常用标签模式**（默认）：18+ 预定义标签
    - 日常工作：日常标注、算法研发、模型训练、代码开发、Bug修复等
    - 会议相关：会议、招聘面试、客户沟通
    - 外出相关：出差、外出、培训学习
    - 其他类型：文档编写、技术调研、项目部署、日常维护
  - **关联项目模式**：快速关联到具体项目任务
  - Radio 按钮切换，两种模式互斥
- ✅ **可视化设计**
  - Emoji 图标 + 彩色背景标识
  - 标签名称加粗显示
  - 描述文字辅助说明
  - 一目了然的选项布局
- ✅ **智能交互**
  - 创建新日志默认「常用标签」模式
  - 编辑时自动识别标题类型（标签/项目）
  - 切换模式时自动清空选择
  - 支持自定义输入扩展
- ✅ **类型安全**
  - TypeScript 类型守卫
  - 运行时参数验证
  - 完善的错误处理

#### 🔄 工作周归档过滤功能

- ✅ **切换开关控制**
  - 切换显示/隐藏已归档工作周
  - 默认隐藏已归档，保持界面整洁
  - 开关位于左侧导航栏筛选区域
- ✅ **智能过滤**
  - 关闭时只显示活跃工作周
  - 开启时显示所有工作周（包括已归档）
  - 实时更新树形结构
- ✅ **智能选择处理**
  - 关闭开关时自动切换选中状态
  - 自动选中第一个活跃工作周
  - 平滑的用户体验
- ✅ **归档后自动刷新**
  - 归档操作后立即刷新导航栏
  - 恢复归档后立即刷新导航栏
  - 父子组件事件通信机制

#### 👤 个人中心即时刷新优化

- ✅ **头像更新后自动刷新**
  - 上传新头像后立即显示
  - 无需手动刷新页面
  - 全局同步（顶部导航栏也同步更新）
- ✅ **基本信息编辑后自动刷新**
  - 保存信息后立即显示最新数据
  - 通过 userStore 全局状态管理
  - 确保前后端数据一致性
- ✅ **响应式数据流**
  - 正确使用 Pinia store
  - Computed 响应式更新
  - 日志追踪和错误处理

#### 📝 文章编辑器工具栏固定优化

- ✅ **Sticky 工具栏**
  - 编辑长文档时工具栏固定在顶部
  - 无需滚动回顶部即可使用格式化功能
  - 使用 CSS `position: sticky` 实现
  - 零 JavaScript 开销，性能优秀
- ✅ **体验一致性**
  - 与项目列表中的编辑体验保持一致
  - 知识与文章页面编辑体验提升
  - 会议记录和模型测试编辑更流畅
- ✅ **最小改动**
  - 只需添加 CSS 样式
  - 不影响现有布局结构
  - 维护成本低

#### 📝 技术文档

- ✅ 新增 `WORK_WEEK_IMPROVEMENTS.md` - 工作周优化详解
- ✅ 新增 `WORK_LOG_EXPORT_FEATURE.md` - 基础导出功能文档
- ✅ 新增 `WORK_LOG_ADVANCED_EXPORT.md` - 高级导出功能文档
- ✅ 新增 `WORK_LOG_EXPORT_YEAR_FIX.md` - 年份选择器修复文档
- ✅ 新增 `WORK_LOG_EXPORT_JOINEDLOAD_FIX.md` - SQLAlchemy错误修复
- ✅ 新增 `WORK_LOG_EXPORT_YEAR_ATTRIBUTE_FIX.md` - Year属性错误修复
- ✅ 新增 `WORK_LOG_SUBJECT_TAG_FEATURE.md` - 工作标题快速选择功能文档
- ✅ 新增 `USER_CENTER_AVATAR_REFRESH_FIX.md` - 个人中心自动刷新修复文档
- ✅ 新增 `ARTICLE_EDITOR_TOOLBAR_STICKY_FIX.md` - 编辑器工具栏固定优化文档
- ✅ 详细的修复说明和测试指南
- ✅ 使用场景和最佳实践

---

### v3.1.0 (2025-10-23) - 时区修复与系统优化

#### 🕐 时区问题根源修复（重要更新）

- ✅ **后端统一时间处理**
  - 新增 `datetime_utils.py` 工具模块
  - 所有时间使用 `utc_now()` 生成 UTC aware datetime
  - 序列化自动添加时区标识（`Z` 或 `+00:00`）
  - 修复 6 个后端文件，24+ 处时间获取点
- ✅ **前端时间格式化**
  - 新增 `timeFormat.ts` 统一时间工具
  - 自动检测并修复 UTC 时间字符串
  - 支持多种格式化类型（datetime/date/time/timeAgo）
  - 修复 4 个前端页面的时间显示
- ✅ **修复的时间字段**
  - 任务相关：created_at, assigned_at, submitted_at, reviewed_at
  - 工作日志：submitted_at, reviewed_at, updated_at
  - 文章管理：locked_at, updated_at
  - 协作文档：last_edited_at
- ✅ **技术文档完善**
  - `ROOT_CAUSE_FIX_SUMMARY.md` - 根源修复总结
  - `BACKEND_TIME_FIX.md` - 后端修复详解
  - `TIME_FIX_COMPLETE.md` - 完整修复方案
  - `DATABASE_TIME_STORAGE.md` - 数据库时间存储说明
  - `FIX_TIME_ZONE_ISSUE.md` - 前端修复文档

#### 🎯 定时通知功能

- ✅ **后端定时任务系统**
  - 集成 APScheduler 定时调度器
  - 每日 17:10 自动发送下班提醒
  - 支持手动触发测试接口
  - 可配置的 Cron 表达式
- ✅ **前端通知增强**
  - WebSocket 实时接收通知
  - Element Plus Message 弹窗提示
  - 浏览器系统级通知
  - 所有用户自动请求通知权限
- ✅ **通知管理器优化**
  - `broadcast_to_all()` 全员广播方法
  - 连接状态管理和自动清理
  - 详细的日志记录和错误处理
  - 支持高优先级消息

#### 🎨 UI/UX 优化

- ✅ **驳回原因弹窗优化**
  - 修复截图预览层级问题（z-index: 3000）
  - 添加醒目的警告提示
  - 驳回原因红色高亮显示
  - 截图悬停效果（边框、阴影、放大镜图标）
  - 优化时间格式化显示
- ✅ **快速入口控制**
  - 支持配置显示/隐藏快速入口功能
  - 简化顶部导航栏
- ✅ **前端导航栏优化**
  - 可配置初始宽度（`defaultMenuWidth`）
  - 支持动态调整和折叠

#### 🐛 Bug 修复

- ✅ 修复任务时间显示晚 8 小时问题
- ✅ 修复工作日志时间格式问题
- ✅ 修复个人绩效时间统计不准确
- ✅ 修复项目仪表板"X小时前"计算错误
- ✅ 修复驳回原因弹窗截图被遮挡
- ✅ 修复下班提醒前端无响应问题

#### 🔧 技术改进

- ✅ **时间处理标准化**
  - 后端：统一使用 UTC 时间存储
  - 前端：统一使用工具函数格式化
  - 符合 ISO 8601 国际标准
- ✅ **代码质量提升**
  - 添加详细的调试日志
  - 完善错误处理机制
  - 统一命名规范
- ✅ **文档体系完善**
  - 新增 8+ 个技术文档
  - 详细的修复说明和测试指南
  - 快速参考文档

---

### v3.0.0 (2025-10-22) - 大型重构版本

#### 🎉 项目管理重构

- ✅ 新增树形导航结构（项目→分类→文章）
- ✅ 优化项目详情页，增加统计图表
- ✅ 支持动态项目分类
- ✅ 优化批量任务导入流程

#### 🔐 权限系统升级

- ✅ 完善 RBAC 权限体系
- ✅ 角色权限可视化配置
- ✅ 前后端权限联动
- ✅ 按钮级权限控制

#### 🎨 UI 界面优化

- ✅ 统一组件风格
- ✅ 优化响应式布局
- ✅ 美化统计图表
- ✅ 优化表单交互

#### 📝 文章系统增强

- ✅ 支持项目关联
- ✅ 三级导航（部门→月份→文章）
- ✅ 批量管理功能
- ✅ Markdown/Word 导入

#### 🔄 任务流程优化

- ✅ 新增跳过申请机制
- ✅ 优化审核流程
- ✅ 增强状态追踪
- ✅ 改进截图上传

#### 📊 绩效系统改进

- ✅ 优化个人绩效页面
- ✅ 增强团队绩效分析
- ✅ 新增项目仪表板
- ✅ 统一图表配色

#### 🗓️ 工作日志优化

- ✅ 三级导航（工作组→年月→工作周）
- ✅ 智能工作周创建
- ✅ 优化日志统计
- ✅ 改进用户选择器

---

## 🕐 时间处理说明（重要）

### 后端时间标准

系统采用 **UTC 时间** 作为统一标准：

```python
# 使用统一的 UTC 时间工具
from app.utils.datetime_utils import utc_now

# ✅ 正确：生成带时区的 UTC 时间
task.created_at = utc_now()
# → datetime(2025, 10, 23, 10, 0, 0, tzinfo=timezone.utc)

# ✅ 序列化自动添加时区标识
# → JSON: "2025-10-23T10:00:00Z"

# ❌ 错误：不要使用 datetime.now()
# task.created_at = datetime.now()  # naive datetime，无时区信息
```

### 前端时间格式化

前端统一使用工具函数处理时间：

```typescript
// 导入时间工具
import { formatDateTime, formatDate, formatTimeAgo } from '@/utils/timeFormat'

// ✅ 格式化完整日期时间
formatDateTime('2025-10-23T10:00:00Z')
// → "2025-10-23 18:00:00"（自动转为本地时间 UTC+8）

// ✅ 格式化日期
formatDate('2025-10-23T10:00:00Z')
// → "2025-10-23"

// ✅ 相对时间
formatTimeAgo('2025-10-23T10:00:00Z')
// → "3小时前"
```

### 时间流程

```
用户操作（北京时间 18:00）
   ↓
后端生成 UTC 时间
utc_now() → 10:00 UTC
   ↓
存入数据库
"2025-10-23 10:00:00"
   ↓
序列化返回前端
"2025-10-23T10:00:00Z"  ← 含 Z 标识
   ↓
前端格式化显示
"2025-10-23 18:00:00"  ← 本地时间
```

### 工作周日期计算（v3.2+）

工作周日期使用 **本地时区** 计算，避免 UTC 转换问题：

```typescript
// ✅ 正确：使用本地时区手动格式化
const formatLocalDate = (date: Date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// ❌ 错误：UTC 时间转换导致日期偏差
return date.toISOString().split('T')[0] // 可能晚 8 小时，显示前一天
```

**关键点**：

- 工作周日期存储为 `YYYY-MM-DD` 字符串（无时间部分）
- 解析时添加 `T00:00:00` 确保本地时区
- 避免使用 `toISOString()` 导致时区转换
- 所有日期计算基于本地时间

**详细文档：**

- 任务时间处理：`ROOT_CAUSE_FIX_SUMMARY.md`、`TIME_HANDLING_EXPLANATION.md`
- 工作周日期：`WORK_WEEK_IMPROVEMENTS.md`

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'feat: add amazing feature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 提交 **Pull Request**

### 时间处理规范（必读）

如果您的代码涉及时间处理，请遵循以下规范：

**后端（任务/日志等带时间戳的数据）：**

```python
# ✅ 使用
from app.utils.datetime_utils import utc_now
created_at = utc_now()

# ❌ 避免
from datetime import datetime
created_at = datetime.now()
```

**前端（时间显示）：**

```typescript
// ✅ 使用
import { formatDateTime } from '@/utils/timeFormat'
const displayTime = formatDateTime(task.createdAt)

// ❌ 避免
const displayTime = new Date(task.createdAt).toLocaleString()
```

**前端（日期字符串，如工作周日期）：**

```typescript
// ✅ 使用本地时区格式化
const year = date.getFullYear()
const month = String(date.getMonth() + 1).padStart(2, '0')
const day = String(date.getDate()).padStart(2, '0')
const dateString = `${year}-${month}-${day}`

// ✅ 解析时添加时间确保本地时区
const date = new Date(dateString + 'T00:00:00')

// ❌ 避免 UTC 转换
const dateString = date.toISOString().split('T')[0] // 错误！
```
