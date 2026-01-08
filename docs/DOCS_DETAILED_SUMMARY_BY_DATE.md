# 开发/修复/重构详细汇总（按日期×模块）

说明：不逐条罗列文件名，而是概述“具体做了什么”，并在每一项后提供链接可查看原始文档细节。

## 2025-10-16

### 权限与用户

- 开发：搭建角色/权限管理框架，梳理菜单结构与权限边界（详见：`./PERMISSION_MANAGEMENT.md`、`./ROLE_PERMISSION_USAGE_GUIDE.md`、`./MENU_REORGANIZATION.md`）。
- 修复：补强用户 API 权限校验、修复头像刷新不同步问题（详见：`./USER_API_PERMISSION_FIX.md`、`./USER_AVATAR_FIX.md`）。
- 开发：完善用户删除闭环，包含删除标记、任务转移与任务状态联动（详见：`./USER_DELETE_LOGIC.md`、`./USER_DELETE_TASK_STATUS.md`、`./USER_DELETE_TRANSFER_LOGIC.md`）。

### Token/会话

- 开发：明确 Token 过期策略、刷新机制与边界说明，用于统一会话管理（详见：`./TOKEN_EXPIRATION_GUIDE.md`）。

### Redis/基础

- 开发：撰写 Redis 使用规范与入门说明，为后续通知与缓存改造奠定基础（详见：`./REDIS_USAGE.md`）。

## 2025-10-17

### 工作日志（Work Log）

- 重构：管理用户界面与交互重做，日志条目布局升级到 V2，统计逻辑重构（详见：`./WORK_LOG_MANAGE_USERS_REDESIGN.md`、`./WORK_LOG_ENTRY_LAYOUT_V2.md`、`./WORK_LOG_STATISTICS_REFACTOR.md`）。
- 修复：管理用户对话框交互问题、统计后端返回异常，优化单元格渲染性能（详见：`./WORK_LOG_MANAGE_USERS_DIALOG_FIX.md`、`./WORK_LOG_STATISTICS_BACKEND_FIX.md`、`./WORK_LOG_ENTRY_CELL_OPTIMIZATION.md`）。
- 开发：新增分组预设与工作周展示更新，优化导航交互（详见：`./WORK_LOG_GROUP_PRESETS.md`、`./WORK_LOG_WEEK_DAYS_UPDATE.md`、`./WORK_LOG_NAV_OPTIMIZATION.md`）。

### 文章导航（Articles Nav）

- 重构：部门导航结构优化、标签截断策略统一，完善三级导航（详见：`./ARTICLES_NAV_DEPARTMENT_OPTIMIZATION.md`、`./ARTICLES_NAV_LABEL_TRUNCATE.md`、`./ARTICLES_NAV_THREE_LEVEL_FIX.md`）。
- 开发：新增文章批量管理能力（详见：`./ARTICLES_BATCH_MANAGEMENT.md`）。

## 2025-10-20

### Token/会话

- 重构：迁移 Token 存储方案并修复登录存储与读取不一致导致的会话问题（详见：`./TOKEN_STORAGE_MIGRATION.md`、`./TOKEN_STORAGE_FIX_LOGIN_ISSUE.md`）。

## 2025-10-21

### 文章/权限

- 开发：新增文章批量管理权限与删除权限校验链路，完善权限闭环（详见：`./ARTICLE_BATCH_MANAGE_PERMISSION.md`、`./ARTICLE_DELETE_PERMISSION.md`）。

### 导出/性能

- 开发：实现性能数据与项目报表导出能力（详见：`./PERFORMANCE_EXPORT_FEATURE.md`、`./PROJECT_REPORT_EXPORT.md`）。

### PDF

- 修复：处理字体渲染与嵌入异常，保障导出效果一致性（详见：`./PDF_FONT_FIX_GUIDE.md`）。

### 用户中心

- 修复：入职日期缺失与显示问题；开发相应的展示逻辑（详见：`./FIX_HIRE_DATE_NOT_SET.md`、`./USER_CENTER_HIRE_DATE_DISPLAY.md`）。

### 绩效

- 开发：新增个人绩效 PDF 导出功能（详见：`./PERSONAL_PERFORMANCE_PDF_EXPORT.md`）。

## 2025-10-22

### 时间/时区

- 开发：统一时间处理规范说明，明确后端/数据库的时间边界与约定（详见：`./TIME_HANDLING_EXPLANATION.md`）。
- 修复：后端时间使用错误与时区计算问题，完成时间修复闭环（详见：`./BACKEND_TIME_FIX.md`、`./FIX_TIME_ZONE_ISSUE.md`、`./TIME_FIX_COMPLETE.md`）。

### 通知/任务

