-- ============================================================
-- 任务池性能优化 - 索引验证 SQL 脚本
-- 在 DataGrip/DBeaver/Navicat 等数据库工具中执行
-- ============================================================

-- 方法1: 查看 tasks 表的所有索引
SHOW INDEX FROM tasks;

-- 方法2: 查看 projects 表的所有索引  
SHOW INDEX FROM projects;

-- 方法3: 查看索引详细信息（推荐）
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    NON_UNIQUE,
    GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS COLUMNS,
    INDEX_TYPE
FROM 
    information_schema.STATISTICS
WHERE 
    TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN ('tasks', 'projects')
GROUP BY 
    TABLE_NAME, INDEX_NAME, NON_UNIQUE, INDEX_TYPE
ORDER BY 
    TABLE_NAME, INDEX_NAME;

-- 方法4: 只查看我们新创建的性能优化索引
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS COLUMNS
FROM 
    information_schema.STATISTICS
WHERE 
    TABLE_SCHEMA = DATABASE()
    AND INDEX_NAME IN (
        'idx_tasks_status',
        'idx_tasks_assigned_to',
        'idx_tasks_created_at',
        'idx_tasks_project_id',
        'idx_task_project_status',
        'idx_task_status_assigned',
        'idx_projects_status'
    )
GROUP BY 
    TABLE_NAME, INDEX_NAME
ORDER BY 
    TABLE_NAME, INDEX_NAME;

-- ============================================================
-- 预期结果：应该看到以下7个索引
-- ============================================================
-- tasks 表（6个索引）:
--   ✅ idx_tasks_status          -> (status)
--   ✅ idx_tasks_assigned_to     -> (assigned_to)
--   ✅ idx_tasks_created_at      -> (created_at)
--   ✅ idx_tasks_project_id      -> (project_id)
--   ✅ idx_task_project_status   -> (project_id, status)
--   ✅ idx_task_status_assigned  -> (status, assigned_to)
--
-- projects 表（1个索引）:
--   ✅ idx_projects_status       -> (status)
-- ============================================================

-- 可选：查看索引大小（了解索引占用空间）
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    ROUND(stat_value * @@innodb_page_size / 1024 / 1024, 2) AS size_mb
FROM 
    mysql.innodb_index_stats
WHERE 
    database_name = DATABASE()
    AND table_name IN ('tasks', 'projects')
    AND stat_name = 'size'
ORDER BY 
    size_mb DESC;

-- 可选：测试索引是否被使用
-- 查看查询执行计划，确认索引是否生效
EXPLAIN SELECT * FROM tasks WHERE status = 'pending' ORDER BY created_at DESC LIMIT 20;
EXPLAIN SELECT * FROM tasks WHERE assigned_to = 'user1';
EXPLAIN SELECT * FROM tasks WHERE project_id = 'proj1' AND status = 'in_progress';

-- 预期：type 应该是 ref 或 index，不应该是 ALL
-- key 列应该显示使用了我们创建的索引名称

