-- 为现有项目添加协作文档分类
-- 执行时间: 2024-11-20
-- 说明: 为所有现有项目添加"协作文档"分类，与会议记录、模型测试并列

-- PostgreSQL 版本
-- 为所有现有项目添加协作文档分类（如果不存在）
INSERT INTO project_categories (id, project_id, name, type, icon, sort_order)
SELECT 
    gen_random_uuid()::text,
    p.id,
    '协作文档',
    'collaboration',
    '🤝',
    3
FROM projects p
WHERE NOT EXISTS (
    SELECT 1 FROM project_categories pc 
    WHERE pc.project_id = p.id AND pc.type = 'collaboration'
);

-- MySQL 版本（如果使用 MySQL，请使用这个版本）
-- INSERT INTO project_categories (id, project_id, name, type, icon, sort_order)
-- SELECT 
--     UUID(),
--     p.id,
--     '协作文档',
--     'collaboration',
--     '🤝',
--     3
-- FROM projects p
-- WHERE NOT EXISTS (
--     SELECT 1 FROM project_categories pc 
--     WHERE pc.project_id = p.id AND pc.type = 'collaboration'
-- );

-- 验证插入结果
SELECT 
    p.name AS project_name,
    pc.name AS category_name,
    pc.type AS category_type,
    pc.icon AS category_icon,
    pc.sort_order
FROM projects p
JOIN project_categories pc ON p.id = pc.project_id
WHERE pc.type = 'collaboration'
ORDER BY p.name;

-- 查看每个项目的分类数量
SELECT 
    p.name AS project_name,
    COUNT(pc.id) AS category_count,
    GROUP_CONCAT(pc.name ORDER BY pc.sort_order) AS categories
FROM projects p
LEFT JOIN project_categories pc ON p.id = pc.project_id
GROUP BY p.id, p.name
ORDER BY p.name;

