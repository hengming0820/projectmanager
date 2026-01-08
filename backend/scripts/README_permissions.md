# 团队协作功能权限配置

## 问题说明

团队协作功能已经在后端菜单API中配置，但用户角色可能缺少相应的访问权限。

## 解决方案

### 方法1：通过数据库直接更新（推荐）

连接到您的数据库，执行以下SQL语句来为相关角色添加团队协作权限：

```sql
-- 查看当前角色和权限
SELECT id, name, role, permissions FROM roles;

-- 为超级管理员添加协作权限
UPDATE roles
SET permissions = CASE
    WHEN permissions IS NULL OR permissions = '' THEN '["CollaborationManagement"]'
    ELSE JSON_ARRAY_APPEND(permissions, '$', 'CollaborationManagement')
END
WHERE role IN ('R_SUPER', 'super', 'administrator');

-- 为管理员添加协作权限
UPDATE roles
SET permissions = CASE
    WHEN permissions IS NULL OR permissions = '' THEN '["CollaborationManagement"]'
    ELSE JSON_ARRAY_APPEND(permissions, '$', 'CollaborationManagement')
END
WHERE role IN ('R_ADMIN', 'admin');

-- 为标注员添加协作权限
UPDATE roles
SET permissions = CASE
    WHEN permissions IS NULL OR permissions = '' THEN '["CollaborationManagement"]'
    ELSE JSON_ARRAY_APPEND(permissions, '$', 'CollaborationManagement')
END
WHERE role IN ('R_ANNOTATOR', 'annotator');

-- 为审核员添加协作权限
UPDATE roles
SET permissions = CASE
    WHEN permissions IS NULL OR permissions = '' THEN '["CollaborationManagement"]'
    ELSE JSON_ARRAY_APPEND(permissions, '$', 'CollaborationManagement')
END
WHERE role IN ('R_REVIEWER', 'reviewer');

-- 验证更新结果
SELECT role, name, permissions FROM roles
WHERE role IN ('R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER');
```

### 方法2：如果数据库不支持JSON函数

如果您的数据库版本较老，不支持JSON函数，可以手动更新：

```sql
-- 查看当前权限
SELECT id, name, role, permissions FROM roles;

-- 手动更新每个角色的权限（示例）
-- 假设超级管理员当前权限为 '["Dashboard", "System"]'
UPDATE roles
SET permissions = '["Dashboard", "System", "CollaborationManagement"]'
WHERE role = 'R_SUPER';

-- 根据实际情况调整其他角色的权限
```

### 方法3：通过Python脚本（如果可以运行）

如果您可以运行Python脚本，可以使用我们提供的脚本：

```bash
cd backend
python scripts/update_collaboration_permissions.py
```

## 验证步骤

1. 更新权限后，用户需要重新登录以刷新权限缓存
2. 登录后应该能在"项目管理"菜单下看到"团队协作"选项
3. 点击"团队协作"应该能正常访问页面

## 权限说明

- `CollaborationManagement`: 团队协作管理页面的访问权限
- 该权限控制用户是否能看到和访问团队协作功能

## 注意事项

1. 权限更新后需要用户重新登录
2. 确保数据库连接正常
3. 建议先在测试环境验证
4. 如有问题，可以回滚权限配置
