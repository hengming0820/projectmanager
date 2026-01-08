"""
修复项目统计字段的脚本
更新所有项目的 total_tasks, assigned_tasks, completed_tasks 字段
"""
import sys
import os

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.project import Project
from app.models.task import Task
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_project_stats():
    """修复所有项目的统计字段"""
    db: Session = SessionLocal()
    try:
        logger.info("🔄 开始修复项目统计数据...")
        
        # 获取所有项目
        projects = db.query(Project).all()
        logger.info(f"📊 找到 {len(projects)} 个项目")
        
        for project in projects:
            logger.info(f"\n📦 处理项目: {project.name} ({project.id})")
            
            # 查询该项目的所有任务
            tasks = db.query(Task).filter(Task.project_id == project.id).all()
            
            # 统计
            total = len(tasks)
            assigned = len([t for t in tasks if t.assigned_to is not None])
            completed = len([t for t in tasks if t.status == 'approved'])
            
            # 显示修复前的数据
            logger.info(f"  修复前: total_tasks={project.total_tasks}, assigned_tasks={project.assigned_tasks}, completed_tasks={project.completed_tasks}")
            
            # 更新项目字段
            project.total_tasks = total
            project.assigned_tasks = assigned
            project.completed_tasks = completed
            
            # 显示修复后的数据
            logger.info(f"  修复后: total_tasks={total}, assigned_tasks={assigned}, completed_tasks={completed}")
            
            if total > 0:
                completion_rate = round((completed / total) * 100, 2)
                logger.info(f"  ✅ 完成率: {completion_rate}%")
        
        # 提交所有更改
        db.commit()
        logger.info(f"\n✅ 所有项目统计数据已修复！")
        
    except Exception as e:
        logger.error(f"❌ 修复失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_project_stats()

