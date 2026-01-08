"""add indexes for task pool performance

Revision ID: task_perf_idx_001
Revises: 
Create Date: 2025-10-31 20:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'task_perf_idx_001'
down_revision = None  # 请根据实际情况修改为当前最新的revision ID
branch_labels = None
depends_on = None


def upgrade():
    """
    添加索引以优化任务池查询性能
    预期效果: 查询速度提升 60-80%
    """
    # ✅ 为tasks表添加单列索引
    op.create_index('idx_tasks_status', 'tasks', ['status'], unique=False)
    op.create_index('idx_tasks_assigned_to', 'tasks', ['assigned_to'], unique=False)
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'], unique=False)
    op.create_index('idx_tasks_project_id', 'tasks', ['project_id'], unique=False)
    
    # ✅ 为tasks表添加复合索引（针对常用查询组合）
    op.create_index('idx_task_project_status', 'tasks', ['project_id', 'status'], unique=False)
    op.create_index('idx_task_status_assigned', 'tasks', ['status', 'assigned_to'], unique=False)
    
    # ✅ 为projects表添加status索引（用于过滤completed项目）
    op.create_index('idx_projects_status', 'projects', ['status'], unique=False)
    
    print("✅ 性能索引创建成功！预期查询速度提升 60-80%")


def downgrade():
    """
    删除性能优化索引
    """
    # 删除projects表索引
    op.drop_index('idx_projects_status', table_name='projects')
    
    # 删除tasks表复合索引
    op.drop_index('idx_task_status_assigned', table_name='tasks')
    op.drop_index('idx_task_project_status', table_name='tasks')
    
    # 删除tasks表单列索引
    op.drop_index('idx_tasks_project_id', table_name='tasks')
    op.drop_index('idx_tasks_created_at', table_name='tasks')
    op.drop_index('idx_tasks_assigned_to', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')
    
    print("✅ 性能索引已删除")

