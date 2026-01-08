from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.models.project import Project
from app.utils.security import get_current_user, get_current_admin_user
from app.utils.permissions import require_permission
from datetime import datetime
from app.utils.datetime_utils import utc_now
from app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("ProjectManagement"))
):
    """创建项目（需菜单权限 ProjectManagement）"""
    # 生成符合规则的项目ID：proj + YYYY + Q + NN（季度内递增，至少2位）
    now = utc_now()
    year = now.year
    quarter = (now.month - 1) // 3 + 1
    prefix = f"proj{year}{quarter}"

    # 查找该前缀下已存在的最大序号
    existing_ids = db.query(Project.id).filter(Project.id.like(f"{prefix}%")).all()
    max_index = 0
    for (pid,) in existing_ids:
        suffix = pid.replace(prefix, '')
        try:
            idx = int(suffix)
            if idx > max_index:
                max_index = idx
        except Exception:
            continue
    next_index = max_index + 1
    new_id = f"{prefix}{next_index:02d}"

    db_project = Project(
        id=new_id,
        **project_data.dict(),
        created_by=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # 为新项目创建默认分类
    try:
        from app.models.project_category import ProjectCategory
        import uuid
        
        default_categories = [
            {
                "name": "会议记录",
                "type": "meeting",
                "icon": "📋",
                "sort_order": 1
            },
            {
                "name": "模型测试",
                "type": "model_test",
                "icon": "🧪",
                "sort_order": 2
            },
            {
                "name": "协作文档",
                "type": "collaboration",
                "icon": "🤝",
                "sort_order": 3
            }
        ]
        
        for cat_data in default_categories:
            category = ProjectCategory(
                id=str(uuid.uuid4()),
                project_id=db_project.id,
                **cat_data
            )
            db.add(category)
        
        db.commit()
    except Exception as e:
        # 如果创建默认分类失败，记录日志但不影响项目创建
        print(f"警告: 为项目 {db_project.id} 创建默认分类失败: {e}")
    
    return db_project

@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[List[str]] = Query(None),
    category: str = None,
    sub_category: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取项目列表（带Redis缓存）
    - status: 项目状态筛选，支持数组（如 ['active'] 或 ['active', 'paused']）
    - 如果 status 包含 'active'，则只返回进行中的项目，过滤已完结项目
    """
    logger.info(f"📊 [ProjectAPI] 获取项目列表 - status参数: {status}, 类型: {type(status)}")
    
    # 生成缓存key
    status_key = ','.join(sorted(status)) if status else 'all'
    cache_key = f"projects:list:{status_key}:{category or 'all'}:{sub_category or 'all'}:{skip}:{limit}"
    
    # 暂时禁用缓存，因为ORM对象序列化问题
    # cached_data = cache_service.get(cache_key)
    # if cached_data:
    #     logger.info(f"🎯 项目列表缓存命中: {cache_key}")
    #     return cached_data
    
    query = db.query(Project)
    
    # 状态筛选：支持数组
    if status:
        logger.info(f"📊 [ProjectAPI] 按状态筛选项目: {status}")
        query = query.filter(Project.status.in_(status))
    else:
        logger.info(f"⚠️ [ProjectAPI] 未提供status参数，返回所有状态的项目")
    
    if category:
        query = query.filter(Project.category == category)
    if sub_category:
        query = query.filter(Project.sub_category == sub_category)
    
    projects = query.offset(skip).limit(limit).all()
    logger.info(f"✅ [ProjectAPI] 返回 {len(projects)} 个项目")
    
    # 转换为可序列化的格式（Pydantic会自动处理）
    # 注意：由于返回类型是 List[ProjectResponse]，FastAPI会自动转换
    # 但缓存时不能直接存ORM对象，需要在返回前让Pydantic转换
    # 实际上这里不应该缓存ORM对象，应该在返回后缓存
    # 暂时禁用项目列表的缓存，因为ORM对象序列化问题
    
    # TODO: 项目列表缓存需要特殊处理ORM对象
    # cache_service.set(cache_key, projects, expire=600)
    # logger.debug(f"💾 项目列表写入缓存: {cache_key}")
    
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目详情（带Redis缓存）"""
    # 生成缓存key
    cache_key = f"projects:detail:{project_id}"
    
    # 暂时禁用缓存，因为ORM对象序列化问题
    # cached_project = cache_service.get(cache_key)
    # if cached_project:
    #     logger.info(f"🎯 项目详情缓存命中: {project_id}")
    #     return cached_project
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 暂时禁用缓存，因为ORM对象序列化问题
    # cache_service.set(cache_key, project, expire=600)
    # logger.debug(f"💾 项目详情写入缓存: {project_id}")
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("ProjectManagement"))
):
    """更新项目（仅管理员）"""
    logger.info(f"📝 [ProjectAPI] 更新项目请求 - 项目ID: {project_id}, 用户: {current_user.username}")
    logger.info(f"📝 [ProjectAPI] 更新数据: {project_data.dict(exclude_unset=True)}")
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        logger.error(f"❌ [ProjectAPI] 项目不存在: {project_id}")
        raise HTTPException(status_code=404, detail="项目不存在")
    
    logger.info(f"📝 [ProjectAPI] 更新前状态: {project.status}")
    
    # 更新项目信息
    update_dict = project_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        logger.info(f"📝 [ProjectAPI] 设置字段: {field} = {value}")
        setattr(project, field, value)
    
    logger.info(f"📝 [ProjectAPI] 更新后状态（提交前）: {project.status}")
    
    db.commit()
    db.refresh(project)
    
    # ✅ 清除缓存
    cache_service.invalidate_projects_cache()
    cache_service.invalidate_project_detail_cache(project_id)
    # 项目更新可能影响任务列表，也清除任务缓存
    cache_service.invalidate_tasks_cache(project_id)
    
    logger.info(f"✅ [ProjectAPI] 更新后状态（提交后）: {project.status}")
    logger.info(f"✅ [ProjectAPI] 项目更新成功: {project_id}")
    
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("ProjectManagement"))
):
    """删除项目（仅管理员）"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    db.delete(project)
    db.commit()
    
    # ✅ 清除缓存
    cache_service.invalidate_projects_cache()
    cache_service.invalidate_project_detail_cache(project_id)
    cache_service.invalidate_tasks_cache(project_id)
    
    return {"message": "项目删除成功"}

@router.get("/{project_id}/stats")
def get_project_stats(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目统计数据（包含完结项目的真实任务统计，带Redis缓存）"""
    logger.info(f"📊 [ProjectAPI] 获取项目统计 - 项目ID: {project_id}")
    
    # 生成缓存key
    cache_key = f"projects:stats:{project_id}"
    
    # 尝试从缓存获取
    cached_stats = cache_service.get(cache_key)
    if cached_stats:
        logger.info(f"🎯 项目统计缓存命中: {project_id}")
        return cached_stats
    
    # 查询项目
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 查询该项目的所有任务（不过滤完结项目）
    from app.models.task import Task
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    # 统计任务状态
    total = len(tasks)
    pending = len([t for t in tasks if t.status == 'pending'])
    in_progress = len([t for t in tasks if t.status == 'in_progress'])
    submitted = len([t for t in tasks if t.status == 'submitted'])
    approved = len([t for t in tasks if t.status == 'approved'])
    rejected = len([t for t in tasks if t.status == 'rejected'])
    skipped = len([t for t in tasks if t.status == 'skipped'])
    
    # 计算完成率
    completion_rate = round((approved / total * 100) if total > 0 else 0, 2)
    
    logger.info(f"✅ [ProjectAPI] 项目统计完成 - 总任务: {total}, 已完成: {approved}, 完成率: {completion_rate}%")
    
    result = {
        "project_id": project_id,
        "project_name": project.name,
        "project_status": project.status,
        "total_tasks": total,
        "pending_tasks": pending,
        "in_progress_tasks": in_progress,
        "submitted_tasks": submitted,
        "approved_tasks": approved,
        "rejected_tasks": rejected,
        "skipped_tasks": skipped,
        "completion_rate": completion_rate
    }
    
    # 写入缓存（10分钟）
    cache_service.set(cache_key, result, expire=600)
    logger.debug(f"💾 项目统计写入缓存: {project_id}")
    
    return result

@router.get("/categories/stats")
def get_category_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目分类统计"""
    from sqlalchemy import func
    
    stats = db.query(
        Project.category,
        Project.sub_category,
        func.count(Project.id).label('count')
    ).group_by(
        Project.category, 
        Project.sub_category
    ).all()
    
    # 组织数据结构
    result = {
        "case": {"trial": 0, "research": 0, "paid": 0, "total": 0},
        "ai_annotation": {"research": 0, "daily": 0, "total": 0},
        "total": 0
    }
    
    for stat in stats:
        category, sub_category, count = stat
        if category and sub_category:
            if category in result:
                if sub_category in result[category]:
                    result[category][sub_category] = count
                    result[category]["total"] += count
                    result["total"] += count
    
    return result 