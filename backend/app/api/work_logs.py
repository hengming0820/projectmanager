from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.utils.datetime_utils import utc_now
import uuid
import logging

from app.database import get_db
from app.models.work_log import WorkWeek, WorkLogEntry, WorkLogType
from app.models.user import User
from app.schemas.work_log import (
    WorkWeekCreate, WorkWeekUpdate, WorkWeekResponse, WorkWeekQueryParams,
    WorkLogEntryCreate, WorkLogEntryUpdate, WorkLogEntrySubmit, WorkLogEntryReview,
    WorkLogEntryResponse, WorkLogQueryParams,
    WorkLogTypeCreate, WorkLogTypeUpdate, WorkLogTypeResponse,
    WorkWeekSummary, WorkWeekStatistics, WorkLogBatchCreate
)
from app.utils.security import get_current_user
from app.utils.permissions import require_permission
from app.services.pdf_export_service import work_log_pdf_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/work-logs", tags=["work-logs"])

# ==================== 工作周管理 ====================

@router.post("/weeks")
async def create_work_week(
    work_week: WorkWeekCreate,
    auto_init: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("WorkLogManagement"))
):
    """创建工作周（管理员权限）"""
    try:
        print(f"🔨 [WorkLogAPI] 创建工作周，用户: {current_user.username}, 数据: {work_week}")
        
        # 验证日期范围（确保是一个完整的工作周）
        if (work_week.week_end_date - work_week.week_start_date).days != 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="工作周必须是5天（周一到周五）"
            )
        
        # 放宽限制：允许同时间段创建多个工作周（用于覆盖不同员工集）
        # 仅当完全相同时间段且标题也相同，才自动调整标题避免冲突
        same_range_weeks = db.query(WorkWeek).filter(
            WorkWeek.week_start_date == work_week.week_start_date,
            WorkWeek.week_end_date == work_week.week_end_date,
            WorkWeek.status == "active"
        ).all()
        if same_range_weeks:
            base_title = work_week.title or "工作周"
            # 若已有同名，则追加序号后缀
            conflict_count = sum(1 for w in same_range_weeks if (w.title or "") == base_title)
            if conflict_count > 0:
                work_week_dict = work_week.dict()
                work_week_dict["title"] = f"{base_title}({conflict_count + 1})"
                work_week = WorkWeekCreate(**work_week_dict)
        
        # 创建工作周
        db_work_week = WorkWeek(
            id=str(uuid.uuid4()),
            **work_week.dict(),
            created_by=current_user.id
        )
        
        db.add(db_work_week)
        db.commit()
        db.refresh(db_work_week)
        
        print(f"✅ [WorkLogAPI] 工作周创建成功: {db_work_week.id}, 标题: {db_work_week.title}")
        
        # 可选：为指定用户生成空白条目（若 config.covered_user_ids 提供则只生成这些人）
        if auto_init:
            covered_user_ids = None
            try:
                if db_work_week.config and isinstance(db_work_week.config, dict):
                    covered_user_ids = db_work_week.config.get('covered_user_ids')
                    if covered_user_ids and not isinstance(covered_user_ids, list):
                        covered_user_ids = None
            except Exception:
                covered_user_ids = None
            if covered_user_ids:
                # 按选择的用户生成
                await _generate_entries_for_specific_users(db, db_work_week, covered_user_ids)
            else:
                await _create_default_entries_for_week(db, db_work_week)
            print(f"✅ [WorkLogAPI] 工作周创建完成，已为活跃用户初始化条目")
        else:
            print(f"✅ [WorkLogAPI] 工作周创建完成（未初始化条目）")
        
        # 构建标准响应格式
        return {
            "code": 200,
            "msg": "success",
            "data": {
                "id": db_work_week.id,
                "title": db_work_week.title,
                "week_start_date": db_work_week.week_start_date.isoformat(),
                "week_end_date": db_work_week.week_end_date.isoformat(),
                "description": db_work_week.description,
                "status": db_work_week.status,
                "config": db_work_week.config,
                "created_by": db_work_week.created_by,
                "created_at": db_work_week.created_at.isoformat(),
                "updated_at": db_work_week.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [WorkLogAPI] 创建工作周失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建工作周失败: {str(e)}"
        )

@router.get("/weeks")
async def get_work_weeks(
    params: WorkWeekQueryParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作周列表"""
    try:
        print(f"📋 [WorkLogAPI] 获取工作周列表，用户: {current_user.username}")
        
        query = db.query(WorkWeek)
        
        # 过滤条件
        if params.status:
            query = query.filter(WorkWeek.status == params.status)
        if params.date_start:
            query = query.filter(WorkWeek.week_start_date >= params.date_start)
        if params.date_end:
            query = query.filter(WorkWeek.week_end_date <= params.date_end)
        if params.created_by:
            query = query.filter(WorkWeek.created_by == params.created_by)
        
        # 分页
        total = query.count()
        print(f"📊 [WorkLogAPI] 找到 {total} 个工作周")
        
        work_weeks = query.order_by(desc(WorkWeek.week_start_date)).offset(
            (params.page - 1) * params.page_size
        ).limit(params.page_size).all()
        
        print(f"📄 [WorkLogAPI] 当前页 {len(work_weeks)} 个工作周")
        
        # 构建响应数据，添加统计信息
        week_responses = []
        for week in work_weeks:
            entries = db.query(WorkLogEntry).filter(WorkLogEntry.work_week_id == week.id).all()
            total_entries = len(entries)
            submitted_entries = len([e for e in entries if e.status in ["submitted", "approved"]])
            completion_rate = (submitted_entries / total_entries * 100) if total_entries > 0 else 0
            
            # 构建响应对象
            week_data = {
                "id": week.id,
                "title": week.title,
                "week_start_date": week.week_start_date.isoformat(),
                "week_end_date": week.week_end_date.isoformat(),
                "description": week.description,
                "status": week.status,
                "config": week.config,
                "created_by": week.created_by,
                "created_at": week.created_at.isoformat(),
                "updated_at": week.updated_at.isoformat(),
                "total_entries": total_entries,
                "submitted_entries": submitted_entries,
                "completion_rate": completion_rate
            }
            week_responses.append(week_data)
        
        result = {
            "code": 200,
            "msg": "success",
            "data": {
                "list": week_responses,
                "total": total
            }
        }
        
        print(f"✅ [WorkLogAPI] 返回响应: {len(week_responses)} 个工作周, 总计: {total}")
        return result
        
    except Exception as e:
        print(f"❌ [WorkLogAPI] 获取工作周列表失败: {e}")
        raise

@router.get("/weeks/{week_id}")
async def get_work_week(
    week_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作周详情"""
    try:
        work_week = db.query(WorkWeek).filter(WorkWeek.id == week_id).first()
        if not work_week:
            print(f"❌ [WorkLogAPI] 工作周不存在: {week_id}")
            raise HTTPException(status_code=404, detail="工作周不存在")
        
        print(f"✅ [WorkLogAPI] 找到工作周: {work_week.title}")
        
        # 添加统计信息
        entries = db.query(WorkLogEntry).filter(WorkLogEntry.work_week_id == week_id).all()
        total_entries = len(entries)
        submitted_entries = len([e for e in entries if e.status in ["submitted", "approved"]])
        completion_rate = (submitted_entries / total_entries * 100) if total_entries > 0 else 0
        
        # 构建标准响应
        result = {
            "code": 200,
            "msg": "success",
            "data": {
                "id": work_week.id,
                "title": work_week.title,
                "week_start_date": work_week.week_start_date.isoformat(),
                "week_end_date": work_week.week_end_date.isoformat(),
                "description": work_week.description,
                "status": work_week.status,
                "config": work_week.config,
                "created_by": work_week.created_by,
                "created_at": work_week.created_at.isoformat(),
                "updated_at": work_week.updated_at.isoformat(),
                "total_entries": total_entries,
                "submitted_entries": submitted_entries,
                "completion_rate": completion_rate
            }
        }
        
        print(f"✅ [WorkLogAPI] 返回工作周详情: {work_week.title}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [WorkLogAPI] 获取工作周详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取工作周详情失败: {str(e)}"
        )

@router.put("/weeks/{week_id}", response_model=WorkWeekResponse)
async def update_work_week(
    week_id: str,
    work_week_update: WorkWeekUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("WorkLogManagement"))
):
    """更新工作周"""
    
    work_week = db.query(WorkWeek).filter(WorkWeek.id == week_id).first()
    if not work_week:
        raise HTTPException(status_code=404, detail="工作周不存在")
    
    # 更新字段
    for field, value in work_week_update.dict(exclude_unset=True).items():
        setattr(work_week, field, value)
    
    work_week.updated_at = utc_now()
    db.commit()
    db.refresh(work_week)
    
    return work_week

@router.delete("/weeks/{week_id}")
async def delete_work_week(
    week_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("WorkLogManagement"))
):
    """删除工作周（硬删除，同时删除相关工作项）"""
    
    work_week = db.query(WorkWeek).filter(WorkWeek.id == week_id).first()
    if not work_week:
        raise HTTPException(status_code=404, detail="工作周不存在")
    
    print(f"🗑️ [WorkLogAPI] 开始删除工作周: {work_week.id}, 标题: {work_week.title}")
    
    # 首先删除该工作周下的所有工作日志条目
    work_entries = db.query(WorkLogEntry).filter(WorkLogEntry.work_week_id == week_id).all()
    entries_count = len(work_entries)
    
    if entries_count > 0:
        print(f"📋 [WorkLogAPI] 发现 {entries_count} 个相关工作项，开始删除...")
        for entry in work_entries:
            db.delete(entry)
        print(f"✅ [WorkLogAPI] 已删除 {entries_count} 个工作项")
    else:
        print(f"📋 [WorkLogAPI] 该工作周下没有工作项")
    
    # 然后删除工作周本身
    db.delete(work_week)
    db.commit()
    
    print(f"✅ [WorkLogAPI] 工作周删除完成: {work_week.title}")
    
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "message": "工作周及相关工作项已彻底删除",
            "deleted_entries_count": entries_count
        }
    }

