-- 为 articles 表添加 project_id 字段
-- 用于关联文章到项目，支持项目管理页面的树形导航

-- 添加 project_id 字段（可为空，NULL 表示公共文章）
ALTER TABLE articles ADD COLUMN IF NOT EXISTS project_id VARCHAR(36);

-- 添加外键约束（级联删除：删除项目时自动删除相关文章）
-- PostgreSQL: 先检查约束是否存在，避免重复添加
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_articles_project'
    ) THEN
        ALTER TABLE articles 
        ADD CONSTRAINT fk_articles_project 
        FOREIGN KEY (project_id) 
        REFERENCES projects(id) 
        ON DELETE CASCADE;
    END IF;
END $$;

-- 添加索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_articles_project_id ON articles(project_id);
CREATE INDEX IF NOT EXISTS idx_articles_project_type ON articles(project_id, type);

-- 注释（PostgreSQL）
COMMENT ON COLUMN articles.project_id IS '所属项目ID，为空表示公共文章';

