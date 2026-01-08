from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.performance import PerformanceStatsResponse, ProjectStatsResponse, PersonalPerformanceResponse
from app.models.performance import PerformanceStats, ProjectStats
from app.models.project import Project
from app.utils.security import get_current_user, get_current_admin_user
from app.utils.permissions import require_permission
from app.services.performance_service import performance_service
from app.services.stats_cache_service import stats_cache_service
import logging

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/stats")
def get_performance_stats(
    period: str = "monthly",
    user_id: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("TeamPerformance"))
):
    """获取绩效统计（需菜单权限 TeamPerformance，带缓存）"""
    from app.models.user import User
    
    # 尝试从缓存获取（团队绩效）
    if not user_id:
        cached_data = stats_cache_service.get_performance_stats(period=period)
        if cached_data:
            logger.info(f"🎯 [PerformanceAPI] 团队绩效缓存命中: {period}")
            return {
                "code": 200,
                "msg": "成功",
                "data": cached_data
            }
    
    # 使用 JOIN 查询获取绩效数据和用户信息
    query = db.query(PerformanceStats, User).join(
        User, PerformanceStats.user_id == User.id
    ).filter(PerformanceStats.period == period)
    
    if user_id:
        query = query.filter(PerformanceStats.user_id == user_id)
    
    results = query.all()
    
    # 构建返回数据
    result_data = {
        "list": [{
            "id": stat.id,
            "user_id": stat.user_id,
            "username": user.username,
            "real_name": user.real_name,
            "avatar": user.avatar_url,
            "period": stat.period,
            "date": stat.date,
            "total_tasks": stat.total_tasks,
            "completed_tasks": stat.completed_tasks,
            "approved_tasks": stat.approved_tasks,
            "rejected_tasks": stat.rejected_tasks,
            "total_score": stat.total_score,
            "average_score": float(stat.average_score),
            "total_hours": float(stat.total_hours),
            "average_hours": float(stat.average_hours),
            "created_at": stat.created_at.isoformat(),
            "updated_at": stat.updated_at.isoformat()
        } for stat, user in results],
        "total": len(results)
    }
    
    # 写入缓存（团队绩效）
    if not user_id:
        stats_cache_service.set_performance_stats(result_data, period=period)
        logger.info(f"💾 [PerformanceAPI] 团队绩效已缓存: {period}")
    
    # 返回统一格式，包含用户信息
    return {
        "code": 200,
        "msg": "成功",
        "data": result_data
    }

@router.get("/personal")
def get_personal_performance(
    period: str = "monthly",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取个人绩效（带缓存）"""
    logger.info(f"📈 [PerformanceAPI] 获取个人绩效: 用户 {current_user.username}, 周期: {period}")
    
    try:
        # 尝试从缓存获取
        cached_data = stats_cache_service.get_performance_stats(
            user_id=current_user.id, 
            period=period
        )
        if cached_data:
            logger.info(f"🎯 [PerformanceAPI] 个人绩效缓存命中: 用户 {current_user.username}")
            return {
                "code": 200,
                "msg": "成功",
                "data": cached_data
            }
        
        # 缓存未命中，计算绩效
        performance_data = performance_service.calculate_user_performance(
            db=db, 
            user_id=current_user.id, 
            period=period
        )
        
        # 写入缓存
        stats_cache_service.set_performance_stats(
            performance_data,
            user_id=current_user.id,
            period=period
        )
        
        logger.info(f"✅ [PerformanceAPI] 个人绩效计算成功: 用户 {current_user.username}")
        logger.info(f"📉 [PerformanceAPI] 绩效数据: {performance_data}")
        
        # 返回统一格式
        return {
            "code": 200,
            "msg": "成功",
            "data": performance_data
        }
    except Exception as e:
        logger.error(f"❌ [PerformanceAPI] 个人绩效计算失败: 用户 {current_user.username}, 错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"绩效计算失败: {str(e)}"
        )

@router.get("/project/{project_id}/stats", response_model=ProjectStatsResponse)
def get_project_stats(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("ProjectDashboard"))
):
    """获取项目统计（需菜单权限 ProjectDashboard，带缓存）"""
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 尝试从缓存获取
    cached_stats = stats_cache_service.get_project_stats(project_id)
    if cached_stats:
        logger.info(f"🎯 [PerformanceAPI] 项目统计缓存命中: {project_id}")
        return cached_stats
    
    # 统一权限管理：通过菜单权限控制，不再硬编码角色检查
    # 如果用户能访问 ProjectDashboard，就能查看所有项目数据
    
    stats = performance_service.calculate_project_stats(db, project_id)
    
    # 写入缓存
    stats_dict = stats.dict() if hasattr(stats, 'dict') else stats
    stats_cache_service.set_project_stats(project_id, stats_dict)
    logger.info(f"💾 [PerformanceAPI] 项目统计已缓存: {project_id}")
    
    return stats

@router.get("/dashboard")
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("ProjectDashboard"))
):
    """获取仪表板数据（需菜单权限 ProjectDashboard，带缓存）"""
    from app.models.task import Task
    from app.models.user import User
    
    # 尝试从缓存获取
    cached_dashboard = stats_cache_service.get_dashboard_stats()
    if cached_dashboard:
        logger.info("🎯 [PerformanceAPI] 仪表板统计缓存命中")
        return cached_dashboard
    
    # 基础统计
    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == "active").count()
    total_tasks = db.query(Task).count()
    pending_tasks = db.query(Task).filter(Task.status == "pending").count()
    completed_tasks = db.query(Task).filter(Task.status.in_(["submitted", "approved"])).count()
    total_users = db.query(User).count()
    
    # 项目进度
    projects = db.query(Project).all()
    project_progress = []
    for project in projects:
        project_tasks = db.query(Task).filter(Task.project_id == project.id).all()
        total_project_tasks = len(project_tasks)
        completed_project_tasks = len([t for t in project_tasks if t.status in ["submitted", "approved"]])
        completion_rate = (completed_project_tasks / total_project_tasks * 100) if total_project_tasks > 0 else 0
        
        project_progress.append({
            "id": project.id,
            "name": project.name,
            "progress": completion_rate,
            "total_tasks": total_project_tasks,
            "completed_tasks": completed_project_tasks
        })
    
    dashboard_data = {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "total_users": total_users,
        "project_progress": project_progress
    }
    
    # 写入缓存
    stats_cache_service.set_dashboard_stats(dashboard_data)
    logger.info("💾 [PerformanceAPI] 仪表板统计已缓存")
    
    return dashboard_data 