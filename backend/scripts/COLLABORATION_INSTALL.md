# 团队协作功能安装指南

## 🎯 功能概述

团队协作文档功能提供了完整的多人协作编辑体验，包括：

- **富文本编辑器**：基于 WangEditor，支持完整工具栏
- **实时协作**：多人同时编辑，文档锁定机制
- **权限管理**：所有者、编辑者、查看者三种角色
- **版本控制**：编辑历史记录和变更追踪
- **文档管理**：分类、标签、搜索、筛选
- **统计面板**：文档数量、协作者、活动记录

## 🚀 快速安装

### 方法1：一键安装（推荐）

```bash
cd backend
python scripts/install_collaboration_feature.py
```

这个脚本会自动完成：

- ✅ 创建所有必需的数据库表
- ✅ 更新用户角色权限
- ✅ 插入示例数据

### 方法2：分步安装

#### 步骤1：创建数据库表

```bash
cd backend
python scripts/migrate_add_collaboration_tables.py
```

#### 步骤2：更新用户权限

```bash
cd backend
python scripts/update_collaboration_permissions.py
```

或者手动执行SQL（如果Python脚本失败）：

```sql
-- 为相关角色添加协作权限
UPDATE roles
SET permissions = CASE
    WHEN permissions IS NULL OR permissions = '' THEN '["CollaborationManagement"]'
    ELSE JSON_ARRAY_APPEND(permissions, '$', 'CollaborationManagement')
END
WHERE role IN ('R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER');
```

## 📊 数据库表结构

安装完成后将创建以下表：

### 1. `collaboration_documents` - 协作文档主表

```sql
- id: 文档ID
- title: 文档标题
- description: 文档描述
- content: 富文本内容
- status: 状态 (draft/active/completed/archived)
- priority: 优先级 (low/normal/high/urgent)
- owner_id: 所有者ID
- owner_name: 所有者姓名
- project_id: 关联项目ID
- category: 文档分类
- tags: 标签 (JSON)
- view_count: 查看次数
- edit_count: 编辑次数
- version: 版本号
- is_locked: 是否锁定
- locked_by: 锁定者
- created_at/updated_at: 时间戳
```

### 2. `document_collaborators` - 协作者关系表

```sql
- id: 关系ID
- document_id: 文档ID
- user_id: 用户ID
- user_name: 用户姓名
- role: 角色 (owner/editor/viewer)
- joined_at: 加入时间
- last_active_at: 最后活跃时间
```

### 3. `document_edit_history` - 编辑历史表

```sql
- id: 历史ID
- document_id: 文档ID
- editor_id: 编辑者ID
- editor_name: 编辑者姓名
- action: 操作类型 (create/update/delete/lock/unlock)
- changes_summary: 变更摘要
- content_diff: 内容差异
- version_before/after: 版本号
```

### 4. `document_comments` - 文档评论表

```sql
- id: 评论ID
- document_id: 文档ID
- user_id: 用户ID
- content: 评论内容
- position: 在文档中的位置
- parent_id: 父评论ID（回复）
```

### 5. `collaboration_sessions` - 协作会话表

```sql
- id: 会话ID
- document_id: 文档ID
- user_id: 用户ID
- session_id: 会话标识
- is_active: 是否活跃
- cursor_position: 光标位置
- last_heartbeat: 最后心跳时间
```

## 🔐 权限配置

### 角色权限

安装后，以下角色将获得协作功能权限：

- `R_SUPER` - 超级管理员
- `R_ADMIN` - 管理员
- `R_ANNOTATOR` - 标注员
- `R_REVIEWER` - 审核员

### 功能权限

- **所有者**：完全控制权限（编辑、删除、管理协作者）
- **编辑者**：可以编辑文档内容
- **查看者**：只能查看文档内容

## 🎯 使用步骤

### 1. 完成安装后重新登录

重新登录系统以刷新权限缓存

### 2. 访问协作功能

导航栏：**项目管理** → **团队协作**

### 3. 创建协作文档

- 点击"创建协作文档"
- 填写标题、描述、优先级等信息
- 添加初始协作者（可选）
- 点击"创建"

### 4. 编辑文档

- 点击文档进入详情页
- 点击"开始编辑"进入编辑模式
- 使用富文本编辑器编辑内容
- 系统会自动保存，也可手动保存

### 5. 管理协作者

- 在文档详情页点击"管理协作者"
- 添加新的协作者并设置角色
- 修改现有协作者的角色
- 移除不需要的协作者

## 🛠️ 故障排除

### 问题1：导航栏看不到"团队协作"菜单

**解决方案：**

1. 检查用户角色权限是否正确配置
2. 重新登录刷新权限缓存
3. 检查后端菜单API是否正确返回协作菜单

### 问题2：数据库表创建失败

**解决方案：**

1. 检查数据库连接是否正常
2. 确保数据库用户有创建表的权限
3. 查看具体错误信息，可能是字段类型不兼容

### 问题3：权限更新失败

**解决方案：**

1. 手动执行SQL更新权限
2. 检查 `roles` 表是否存在
3. 确认角色代码是否正确

### 问题4：前端页面加载失败

**解决方案：**

1. 检查前端路由配置是否正确
2. 确认组件文件是否存在
3. 查看浏览器控制台错误信息

## 📞 技术支持

如果遇到安装问题，请检查：

1. **数据库连接**：确保后端能正常连接数据库
2. **用户权限**：确保数据库用户有足够权限
3. **依赖包**：确保所有Python依赖已安装
4. **前端构建**：确保前端项目正常编译

## 🔄 卸载功能

如需卸载协作功能，可以：

1. **删除数据库表**：

```sql
DROP TABLE IF EXISTS collaboration_sessions;
DROP TABLE IF EXISTS document_comments;
DROP TABLE IF EXISTS document_edit_history;
DROP TABLE IF EXISTS document_collaborators;
DROP TABLE IF EXISTS collaboration_documents;
```

2. **移除权限配置**：

```sql
UPDATE roles
SET permissions = JSON_REMOVE(permissions, JSON_UNQUOTE(JSON_SEARCH(permissions, 'one', 'CollaborationManagement')))
WHERE JSON_SEARCH(permissions, 'one', 'CollaborationManagement') IS NOT NULL;
```

3. **删除前端文件**：

- `src/views/collaboration/`
- `src/api/collaborationApi.ts`
- `src/types/collaboration.ts`

---

🎉 **安装完成后，您就可以开始使用强大的团队协作文档功能了！**
