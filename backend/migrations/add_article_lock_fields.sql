-- 为 articles 表添加编辑锁字段
-- 日期: 2025-10-13
-- 目的: 防止多人同时编辑同一篇文章导致数据覆盖

-- 添加编辑锁字段
ALTER TABLE articles ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS locked_by VARCHAR(50);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS locked_at TIMESTAMP WITH TIME ZONE;

-- 为已有记录设置默认值
UPDATE articles SET is_locked = FALSE WHERE is_locked IS NULL;

-- 添加注释
COMMENT ON COLUMN articles.is_locked IS '是否被锁定（有人正在编辑）';
COMMENT ON COLUMN articles.locked_by IS '锁定者用户ID';
COMMENT ON COLUMN articles.locked_at IS '锁定时间';

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_articles_is_locked ON articles(is_locked);
CREATE INDEX IF NOT EXISTS idx_articles_locked_by ON articles(locked_by);