- 修复：任务上限限制与通知队列异常带来的稳定性问题（详见：`./NOTIFICATION_AND_TASK_LIMIT_FIX.md`）。
- 开发：补充通知测试、定时通知指引与实现方案总结（详见：`./TEST_NOTIFICATION.md`、`./SCHEDULED_NOTIFICATION_GUIDE.md`、`./NOTIFICATION_IMPLEMENTATION_SUMMARY.md`）。
- 修复：定位缓存失效根因并形成修复总结（详见：`./ROOT_CAUSE_FIX_SUMMARY.md`）。

### Token/会话

- 开发：统一 Token 管理与操作指南（详见：`./TOKEN_MANAGEMENT_GUIDE.md`）。

### 通用文档

- 开发：常用操作与约定的速查（详见：`./QUICK_REFERENCE.md`）。

## 2025-10-23

### UI/对话框

- 修复：拒绝对话框交互问题（详见：`./FIX_REJECT_DIALOG_ISSUES.md`）。

### 时间/数据库

- 开发：数据库时间存储规范与注意事项（详见：`./DATABASE_TIME_STORAGE.md`）。

## 2025-10-24

### 文章/功能

- 开发：在新视图中补充新增/删除能力（详见：`./ADD_DELETE_FEATURE_TO_NEW_VIEW.md`）。

### 工作日志/权限

- 开发：记录与说明工作日志的权限策略（详见：`./WORK_LOG_PERMISSION_GUIDE.md`）。

### 项目/删除

- 开发：项目删除流程与使用指引（详见：`./PROJECT_DELETE_FEATURE_GUIDE.md`）。

## 2025-10-27

### 工作日志/导出与功能

- 开发：基础与高级导出能力（详见：`./WORK_LOG_EXPORT_FEATURE.md`、`./WORK_LOG_ADVANCED_EXPORT.md`）。
- 修复：导出失败的 ORM 关联问题、年度属性不一致与条目删除逻辑（详见：`./WORK_LOG_EXPORT_JOINEDLOAD_FIX.md`、`./WORK_LOG_EXPORT_YEAR_ATTRIBUTE_FIX.md`、`./WORK_LOG_EXPORT_YEAR_FIX.md`、`./FIX_WORK_LOG_ENTRY_DELETE.md`）。
- 开发：新增主题标签能力（详见：`./WORK_LOG_SUBJECT_TAG_FEATURE.md`）。

### 工作日志/导航与归档

- 开发：导航缩进指南与归档开关（详见：`./WORK_LOG_NAVIGATION_INDENT_GUIDE.md`、`./WORK_LOG_ARCHIVED_TOGGLE_FEATURE.md`）。

### 文章/编辑与权限

- 重构：编辑器功能增强与交互升级（详见：`./ARTICLE_EDITOR_IMPROVEMENTS.md`）。
- 修复：文章权限校验与创建路由错误（详见：`./FIX_ARTICLE_PERMISSION_COMPLETE.md`、`./FIX_ARTICLE_CREATE_ROUTE_ERROR.md`）。

### 用户中心

- 修复：头像刷新不同步问题（详见：`./USER_CENTER_AVATAR_REFRESH_FIX.md`）。

### 工作周

- 重构：工作周显示与结构优化（详见：`./WORK_WEEK_IMPROVEMENTS.md`）。

### 版本日志

- 开发：v3.2 变更记录（详见：`./CHANGELOG_v3.2.md`）。

## 2025-10-28

### 文章/编辑器工具栏

- 修复：工具栏粘性样式与滚动交互问题（详见：`./ARTICLE_EDITOR_TOOLBAR_STICKY_FIX.md`）。

## 2025-10-31

### 时间线（Timeline）

- 重构：UI 增强与功能迭代收尾（详见：`./TIMELINE_UI_ENHANCEMENT.md`、`./TIMELINE_ENHANCEMENT_COMPLETE.md`、`./TIMELINE_COMPLETE_FINAL.md`、`./TIMELINE_FINAL_SUMMARY.md`）。
- 修复：Z-index 层级遮挡问题（详见：`./TIMELINE_Z_INDEX_FIX.md`）。
- 开发：截图采集、图片去重与基于时间匹配算法（详见：`./TIMELINE_SCREENSHOTS_FEATURE.md`、`./TIMELINE_IMAGE_DEDUPLICATION.md`、`./TIMELINE_TIME_BASED_IMAGE_MATCHING.md`）。

### Redis/通知/缓存

