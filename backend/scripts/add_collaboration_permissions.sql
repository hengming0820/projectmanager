-- 添加团队协作功能的权限配置
-- 此脚本用于更新角色权限，添加团队协作相关的菜单和功能权限

-- 更新超级管理员权限
UPDATE roles 
SET permissions = JSON_ARRAY_APPEND(
    COALESCE(permissions, '[]'), 
    '$', 
    'CollaborationManagement'
)
WHERE role IN ('R_SUPER', 'super', 'administrator', 'admin')
AND (permissions IS NULL OR JSON_SEARCH(permissions, 'one', 'CollaborationManagement') IS NULL);

-- 更新管理员权限
UPDATE roles 
SET permissions = JSON_ARRAY_APPEND(
    COALESCE(permissions, '[]'), 
    '$', 
    'CollaborationManagement'
)
WHERE role IN ('R_ADMIN', 'admin')
AND (permissions IS NULL OR JSON_SEARCH(permissions, 'one', 'CollaborationManagement') IS NULL);

-- 更新标注员权限
UPDATE roles 
SET permissions = JSON_ARRAY_APPEND(
    COALESCE(permissions, '[]'), 
    '$', 
    'CollaborationManagement'
)
WHERE role IN ('R_ANNOTATOR', 'annotator')
AND (permissions IS NULL OR JSON_SEARCH(permissions, 'one', 'CollaborationManagement') IS NULL);

-- 更新审核员权限
UPDATE roles 
SET permissions = JSON_ARRAY_APPEND(
    COALESCE(permissions, '[]'), 
    '$', 
    'CollaborationManagement'
)
WHERE role IN ('R_REVIEWER', 'reviewer')
AND (permissions IS NULL OR JSON_SEARCH(permissions, 'one', 'CollaborationManagement') IS NULL);

-- 查看更新结果
SELECT role, name, permissions 
FROM roles 
WHERE role IN ('R_SUPER', 'R_ADMIN', 'R_ANNOTATOR', 'R_REVIEWER', 'super', 'admin', 'annotator', 'reviewer')
ORDER BY role;
