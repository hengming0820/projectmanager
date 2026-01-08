-- 检查和设置用户入职时间的SQL脚本

-- 1. 查看所有用户的入职时间情况
SELECT 
    id,
    username,
    real_name,
    hire_date,
    created_at,
    CASE 
        WHEN hire_date IS NULL THEN '未设置'
        ELSE '已设置'
    END AS hire_date_status
FROM users
ORDER BY created_at DESC;

-- 2. 查看未设置入职时间的用户
SELECT 
    id,
    username,
    real_name,
    created_at
FROM users
WHERE hire_date IS NULL;

-- 3. 为特定用户设置入职时间（示例）
-- 替换 'your_username' 为实际的用户名，'2025-08-29' 为实际的入职日期
-- UPDATE users 
-- SET hire_date = '2025-08-29'
-- WHERE username = 'your_username';

-- 4. 批量设置：将 hire_date 为 NULL 的用户设置为其创建日期
-- 这是一个合理的默认值，假设创建账号的日期就是入职日期
-- UPDATE users 
-- SET hire_date = DATE(created_at)
-- WHERE hire_date IS NULL;

-- 5. 为当前登录的用户设置入职时间（示例：whh@xxjz.com 对应的用户）
-- UPDATE users 
-- SET hire_date = '2025-08-29'
-- WHERE email = 'whh@xxjz.com';

-- 6. 验证更新结果
-- SELECT username, real_name, hire_date FROM users WHERE username = 'your_username';

