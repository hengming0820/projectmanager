-- 为文章编辑历史添加级联删除约束
-- 当文章被删除时，自动删除相关的编辑历史记录

-- 1. 删除旧的外键约束
ALTER TABLE article_edit_history 
DROP CONSTRAINT IF EXISTS article_edit_history_article_id_fkey;

-- 2. 添加新的外键约束（带级联删除）
ALTER TABLE article_edit_history 
ADD CONSTRAINT article_edit_history_article_id_fkey 
FOREIGN KEY (article_id) 
REFERENCES articles(id) 
ON DELETE CASCADE;

-- 说明：
-- ON DELETE CASCADE 表示当父表（articles）中的记录被删除时，
-- 子表（article_edit_history）中所有引用该记录的行也会自动被删除。