- 开发：部署指南、集成总结、通知系统设计与离线通知；持久化与快速入门（详见：`./REDIS_DEPLOYMENT_GUIDE.md`、`./REDIS_INTEGRATION_FINAL_SUMMARY.md`、`./REDIS_NOTIFICATION_SYSTEM.md`、`./REDIS_PERSISTENCE_GUIDE.md`、`./REDIS_QUICK_START.md`）。
- 修复：缓存策略最终修复（详见：`./REDIS_CACHE_FINAL_FIX.md`）。
- 重构：缓存策略与更新清单、优化指南；阶段性优化总结（详见：`./REDIS_CACHE_STRATEGY.md`、`./REDIS_CACHE_UPDATE_CHECKLIST.md`、`./REDIS_OPTIMIZATION_GUIDE.md`、`./REDIS_WEEK2_OPTIMIZATION_COMPLETE.md`）。

### 性能/任务池

- 重构：应用性能优化方案与任务池性能改进（详见：`./APPLY_PERFORMANCE_OPTIMIZATION.md`、`./TASK_POOL_PERFORMANCE_OPTIMIZATION.md`）。
- 修复：缓存失效与修复总结（详见：`./CACHE_INVALIDATION_FIX.md`、`./CACHE_FIX_SUMMARY.md`）。

### 时间/时区

- 修复：时区问题修复完成；
- 重构：时区问题分析与结论（详见：`./TIME_ZONE_FIX_COMPLETE.md`、`./TIME_ZONE_FIX_ANALYSIS.md`）。

## 2025-11-03

### Redis/通知

- 开发：迁移到 Redis 通知系统、WebSocket 升级与离线通知（详见：`./MIGRATION_TO_REDIS_NOTIFICATION.md`、`./WEBSOCKET_REDIS_NOTIFICATION_UPGRADE.md`、`./REDIS_OFFLINE_NOTIFICATION.md`）。
- 重构：系统通知逻辑优化与实现细节调整（详见：`./SYSTEM_NOTIFICATION_OPTIMIZATION.md`）。
- 修复：通知重复与后端重复推送问题（详见：`./FIX_NOTIFICATION_DUPLICATE.md`、`./FIX_BACKEND_NOTIFICATION_DUPLICATE.md`）。

### 登录/用户体验

- 重构：登录持久化与通知联动增强；新增登录动效（详见：`./LOGIN_PERSISTENCE_AND_NOTIFICATION_ENHANCEMENT.md`、`./LOGIN_XINGXIANG_ANIMATION.md`）。

### 工作日志/UI 与我的工作台

- 修复：暗黑模式细节（详见：`./WORK_LOG_DARK_MODE_FIX.md`）。
- 重构：我的工作台筛选增强与页头体验优化（详见：`./MY_WORKSPACE_FILTER_ENHANCEMENT.md`、`./PAGE_HEADER_ENHANCEMENT.md`）。

### 任务池

- 重构：筛选增强（详见：`./TASK_POOL_FILTER_ENHANCEMENT.md`）。
- 开发：导出能力与任务图片 URL 展示（详见：`./TASK_POOL_EXPORT_FEATURE.md`、`./TASK_IMAGE_URL_DISPLAY_ENHANCEMENT.md`）。

### 绩效

- 重构：个人绩效页头统一（详见：`./PERSONAL_PERFORMANCE_HEADER_UNIFICATION.md`）。

## 2025-11-04

### Markdown/预览

- 开发：新增 Markdown 导入与预览能力；
- 重构：导入流程与性能优化，最终完善并形成总结（详见：`./MARKDOWN_IMPORT_FEATURE.md`、`./MARKDOWN_IMPORT_OPTIMIZATION.md`、`./MARKDOWN_OPTIMIZATION_COMPLETE.md`、`./MARKDOWN_OPTIMIZATION_FINAL.md`、`./MARKDOWN_OPTIMIZATION_SUCCESS.md`）。

### 工作日志/文章搜索

- 重构：工作日志下的文章搜索能力增强（详见：`./WORK_LOG_ARTICLE_SEARCH_ENHANCEMENT.md`）。

### Token/会话

- 重构：Token 过期机制说明与策略统一（详见：`./TOKEN_EXPIRATION_MECHANISM.md`）。

## 2025-11-05

### 工作记录（Work Records）

- 重构：创建与详情流程简化、导航与布局优化，形成最终版（详见：`./WORK_RECORDS_CREATE_SIMPLIFY.md`、`./WORK_RECORDS_DETAIL_SIMPLIFY.md`、`./WORK_RECORDS_NAV_ENHANCEMENT.md`、`./WORK_RECORDS_LAYOUT_OPTIMIZATION.md`、`./WORK_RECORDS_FEATURE_FINAL.md`）。
- 开发：自动选择最新记录，提升录入效率（详见：`./WORK_RECORDS_AUTO_SELECT_LATEST.md`）。
- 修复：批量/导入问题、自动刷新、API 错误、滚动条、编辑模式与工具栏缺陷，以及最终版整合（详见：`./WORK_RECORDS_BATCH_AND_IMPORT_FIX.md`、`./WORK_RECORDS_AUTO_REFRESH_FIX.md`、`./WORK_RECORDS_API_FIX.md`、`./WORK_RECORDS_SCROLLBAR_FIX_FINAL.md`、`./WORK_RECORDS_EDIT_MODE_FIX.md`、`./WORK_RECORDS_TOOLBAR_FIX_FINAL.md`、`./WORK_RECORDS_LAYOUT_FIX_COMPLETE.md`）。