# ==================== 工作日志条目管理 ====================

@router.get("/weeks/{week_id}/entries")
async def get_work_log_entries(
    week_id: str,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作周的日志条目"""
    try:
        print("🔥🔥🔥 [WorkLogAPI] 新版本API被调用！🔥🔥🔥")
        print(f"📋 [WorkLogAPI] 获取工作周日志条目，工作周ID: {week_id}, 用户: {current_user.username}")
        if user_id:
            print(f"📋 [WorkLogAPI] 筛选用户ID: {user_id}")
        
        # 验证工作周存在
        work_week = db.query(WorkWeek).filter(WorkWeek.id == week_id).first()
        if not work_week:
            print(f"❌ [WorkLogAPI] 工作周不存在: {week_id}")
            raise HTTPException(status_code=404, detail="工作周不存在")
        
        print(f"✅ [WorkLogAPI] 找到工作周: {work_week.title}")
        
        query = db.query(WorkLogEntry).options(
            joinedload(WorkLogEntry.user),
            joinedload(WorkLogEntry.reviewer)
        ).filter(WorkLogEntry.work_week_id == week_id)
        
        # 如果指定了用户ID，只返回该用户的条目
        if user_id:
            query = query.filter(WorkLogEntry.user_id == user_id)
        
        entries = query.order_by(WorkLogEntry.work_date, WorkLogEntry.user_id).all()
        print(f"📊 [WorkLogAPI] 找到 {len(entries)} 个工作日志条目")
        
        # 构建标准响应数据
        entries_data = []
        for entry in entries:
            entry_data = {
                "id": entry.id,
                "work_week_id": entry.work_week_id,
                "user_id": entry.user_id,
                "work_date": entry.work_date.isoformat(),
                "day_of_week": entry.day_of_week,
                "work_type": entry.work_type,
                "planned_hours": entry.planned_hours,
                "actual_hours": entry.actual_hours,
                "completion_rate": entry.completion_rate,
                "status": entry.status,
                "priority": entry.priority,
                "work_content": entry.work_content,
                "difficulties": entry.difficulties,
                "next_day_plan": entry.next_day_plan,
                "remarks": entry.remarks,
                "submitted_at": entry.submitted_at.isoformat() if entry.submitted_at else None,
                "reviewed_at": entry.reviewed_at.isoformat() if entry.reviewed_at else None,
                "reviewed_by": entry.reviewed_by,
                "review_comment": entry.review_comment,
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat()
            }
            
            # 添加关联信息
            if entry.user:
                entry_data["user_name"] = getattr(entry.user, 'real_name', None) or getattr(entry.user, 'username', '')
            if entry.reviewer:
                entry_data["reviewer_name"] = getattr(entry.reviewer, 'real_name', None) or getattr(entry.reviewer, 'username', '')
            
            # 获取工作类型信息
            if entry.work_type:
                work_type = db.query(WorkLogType).filter(WorkLogType.name == entry.work_type).first()
                if work_type:
                    entry_data["work_type_info"] = {
                        "id": work_type.id,
                        "name": work_type.name,
                        "description": work_type.description,
                        "color": work_type.color
                    }
            
            entries_data.append(entry_data)
        
        # 构建标准响应
        result = {
            "code": 200,
            "msg": "success",
            "data": entries_data
        }
        
        print(f"✅ [WorkLogAPI] 返回 {len(entries_data)} 个工作日志条目")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [WorkLogAPI] 获取工作日志条目失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取工作日志条目失败: {str(e)}"
        )

@router.post("/entries")
async def create_work_log_entry(
    entry: WorkLogEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建工作日志条目"""
    
    # 验证工作周存在
    work_week = db.query(WorkWeek).filter(WorkWeek.id == entry.work_week_id).first()
    if not work_week:
        raise HTTPException(status_code=404, detail="工作周不存在")
    
    # 计算星期几
    day_of_week = entry.work_date.weekday() + 1  # Python weekday: 0=Monday, 转换为 1=Monday
    
    # 移除唯一性限制 - 支持每天多个工作项
    # 注释：允许同一用户在同一日期创建多个工作日志条目
    print(f"📝 [WorkLogAPI] 允许创建多个工作项，用户: {current_user.id}, 日期: {entry.work_date}")
    
    # 创建条目
    db_entry = WorkLogEntry(
        id=str(uuid.uuid4()),
        **entry.dict(),
        user_id=current_user.id,
        day_of_week=day_of_week
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    print(f"✅ [WorkLogAPI] 工作日志条目创建成功: {db_entry.id}")
    
    # 直接返回数据库条目，与其他API保持一致
    return db_entry

@router.put("/entries/{entry_id}", response_model=WorkLogEntryResponse)
async def update_work_log_entry(
    entry_id: str,
    entry_update: WorkLogEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新工作日志条目"""
    
    entry = db.query(WorkLogEntry).filter(WorkLogEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="工作日志条目不存在")
    
    # 权限检查：只能修改自己的条目，除非是管理员
    if entry.user_id != current_user.id:
        # 检查是否有管理权限
        from app.utils.permissions import check_permission
        if not check_permission(db, current_user, "WorkLogManagement"):
            raise HTTPException(status_code=403, detail="没有权限修改此条目")
    
    # 检查状态：已提交或已审核的条目不能修改（除非是管理员）
    if entry.status in ["submitted", "approved", "rejected"] and entry.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已提交或已审核的条目不能修改"
        )
    
    # 更新字段
    for field, value in entry_update.dict(exclude_unset=True).items():
        setattr(entry, field, value)
    
    entry.updated_at = utc_now()
    db.commit()
    db.refresh(entry)
    
    return entry

@router.delete("/entries/{entry_id}")
async def delete_work_log_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除工作日志条目"""
    try:
        print(f"🗑️ [WorkLogAPI] 删除工作日志条目: {entry_id}")
        
        entry = db.query(WorkLogEntry).filter(WorkLogEntry.id == entry_id).first()
        if not entry:
            print(f"❌ [WorkLogAPI] 工作日志条目不存在: {entry_id}")
            raise HTTPException(status_code=404, detail="工作日志条目不存在")
        
        print(f"📊 [WorkLogAPI] 条目状态: {entry.status}, 用户: {entry.user_id}, 当前用户: {current_user.id}")
        
        # 权限检查：只有条目创建者或管理员可以删除
        if entry.user_id != current_user.id and current_user.role not in ['admin', 'super']:
            print(f"❌ [WorkLogAPI] 权限不足，条目用户: {entry.user_id}, 当前用户: {current_user.id}, 角色: {current_user.role}")
            raise HTTPException(status_code=403, detail="只能删除自己的工作日志或需要管理员权限")
        
        # 状态检查：只有未提交或已驳回的条目可以删除
        if entry.status not in ["pending", "rejected"]:
            print(f"❌ [WorkLogAPI] 状态错误，当前状态: {entry.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"只能删除待填写或已驳回的条目，当前状态: {entry.status}"
            )
        
        # 删除条目
        db.delete(entry)
        db.commit()
        
        print(f"✅ [WorkLogAPI] 删除成功")
        return {"message": "删除成功", "id": entry_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [WorkLogAPI] 删除失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@router.post("/entries/{entry_id}/submit", response_model=WorkLogEntryResponse)
async def submit_work_log_entry(
    entry_id: str,
    submit_data: WorkLogEntrySubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交工作日志条目"""
    try:
        print(f"🔥🔥🔥 [WorkLogAPI] 提交工作日志条目: {entry_id}")
        print(f"📋 [WorkLogAPI] 提交数据: {submit_data.dict()}")
        
        entry = db.query(WorkLogEntry).filter(WorkLogEntry.id == entry_id).first()
        if not entry:
            print(f"❌ [WorkLogAPI] 工作日志条目不存在: {entry_id}")
            raise HTTPException(status_code=404, detail="工作日志条目不存在")
        
        print(f"📊 [WorkLogAPI] 条目状态: {entry.status}, 用户: {entry.user_id}")
        
        # 权限检查
        if entry.user_id != current_user.id:
            print(f"❌ [WorkLogAPI] 权限错误，条目用户: {entry.user_id}, 当前用户: {current_user.id}")
            raise HTTPException(status_code=403, detail="只能提交自己的工作日志")
        
        # 状态检查
        if entry.status != "pending":
            print(f"❌ [WorkLogAPI] 状态错误，当前状态: {entry.status}, 期望: pending")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"只能提交待填写状态的条目，当前状态: {entry.status}"
            )
        
        # 更新条目
        print(f"📝 [WorkLogAPI] 更新条目: actual_hours={submit_data.actual_hours}, completion_rate={submit_data.completion_rate}")
        entry.actual_hours = submit_data.actual_hours
        entry.completion_rate = submit_data.completion_rate
        if submit_data.remarks:
            entry.remarks = submit_data.remarks
        entry.status = "submitted"
        entry.submitted_at = utc_now()
        entry.updated_at = utc_now()
        
        db.commit()
        db.refresh(entry)
        
        print(f"✅ [WorkLogAPI] 提交成功，新状态: {entry.status}")
        return entry
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [WorkLogAPI] 提交失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"提交失败: {str(e)}")

@router.post("/entries/{entry_id}/review", response_model=WorkLogEntryResponse)
async def review_work_log_entry(
    entry_id: str,
    review_data: WorkLogEntryReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("WorkLogReview"))
):
    """审核工作日志条目"""
    
    entry = db.query(WorkLogEntry).filter(WorkLogEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="工作日志条目不存在")
    
    # 状态检查
    if entry.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能审核已提交的条目"
        )
    
    # 更新审核信息
    entry.status = review_data.status
    entry.review_comment = review_data.review_comment
    entry.reviewed_by = current_user.id
    entry.reviewed_at = utc_now()
    entry.updated_at = utc_now()
    
    db.commit()
    db.refresh(entry)
    
    return entry

# ==================== 工作类型管理 ====================

@router.get("/types")
async def get_work_log_types(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作类型列表"""
    try:
        print("🔥🔥🔥 [WorkLogAPI] 获取工作类型列表")
        
        # 检查是否有工作类型数据，如果没有则创建默认类型
        type_count = db.query(WorkLogType).count()
        if type_count == 0:
            print("📝 [WorkLogAPI] 创建默认工作类型")
            default_types = [
                {"name": "开发", "description": "软件开发工作", "color": "#409EFF", "icon": "code", "sort_order": 1},
                {"name": "测试", "description": "软件测试工作", "color": "#67C23A", "icon": "test", "sort_order": 2},
                {"name": "会议", "description": "各类会议", "color": "#E6A23C", "icon": "meeting", "sort_order": 3},
                {"name": "学习", "description": "技术学习和培训", "color": "#909399", "icon": "study", "sort_order": 4},
                {"name": "其他", "description": "其他工作", "color": "#F56C6C", "icon": "other", "sort_order": 5}
            ]
            
            for type_data in default_types:
                work_type = WorkLogType(
                    id=str(uuid.uuid4()),
                    **type_data
                )
                db.add(work_type)
            db.commit()
        
        query = db.query(WorkLogType)
        
        if is_active is not None:
            query = query.filter(WorkLogType.is_active == is_active)
        
        types_list = query.order_by(WorkLogType.sort_order, WorkLogType.name).all()
        
        # 转换为字典格式
        types_data = []
        for work_type in types_list:
            types_data.append({
                "id": work_type.id,
                "name": work_type.name,
                "description": work_type.description,
                "color": work_type.color,
                "icon": work_type.icon,
                "is_active": work_type.is_active,
                "sort_order": work_type.sort_order,
                "created_at": work_type.created_at.isoformat(),
                "updated_at": work_type.updated_at.isoformat()
            })
        
        print(f"✅ [WorkLogAPI] 返回 {len(types_data)} 个工作类型")
        
        return {
            "code": 200,
            "msg": "success",
            "data": types_data
        }
        
    except Exception as e:
        print(f"❌ [WorkLogAPI] 获取工作类型失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取工作类型失败: {str(e)}")

@router.post("/types", response_model=WorkLogTypeResponse)
async def create_work_log_type(
    work_type: WorkLogTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("WorkLogManagement"))
):
    """创建工作类型"""
    
    # 检查名称是否已存在
    existing_type = db.query(WorkLogType).filter(WorkLogType.name == work_type.name).first()
    if existing_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="工作类型名称已存在"
        )
    
    db_work_type = WorkLogType(
        id=str(uuid.uuid4()),
        **work_type.dict()
    )
    
    db.add(db_work_type)
    db.commit()
    db.refresh(db_work_type)
    
    return db_work_type

# ==================== 统计和报表 ====================

@router.get("/weeks/{week_id}/statistics", response_model=WorkWeekStatistics)
async def get_work_week_statistics(
    week_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作周统计信息"""
    
    work_week = db.query(WorkWeek).filter(WorkWeek.id == week_id).first()
    if not work_week:
        raise HTTPException(status_code=404, detail="工作周不存在")
    
    # 获取所有条目，按用户分组
    entries = db.query(WorkLogEntry).options(
        joinedload(WorkLogEntry.user)
    ).filter(WorkLogEntry.work_week_id == week_id).all()
    
    # 按用户统计
    user_stats = {}
    for entry in entries:
        user_id = entry.user_id
        if user_id not in user_stats:
            user_stats[user_id] = {
                'user_id': user_id,
                'user_name': getattr(entry.user, 'real_name', None) or getattr(entry.user, 'username', ''),
                'entries': [],
                'total_planned_hours': 0,
                'total_actual_hours': 0,
                'completion_rates': [],
                'status_count': {'pending': 0, 'submitted': 0, 'approved': 0, 'rejected': 0},
                'work_type_hours': {}  # 按工作类型统计工时
            }
        
        user_stats[user_id]['entries'].append(entry)
        user_stats[user_id]['total_planned_hours'] += entry.planned_hours
        if entry.actual_hours:
            user_stats[user_id]['total_actual_hours'] += entry.actual_hours
            # 按工作类型统计实际工时
            work_type = entry.work_type or '其他'
            if work_type not in user_stats[user_id]['work_type_hours']:
                user_stats[user_id]['work_type_hours'][work_type] = 0
            user_stats[user_id]['work_type_hours'][work_type] += entry.actual_hours
        user_stats[user_id]['completion_rates'].append(entry.completion_rate)
        user_stats[user_id]['status_count'][entry.status] += 1
    
    # 生成用户汇总
    user_summaries = []
    for user_id, stats in user_stats.items():
        avg_completion = sum(stats['completion_rates']) / len(stats['completion_rates']) if stats['completion_rates'] else 0
        submitted_days = stats['status_count']['submitted'] + stats['status_count']['approved']
        
        summary_dict = {
            'work_week_id': week_id,
            'user_id': user_id,
            'user_name': stats['user_name'],
            'total_planned_hours': stats['total_planned_hours'],
            'total_actual_hours': stats['total_actual_hours'],
            'average_completion_rate': avg_completion,
            'submitted_days': submitted_days,
            'total_days': len(stats['entries']),
            'status_summary': stats['status_count'],
            'total_entries': len(stats['entries']),
            'work_type_hours': stats['work_type_hours']
        }
        user_summaries.append(WorkWeekSummary(**summary_dict))
    
    # 整体统计
    total_entries = len(entries)
    submitted_entries = len([e for e in entries if e.status in ['submitted', 'approved']])
    overall_completion = (submitted_entries / total_entries * 100) if total_entries > 0 else 0
    
    overall_stats = {
        'total_users': len(user_stats),
        'total_entries': total_entries,
        'submitted_entries': submitted_entries,
        'completion_rate': overall_completion,
        'total_planned_hours': sum(e.planned_hours for e in entries),
        'total_actual_hours': sum(e.actual_hours or 0 for e in entries)
    }
    
    return WorkWeekStatistics(
        work_week=work_week,
        user_summaries=user_summaries,
        overall_stats=overall_stats
    )

# ==================== 辅助函数 ====================

async def _create_default_entries_for_week(db: Session, work_week: WorkWeek):
    """为工作周创建默认的工作日志条目"""
    
    # 获取所有活跃用户
    active_users = db.query(User).filter(User.status == "active").all()
    
    # 为每个用户创建5天的工作日志条目
    for user in active_users:
        for i in range(5):  # 周一到周五
            work_date = work_week.week_start_date + timedelta(days=i)
            day_of_week = i + 1  # 1=周一, 5=周五
            
            entry = WorkLogEntry(
                id=str(uuid.uuid4()),
                work_week_id=work_week.id,
                user_id=user.id,
                work_date=work_date,
                day_of_week=day_of_week,
                status="pending"
            )
            db.add(entry)
    
    db.commit()

async def _generate_entries_for_specific_users(db: Session, work_week: WorkWeek, user_ids: list[str]):
    from app.models.user import User
    # 仅为指定用户生成 5 天 pending 条目
    for user_id in user_ids:
        for i in range(5):
            work_date = work_week.week_start_date + timedelta(days=i)
            day_of_week = i + 1
            entry = WorkLogEntry(
                id=str(uuid.uuid4()),
                work_week_id=work_week.id,
                user_id=user_id,
                work_date=work_date,
                day_of_week=day_of_week,
                status="pending"
            )
            db.add(entry)
    db.commit()

@router.post("/weeks/{week_id}/generate-entries")
async def generate_entries_for_week(
    week_id: str,
    user_ids: Optional[List[str]] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("WorkLogManagement"))
):
    """为指定用户生成工作周条目
    
    请求体示例:
    {
        "user_ids": ["user1", "user2", "user3"]
    }
    """
    
    work_week = db.query(WorkWeek).filter(WorkWeek.id == week_id).first()
    if not work_week:
        raise HTTPException(status_code=404, detail="工作周不存在")
    
    # 如果没有指定用户，则为所有活跃用户生成
    if not user_ids:
        users = db.query(User).filter(User.status == "active").all()
        user_ids = [user.id for user in users]
    
    # 为指定用户生成条目
    generated_count = 0
    for user_id in user_ids:
        for i in range(5):  # 周一到周五
            work_date = work_week.week_start_date + timedelta(days=i)
            day_of_week = i + 1
            
            # 检查是否已存在
            existing = db.query(WorkLogEntry).filter(
                WorkLogEntry.work_week_id == week_id,
                WorkLogEntry.user_id == user_id,
                WorkLogEntry.work_date == work_date
            ).first()
            
            if not existing:
                entry = WorkLogEntry(
                    id=str(uuid.uuid4()),
                    work_week_id=week_id,
                    user_id=user_id,
                    work_date=work_date,
                    day_of_week=day_of_week,
                    status="pending"
                )
                db.add(entry)
                generated_count += 1
    
    db.commit()
    
    return {"message": f"已生成 {generated_count} 个工作日志条目"}


# ==================== 工作周导出 ====================

@router.get("/weeks/{week_id}/export")
async def export_work_week_report(
    week_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出工作周统计报告PDF
    """
    try:
        logger.info(f"📊 [WorkLogExport] 开始生成工作周报告: 用户={current_user.username}, 工作周ID={week_id}")
        
        # 1. 查询工作周信息
        work_week = db.query(WorkWeek).filter(WorkWeek.id == week_id).first()
        if not work_week:
            raise HTTPException(status_code=404, detail="工作周不存在")
        
        # 2. 获取工作周统计数据（复用现有的统计接口逻辑）
        entries = db.query(WorkLogEntry).filter(
            WorkLogEntry.work_week_id == week_id
        ).options(
            joinedload(WorkLogEntry.user)
        ).all()
        
        logger.info(f"📋 [WorkLogExport] 查询到工作日志条目数: {len(entries)}")
        
        # 3. 准备工作周信息
        status_text_map = {
            'active': '进行中',
            'archived': '已归档',
            'draft': '草稿'
        }
        
        # 从日期中提取年份和周数
        year = work_week.week_start_date.year
        # 计算ISO周数
        week_number = work_week.week_start_date.isocalendar()[1]
        
        work_week_info = {
            'title': work_week.title,
            'week_start_date': work_week.week_start_date.strftime('%Y-%m-%d'),
            'week_end_date': work_week.week_end_date.strftime('%Y-%m-%d'),
            'year': year,
            'week_number': week_number,
            'status': work_week.status,
            'status_text': status_text_map.get(work_week.status, '未知')
        }
        
        # 4. 计算整体统计
        user_ids = set()
        total_actual_hours = 0.0
        work_type_hours_total = {}
        
        for entry in entries:
            if entry.user_id:
                user_ids.add(entry.user_id)
            if entry.actual_hours:
                total_actual_hours += entry.actual_hours
                
                # 统计工作类型工时（work_type 是字符串列，不是关系）
                work_type_name = entry.work_type or '未分类'
                work_type_hours_total[work_type_name] = work_type_hours_total.get(work_type_name, 0) + entry.actual_hours
        
        total_users = len(user_ids)
        total_planned_hours = total_users * 40  # 每人40小时
        efficiency = round((total_actual_hours / total_planned_hours) * 100, 1) if total_planned_hours > 0 else 0
        
        overall_stats = {
            'total_users': total_users,
            'total_planned_hours': total_planned_hours,
            'total_actual_hours': round(total_actual_hours, 1),
            'efficiency': efficiency
        }
        
        # 5. 计算用户详细统计
        user_stats_map = {}
        for entry in entries:
            if not entry.user_id:
                continue
            
            user_id = entry.user_id
            if user_id not in user_stats_map:
                user_name = entry.user.real_name if entry.user and entry.user.real_name else (entry.user.username if entry.user else '未知用户')
                user_stats_map[user_id] = {
                    'user_id': user_id,
                    'user_name': user_name,
                    'total_actual_hours': 0.0,
                    'work_type_hours': {},
                    'entries_count': 0
                }
            
            if entry.actual_hours:
                user_stats_map[user_id]['total_actual_hours'] += entry.actual_hours
                
                work_type_name = entry.work_type or '未分类'
                user_stats_map[user_id]['work_type_hours'][work_type_name] = \
                    user_stats_map[user_id]['work_type_hours'].get(work_type_name, 0) + entry.actual_hours
            
            user_stats_map[user_id]['entries_count'] += 1
        
        # 转换为列表并排序
        user_summaries = sorted(
            [
                {
                    'user_name': stats['user_name'],
                    'total_actual_hours': round(stats['total_actual_hours'], 1),
                    'work_type_hours': {k: round(v, 1) for k, v in stats['work_type_hours'].items()},
                    'entries_count': stats['entries_count']
                }
                for stats in user_stats_map.values()
            ],
            key=lambda x: x['total_actual_hours'],
            reverse=True
        )
        
        # 6. 工作类型统计（四舍五入）
        work_type_stats = {k: round(v, 1) for k, v in work_type_hours_total.items()}
        
        logger.info(f"📊 [WorkLogExport] 统计完成: 用户数={total_users}, 总工时={total_actual_hours}h")
        
        # 7. 生成PDF
        pdf_buffer = work_log_pdf_service.generate_work_week_report(
            work_week_info=work_week_info,
            overall_stats=overall_stats,
            user_summaries=user_summaries,
            work_type_stats=work_type_stats
        )
        
        # 8. 构建文件名
        filename = f"{work_week.title}_统计报告.pdf"
        filename = filename.encode('utf-8').decode('latin1')  # 处理中文文件名
        
        logger.info(f"✅ [WorkLogExport] 报告生成成功: {filename}")
        
        # 9. 返回PDF文件
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [WorkLogExport] 生成报告失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"生成报告失败: {str(e)}"
        )


@router.get("/export")
async def export_work_log_report(
    report_type: str,
    week_id: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    quarter: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    统一的工作日志导出端点
    - report_type: single (单个工作周), monthly (月度), quarterly (季度), yearly (年度)
    - week_id: 单个工作周ID (report_type=single时使用)
    - year: 年份
    - month: 月份 (report_type=monthly时使用)
    - quarter: 季度 (report_type=quarterly时使用)
    """
    try:
        logger.info(f"📊 [WorkLogExport] 开始生成{report_type}报告: 用户={current_user.username}")
        
        if report_type == 'single':
            # 单个工作周 - 复用原有逻辑
            if not week_id:
                raise HTTPException(status_code=400, detail="缺少 week_id 参数")
            return await export_work_week_report(week_id, db, current_user)
        
        # 月度/季度/年度报告
        year = year or datetime.now().year
        
        # 确定日期范围
        if report_type == 'monthly':
            if not month:
                month = datetime.now().month
            start_date = date(year, month, 1)
            # 下个月的第一天
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            period_name = f"{year}年{month}月"
            
        elif report_type == 'quarterly':
            if not quarter or quarter not in [1, 2, 3, 4]:
                quarter = (datetime.now().month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            end_month = start_month + 3
            start_date = date(year, start_month, 1)
            if end_month > 12:
                end_date = date(year + 1, end_month - 12, 1)
            else:
                end_date = date(year, end_month, 1)
            period_name = f"{year}年第{quarter}季度"
            
        elif report_type == 'yearly':
            start_date = date(year, 1, 1)
            end_date = date(year + 1, 1, 1)
            period_name = f"{year}年度"
        
        else:
            raise HTTPException(status_code=400, detail=f"不支持的报告类型: {report_type}")
        
        logger.info(f"📅 [WorkLogExport] 日期范围: {start_date} ~ {end_date}")
        
        # 查询该时间段内的所有工作周
        work_weeks = db.query(WorkWeek).filter(
            and_(
                WorkWeek.week_start_date >= start_date,
                WorkWeek.week_start_date < end_date
            )
        ).order_by(WorkWeek.week_start_date).all()
        
        if not work_weeks:
            raise HTTPException(status_code=404, detail=f"{period_name}没有工作周数据")
        
        logger.info(f"📋 [WorkLogExport] 找到 {len(work_weeks)} 个工作周")
        
        # 查询所有工作日志条目
        week_ids = [ww.id for ww in work_weeks]
        entries = db.query(WorkLogEntry).filter(
            WorkLogEntry.work_week_id.in_(week_ids)
        ).options(
            joinedload(WorkLogEntry.user)
        ).all()
        
        logger.info(f"📋 [WorkLogExport] 查询到工作日志条目数: {len(entries)}")
        
        # 准备报告信息
        work_week_info = {
            'title': f"{period_name}工作日志统计报告",
            'week_start_date': start_date.strftime('%Y-%m-%d'),
            'week_end_date': (end_date - timedelta(days=1)).strftime('%Y-%m-%d'),
            'year': year,
            'week_number': f"{len(work_weeks)}个工作周",
            'status': 'aggregated',
            'status_text': f'聚合报告（{len(work_weeks)}个工作周）'
        }
        
        # 计算整体统计
        user_ids = set()
        total_actual_hours = 0.0
        work_type_hours_total = {}
        
        for entry in entries:
            if entry.user_id:
                user_ids.add(entry.user_id)
            if entry.actual_hours:
                total_actual_hours += entry.actual_hours
                
                work_type_name = entry.work_type or '未分类'
                work_type_hours_total[work_type_name] = work_type_hours_total.get(work_type_name, 0) + entry.actual_hours
        
        total_users = len(user_ids)
        # 计划工时 = 用户数 × 工作周数 × 40小时
        total_planned_hours = total_users * len(work_weeks) * 40
        efficiency = round((total_actual_hours / total_planned_hours) * 100, 1) if total_planned_hours > 0 else 0
        
        overall_stats = {
            'total_users': total_users,
            'total_planned_hours': total_planned_hours,
            'total_actual_hours': round(total_actual_hours, 1),
            'efficiency': efficiency
        }
        
        # 计算用户详细统计
        user_stats_map = {}
        for entry in entries:
            if not entry.user_id:
                continue
            
            user_id = entry.user_id
            if user_id not in user_stats_map:
                user_name = entry.user.real_name if entry.user and entry.user.real_name else (entry.user.username if entry.user else '未知用户')
                user_stats_map[user_id] = {
                    'user_id': user_id,
                    'user_name': user_name,
                    'total_actual_hours': 0.0,
                    'work_type_hours': {},
                    'entries_count': 0
                }
            
            if entry.actual_hours:
                user_stats_map[user_id]['total_actual_hours'] += entry.actual_hours
                
                work_type_name = entry.work_type or '未分类'
                user_stats_map[user_id]['work_type_hours'][work_type_name] = \
                    user_stats_map[user_id]['work_type_hours'].get(work_type_name, 0) + entry.actual_hours
            
            user_stats_map[user_id]['entries_count'] += 1
        
        # 转换为列表并排序
        user_summaries = sorted(
            [
                {
                    'user_name': stats['user_name'],
                    'total_actual_hours': round(stats['total_actual_hours'], 1),
                    'work_type_hours': {k: round(v, 1) for k, v in stats['work_type_hours'].items()},
                    'entries_count': stats['entries_count']
                }
                for stats in user_stats_map.values()
            ],
            key=lambda x: x['total_actual_hours'],
            reverse=True
        )
        
        # 工作类型统计
        work_type_stats = {k: round(v, 1) for k, v in work_type_hours_total.items()}
        
        logger.info(f"📊 [WorkLogExport] 统计完成: {len(work_weeks)}个工作周, {total_users}个用户, 总工时={total_actual_hours}h")
        
        # 生成PDF
        pdf_buffer = work_log_pdf_service.generate_work_week_report(
            work_week_info=work_week_info,
            overall_stats=overall_stats,
            user_summaries=user_summaries,
            work_type_stats=work_type_stats
        )
        
        # 构建文件名
        filename = f"{period_name}_工作日志统计报告.pdf"
        filename = filename.encode('utf-8').decode('latin1')
        
        logger.info(f"✅ [WorkLogExport] 报告生成成功: {filename}")
        
        # 返回PDF文件
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [WorkLogExport] 生成报告失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"生成报告失败: {str(e)}"
        )
