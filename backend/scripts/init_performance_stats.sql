-- 根据任务表初始化performance_stats表的SQL脚本
-- 请在PostgreSQL数据库中执行

-- 清空现有绩效统计数据
DELETE FROM performance_stats;

-- 插入基于任务数据的绩效统计
-- 用户user1的绩效统计
INSERT INTO performance_stats (id, user_id, period, date, total_tasks, completed_tasks, approved_tasks, rejected_tasks, total_score, average_score, total_hours, average_hours, created_at, updated_at)
VALUES 
  (gen_random_uuid(), 'user1', 'monthly', '2025-08', 7, 1, 1, 1, 100, 100.00, 0.00, 0.00, NOW(), NOW());

-- 用户user2的绩效统计  
INSERT INTO performance_stats (id, user_id, period, date, total_tasks, completed_tasks, approved_tasks, rejected_tasks, total_score, average_score, total_hours, average_hours, created_at, updated_at)
VALUES 
  (gen_random_uuid(), 'user2', 'monthly', '2025-08', 3, 3, 3, 0, 150, 50.00, 0.00, 0.00, NOW(), NOW());

-- 用户user3的绩效统计
INSERT INTO performance_stats (id, user_id, period, date, total_tasks, completed_tasks, approved_tasks, rejected_tasks, total_score, average_score, total_hours, average_hours, created_at, updated_at)
VALUES 
  (gen_random_uuid(), 'user3', 'monthly', '2025-08', 3, 2, 2, 0, 110, 55.00, 0.00, 0.00, NOW(), NOW());

-- 用户user4的绩效统计
INSERT INTO performance_stats (id, user_id, period, date, total_tasks, completed_tasks, approved_tasks, rejected_tasks, total_score, average_score, total_hours, average_hours, created_at, updated_at)
VALUES 
  (gen_random_uuid(), 'user4', 'monthly', '2025-08', 2, 1, 1, 0, 80, 80.00, 0.00, 0.00, NOW(), NOW());

-- 验证插入的数据
SELECT 
  user_id,
  period,
  date,
  total_tasks,
  completed_tasks,
  approved_tasks,
  rejected_tasks,
  total_score,
  average_score,
  ROUND((completed_tasks::decimal / total_tasks * 100), 2) as completion_rate
FROM performance_stats 
ORDER BY user_id, date;