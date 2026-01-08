from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.performance import PerformanceStats, ProjectStats
from app.models.task import Task
from app.models.project import Project

class PerformanceService:
    def add_performance_score(
        self,
        db: Session,
        user_id: str,
        task_score: int = 1,
        period: str = "monthly"
    ) -> dict:
        """为用户增加绩效分数（在任务审核通过时调用）"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"📈 [PerformanceService] 为用户 {user_id} 增加 {task_score} 分绩效")
        
        # 获取当前时间和格式
        end_date = datetime.now()
        if period == "daily":
            date_format = "%Y-%m-%d"
        elif period == "weekly":
            date_format = "%Y-%W"
        elif period == "monthly":
            date_format = "%Y-%m"
        else:  # yearly
            date_format = "%Y"
        
        date_str = end_date.strftime(date_format)
        
        # 查找或创建绩效记录
        performance = db.query(PerformanceStats).filter(
            PerformanceStats.user_id == user_id,
            PerformanceStats.period == period,
            PerformanceStats.date == date_str
        ).first()
        
        if not performance:
            # 创建新的绩效记录
            performance = PerformanceStats(
                user_id=user_id,
                period=period,
                date=date_str,
                total_tasks=1,
                completed_tasks=1,
                approved_tasks=1,
                total_score=task_score,
                average_score=task_score
            )
            db.add(performance)
            logger.info(f"✅ [PerformanceService] 创建新的绩效记录: {performance.id}")
        else:
            # 更新现有的绩效记录
            old_score = performance.total_score
            performance.approved_tasks += 1
            performance.completed_tasks += 1
            performance.total_score += task_score
            performance.average_score = performance.total_score / performance.completed_tasks if performance.completed_tasks > 0 else 0
            logger.info(f"✅ [PerformanceService] 更新绩效记录: {old_score} -> {performance.total_score}")
        
        db.commit()
        
        return {
            "user_id": user_id,
            "added_score": task_score,
            "total_score": performance.total_score,
            "completed_tasks": performance.completed_tasks,
            "average_score": float(performance.average_score)
        }
    def calculate_user_performance(
        self, 
        db: Session, 
        user_id: str, 
        period: str = "monthly"
    ) -> dict:
        """计算用户绩效"""
        # 获取时间范围
        end_date = datetime.now()
        if period == "daily":
            start_date = end_date - timedelta(days=1)
            date_format = "%Y-%m-%d"
        elif period == "weekly":
            start_date = end_date - timedelta(weeks=1)
            date_format = "%Y-%W"
        elif period == "monthly":
            start_date = end_date - timedelta(days=30)
            date_format = "%Y-%m"
        else:  # yearly
            start_date = end_date - timedelta(days=365)
            date_format = "%Y"
        
        # 查询任务统计
        tasks = db.query(Task).filter(
            Task.assigned_to == user_id,
            Task.created_at >= start_date,
            Task.created_at <= end_date
        ).all()
        
        # 计算绩效
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == "approved"])
        
        # 每完成一个任务+1分
        total_score = completed_tasks
        average_score = 1 if completed_tasks > 0 else 0
        
        # 保存或更新绩效统计
        performance = db.query(PerformanceStats).filter(
            PerformanceStats.user_id == user_id,
            PerformanceStats.period == period,
            PerformanceStats.date == end_date.strftime(date_format)
        ).first()
        
        if not performance:
            performance = PerformanceStats(
                user_id=user_id,
                period=period,
                date=end_date.strftime(date_format),
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                approved_tasks=completed_tasks,
                total_score=total_score,
                average_score=average_score
            )
            db.add(performance)
        else:
            performance.total_tasks = total_tasks
            performance.completed_tasks = completed_tasks
            performance.approved_tasks = completed_tasks
            performance.total_score = total_score
            performance.average_score = average_score
        
        db.commit()
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "total_score": total_score,
            "average_score": average_score,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def calculate_project_stats(self, db: Session, project_id: str) -> ProjectStats:
        """计算项目统计"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # 查询项目任务
        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        
        # 计算统计
        total_tasks = len(tasks)
        pending_tasks = len([t for t in tasks if t.status == "pending"])
        in_progress_tasks = len([t for t in tasks if t.status == "in_progress"])
        completed_tasks = len([t for t in tasks if t.status in ["submitted", "approved"]])
        approved_tasks = len([t for t in tasks if t.status == "approved"])
        rejected_tasks = len([t for t in tasks if t.status == "rejected"])
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        average_score = sum(t.score or 0 for t in tasks) / total_tasks if total_tasks > 0 else 0
        
        # 保存或更新项目统计
        stats = db.query(ProjectStats).filter(ProjectStats.project_id == project_id).first()
        if not stats:
            stats = ProjectStats(
                project_id=project_id,
                total_tasks=total_tasks,
                pending_tasks=pending_tasks,
                in_progress_tasks=in_progress_tasks,
                completed_tasks=completed_tasks,
                approved_tasks=approved_tasks,
                rejected_tasks=rejected_tasks,
                completion_rate=completion_rate,
                average_score=average_score
            )
            db.add(stats)
        else:
            stats.total_tasks = total_tasks
            stats.pending_tasks = pending_tasks
            stats.in_progress_tasks = in_progress_tasks
            stats.completed_tasks = completed_tasks
            stats.approved_tasks = approved_tasks
            stats.rejected_tasks = rejected_tasks
            stats.completion_rate = completion_rate
            stats.average_score = average_score
        
        db.commit()
        return stats

# 全局绩效服务实例
performance_service = PerformanceService() 