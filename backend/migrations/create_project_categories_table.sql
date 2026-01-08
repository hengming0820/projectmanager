-- 创建项目分类表
-- 用于存储项目的自定义文章分类

-- 创建表
CREATE TABLE IF NOT EXISTS project_categories (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    icon VARCHAR(50),
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project_categories_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_project_categories_project_id ON project_categories(project_id);
CREATE INDEX IF NOT EXISTS idx_project_categories_type ON project_categories(project_id, type);
CREATE INDEX IF NOT EXISTS idx_project_categories_sort ON project_categories(project_id, sort_order);

-- 添加唯一约束：同一项目下的 type 必须唯一
CREATE UNIQUE INDEX IF NOT EXISTS idx_project_categories_unique_type ON project_categories(project_id, type);

-- 添加注释
COMMENT ON TABLE project_categories IS '项目文章分类表';
COMMENT ON COLUMN project_categories.id IS '分类ID';
COMMENT ON COLUMN project_categories.project_id IS '所属项目ID';
COMMENT ON COLUMN project_categories.name IS '分类名称（显示名）';
COMMENT ON COLUMN project_categories.type IS '分类类型标识（用于article.type）';
COMMENT ON COLUMN project_categories.icon IS '图标';
COMMENT ON COLUMN project_categories.description IS '分类描述';
COMMENT ON COLUMN project_categories.sort_order IS '排序顺序';
COMMENT ON COLUMN project_categories.created_at IS '创建时间';
COMMENT ON COLUMN project_categories.updated_at IS '更新时间';

-- 为现有项目插入默认分类
INSERT INTO project_categories (id, project_id, name, type, icon, sort_order)
SELECT 
    gen_random_uuid()::text,
    p.id,
    '会议记录',
    'meeting',
    '📋',
    1
FROM projects p
WHERE NOT EXISTS (
    SELECT 1 FROM project_categories pc 
    WHERE pc.project_id = p.id AND pc.type = 'meeting'
);

INSERT INTO project_categories (id, project_id, name, type, icon, sort_order)
SELECT 
    gen_random_uuid()::text,
    p.id,
    '模型测试',
    'model_test',
    '🧪',
    2
FROM projects p
WHERE NOT EXISTS (
    SELECT 1 FROM project_categories pc 
    WHERE pc.project_id = p.id AND pc.type = 'model_test'
);

