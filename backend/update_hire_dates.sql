-- 更新用户入职日期SQL脚本
-- 为所有没有入职日期的用户设置默认入职日期（使用创建日期）

-- 1. 查看当前没有入职日期的用户
SELECT id, username, real_name, created_at, hire_date 
FROM users 
WHERE hire_date IS NULL;

-- 2. 为没有入职日期的用户设置入职日期（使用创建日期）
UPDATE users 
SET hire_date = DATE(created_at) 
WHERE hire_date IS NULL;

-- 3. 验证更新结果
SELECT id, username, real_name, hire_date 
FROM users 
ORDER BY hire_date;

-- 4. 如果要为特定用户设置入职日期，可以使用：
-- UPDATE users SET hire_date = '2023-06-15' WHERE username = 'your_username';