### 工作日志（Work Log）

- 修复：自动选中与日期逻辑问题（详见：`./WORK_LOG_AUTO_SELECT_AND_DATE_FIX.md`）。

### 登录/会话

- 开发：记住密码能力；
- 修复：Token 问题诊断与修复闭环（详见：`./REMEMBER_PASSWORD_FEATURE.md`、`./TOKEN_FIX_COMPLETE.md`、`./TOKEN_ISSUE_DIAGNOSIS.md`）。

### 文章/抽屉与预览

- 开发：信息抽屉进度与重设、创建时自动选择关联用户、安全预览替换 v-html、新增预览组件（详见：`./ARTICLE_INFO_DRAWER_PROGRESS.md`、`./ARTICLE_INFO_DRAWER_REDESIGN.md`、`./ARTICLE_CREATE_AUTO_SELECT_USERS.md`、`./REPLACE_VHTML_WITH_PREVIEW.md`、`./ART_WANG_PREVIEW_COMPONENT.md`）。
- 修复：文章链接跳转、项目文章缩进与跳转、创建路由错误（详见：`./ARTICLE_LINK_JUMP_FIX.md`、`./PROJECT_MANAGEMENT_ARTICLE_JUMP_AND_INDENT_FIX.md`、`./FIX_ARTICLE_CREATE_ROUTE_ERROR.md`）。

### 样式/通用

- 修复：通用 CSS 错误（详见：`./CSS_ERROR_FIX.md`）。

### 汇总文档

- 开发：阶段总结（详见：`./FINAL_SUMMARY.md`）。

## 2025-11-06

### PDF

- 修复：页眉/页脚导出异常（详见：`./PDF_HEADER_FOOTER_FIX.md`）。
- 开发：页眉/页脚定制能力（详见：`./PDF_HEADER_FOOTER_CUSTOMIZATION.md`）。
- 重构：版心边距与整体布局优化（详见：`./PDF_MARGIN_OPTIMIZATION.md`、`./PDF_LAYOUT_OPTIMIZATION.md`）。

### 导航/UI

- 重构：导航围绕会议/模型进行重构；增强激活态；移除顶栏与分类头；修复样式与展开逻辑；替换页头（详见：`./NAVIGATION_REFACTOR_MEETING_AND_MODEL.md`、`./NAVIGATION_ACTIVE_STATE_ENHANCEMENT.md`、`./REMOVE_TOP_BAR_OPTIMIZATION.md`、`./REMOVE_CATEGORY_HEADER.md`、`./NAVIGATION_STYLE_AND_EXPAND_FIX.md`、`./NAVIGATION_STYLE_FIX_AND_HEADER_REPLACEMENT.md`）。

### 文章模块/预览与解析

- 开发：文章摘要抽屉（详见：`./ARTICLE_SUMMARY_TO_DRAWER.md`）。
- 修复：抽屉样式、项目文章 PDF 导出问题、预览组件 Linter 与 Vue 解析器示例（详见：`./PROJECT_ARTICLE_DRAWER_STYLE_FIX.md`、`./PROJECT_ARTICLE_PDF_EXPORT_FIX.md`、`./ART_WANG_PREVIEW_LINTER_FIX.md`、`./EXAMPLE_VUE_PARSER_FIX.md`）。

### 通知

- 修复：通知自动已读逻辑（详见：`./NOTIFICATION_AUTO_READ_FIX.md`）。

### 路由

- 修复：403 异常（详见：`./ROUTE_FIX_403.md`）。

### 样式

- 修复：卡片边框（详见：`./CARD_BORDER_FIX.md`）。

### 工作记录（Work Records）

- 修复：布局缺陷（详见：`./WORK_RECORDS_LAYOUT_FIX.md`）。

### 汇总文档

- 开发：按时间的汇总文档（详见：`./DOCS_SUMMARY_BY_DATE.md`）。

---

## 附：分类口径说明

- 开发：新增功能或实现能力（含导出、特性、系统迁移/集成等）。
- 修复：缺陷修复、Bug 解决、行为一致性/可靠性改进。
- 重构：结构性调整、布局 V2、性能优化、样式/交互优化、规范化文档。

（注：该汇总以最后修改日期为准；更细粒度的具体改动点，请进入对应链接查看原始文档。）
