"""
绩效报告导出API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.database import get_db
from app.utils.security import get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.models.article import Article
from app.services.pdf_export_service import pdf_service, team_pdf_service, project_pdf_service
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/personal/export")
async def export_personal_performance(
    period_type: str = Query("monthly", description="报告类型: monthly或yearly"),
    year: Optional[int] = Query(None, description="年份，默认当前年"),
    month: Optional[int] = Query(None, description="月份（月度报告时使用），默认当前月"),
    user_id: Optional[str] = Query(None, description="用户ID，默认当前用户"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    导出个人绩效PDF报告
    """
    try:
        logger.info(f"📊 [PerformanceExport] 开始生成报告: 用户={current_user.username}, 类型={period_type}")
        
        # 确定目标用户
        target_user_id = user_id if user_id else current_user.id
        target_user = db.query(User).filter(User.id == target_user_id).first()
        
        if not target_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 权限检查：只有管理员可以导出其他人的报告
        if target_user_id != current_user.id and current_user.role not in ['admin', 'super', 'administrator']:
            raise HTTPException(status_code=403, detail="您没有权限导出其他用户的报告")
        
        # 确定日期范围
        year = year or datetime.now().year
        
        if period_type == "monthly":
            month = month or datetime.now().month
            start_date = datetime(year, month, 1)
            # 下个月的第一天
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
        else:  # yearly
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
        
        logger.info(f"📅 [PerformanceExport] 日期范围: {start_date} ~ {end_date}")
        
        # 1. 准备用户信息
        user_info = {
            'username': target_user.username,
            'real_name': target_user.real_name or target_user.username,
            'department': target_user.department or '未分配',
            'hire_date': target_user.hire_date.strftime('%Y年%m月%d日') if target_user.hire_date else '未知'
        }
        
        # 2. 查询任务数据
        tasks_query = db.query(Task).filter(
            and_(
                Task.assigned_to == target_user_id,
                Task.status == 'approved',  # 只统计已完成的任务
                Task.reviewed_at >= start_date,
                Task.reviewed_at < end_date
            )
        )
        
        tasks = tasks_query.all()
        logger.info(f"📋 [PerformanceExport] 查询到任务数: {len(tasks)}")
        
        # 3. 计算个人概览数据
        overview_data = _calculate_overview(tasks)
        
        # 4. 计算趋势数据
        trend_data = _calculate_trend(tasks, start_date, end_date, period_type)
        
        # 5. 计算分类统计
        category_data = _calculate_category(tasks)
        
        # 6. 生成PDF
        pdf_buffer = pdf_service.generate_personal_report(
            user_info=user_info,
            overview_data=overview_data,
            trend_data=trend_data,
            category_data=category_data,
            period_type=period_type,
            year=year,
            month=month if period_type == "monthly" else None
        )
        
        # 7. 构建文件名
        if period_type == "monthly":
            filename = f"{target_user.real_name or target_user.username}_绩效报告_{year}年{month}月.pdf"
        else:
            filename = f"{target_user.real_name or target_user.username}_年度绩效报告_{year}年.pdf"
        
        filename = filename.encode('utf-8').decode('latin1')  # 处理中文文件名
        
        logger.info(f"✅ [PerformanceExport] 报告生成成功: {filename}")
        
        # 8. 返回PDF文件
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
        logger.error(f"❌ [PerformanceExport] 生成报告失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"生成报告失败: {str(e)}"
        )


def _calculate_overview(tasks: list) -> dict:
    """计算个人概览数据"""
    if not tasks:
        return {
            'total_tasks': 0,
            'avg_time': 0,
            'fastest_time': 0,
            'daily_avg': 0,
            'daily_max': 0
        }
    
    total_tasks = len(tasks)
    
    # 计算完成时间（从分配到完成的时间）
    completion_times = []
    for task in tasks:
        if task.assigned_at and task.reviewed_at:
            time_diff = (task.reviewed_at - task.assigned_at).total_seconds() / 3600  # 转换为小时
            if time_diff > 0:
                completion_times.append(time_diff)
    
    avg_time = sum(completion_times) / len(completion_times) if completion_times else 0
    fastest_time = min(completion_times) if completion_times else 0
    
    # 计算每天完成数量
    daily_counts = {}
    for task in tasks:
        if task.reviewed_at:
            date_key = task.reviewed_at.date()
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
    
    daily_avg = sum(daily_counts.values()) / len(daily_counts) if daily_counts else 0
    daily_max = max(daily_counts.values()) if daily_counts else 0
    
    return {
        'total_tasks': total_tasks,
        'avg_time': round(avg_time, 1),
        'fastest_time': round(fastest_time, 1),
        'daily_avg': round(daily_avg, 1),
        'daily_max': daily_max
    }


def _calculate_trend(tasks: list, start_date: datetime, end_date: datetime, period_type: str) -> list:
    """计算趋势数据"""
    # 统计每天的完成数量
    daily_counts = {}
    for task in tasks:
        if task.reviewed_at:
            date_key = task.reviewed_at.date()
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
    
    # 生成完整的日期序列
    trend_data = []
    current_date = start_date.date()
    end = end_date.date()
    
    # 根据报告类型决定采样间隔
    if period_type == "yearly":
        # 年度报告：按月采样
        from calendar import monthrange
        current = start_date
        while current < end_date:
            # 计算当前月的最后一天
            last_day = monthrange(current.year, current.month)[1]
            month_end = datetime(current.year, current.month, last_day, 23, 59, 59)
            if month_end > end_date:
                month_end = end_date
            
            # 统计该月的任务数
            month_start = datetime(current.year, current.month, 1).date()
            month_end_date = month_end.date()
            month_count = sum(daily_counts.get(d, 0) for d in _date_range(month_start, month_end_date))
            
            trend_data.append({
                'date': f"{current.month}月",
                'count': month_count
            })
            
            # 移动到下一个月
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)
    else:
        # 月度报告：按天采样
        while current_date < end:
            count = daily_counts.get(current_date, 0)
            trend_data.append({
                'date': current_date.strftime('%m-%d'),
                'count': count
            })
            current_date += timedelta(days=1)
    
    return trend_data


def _calculate_category(tasks: list) -> list:
    """计算分类统计"""
    # 分类中英文映射
    category_display_map = {
        'case': '病例',
        'ai_annotation': 'AI标注'
    }
    
    sub_category_display_map = {
        'trial': '试用',
        'research': '研发',
        'paid': '收费',
        'research_ai': '科研',
        'daily': '日常'
    }
    
    category_counts = {}
    
    for task in tasks:
        # 从project中获取category和sub_category
        if hasattr(task, 'project') and task.project:
            category = getattr(task.project, 'category', None)
            sub_category = getattr(task.project, 'sub_category', None)
            
            if category:
                # 构建中文分类名称
                category_cn = category_display_map.get(category, category)
                
                if sub_category:
                    sub_category_cn = sub_category_display_map.get(sub_category, sub_category)
                    category_name = f"{category_cn}-{sub_category_cn}"
                else:
                    category_name = category_cn
            else:
                category_name = '未分类'
        else:
            category_name = '未分类'
        
        category_counts[category_name] = category_counts.get(category_name, 0) + 1
    
    # 转换为列表格式
    category_data = [
        {'category': cat, 'count': count}
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    
    return category_data


def _date_range(start_date, end_date):
    """生成日期范围"""
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


@router.get("/team/export")
async def export_team_performance(
    period_type: str = Query("monthly", description="报告类型: monthly或yearly"),
    year: Optional[int] = Query(None, description="年份，默认当前年"),
    month: Optional[int] = Query(None, description="月份（月度报告时使用），默认当前月"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    导出团队绩效PDF报告
    权限要求：管理员或审核员
    """
    try:
        logger.info(f"📊 [TeamExport] 开始生成团队报告: 用户={current_user.username}, 类型={period_type}")
        
        # 权限检查：只有管理员和审核员可以导出团队报告
        if current_user.role not in ['admin', 'super', 'administrator', 'reviewer']:
            raise HTTPException(status_code=403, detail="您没有权限导出团队报告")
        
        # 确定日期范围
        year = year or datetime.now().year
        
        if period_type == "monthly":
            month = month or datetime.now().month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
        else:  # yearly
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
        
        logger.info(f"📅 [TeamExport] 日期范围: {start_date} ~ {end_date}")
        
        # 1. 查询所有已完成的任务
        tasks_query = db.query(Task).filter(
            and_(
                Task.status == 'approved',
                Task.reviewed_at >= start_date,
                Task.reviewed_at < end_date
            )
        )
        tasks = tasks_query.all()
        logger.info(f"📋 [TeamExport] 查询到任务数: {len(tasks)}")
        
        # 2. 计算团队概览
        team_overview = _calculate_team_overview(tasks, db, start_date, end_date)
        
        # 3. 计算趋势数据
        trend_data = _calculate_trend(tasks, start_date, end_date, period_type)
        
        # 4. 计算排行榜
        ranking_data = _calculate_ranking(tasks, db)
        
        # 5. 计算成员详细数据
        member_details = _calculate_member_details(tasks, db)
        
        # 6. 计算分类统计
        category_data = _calculate_category(tasks)
        
        # 7. 生成PDF
        pdf_buffer = team_pdf_service.generate_team_report(
            team_overview=team_overview,
            trend_data=trend_data,
            ranking_data=ranking_data,
            member_details=member_details,
            category_data=category_data,
            period_type=period_type,
            year=year,
            month=month if period_type == "monthly" else None
        )
        
        # 8. 构建文件名
        if period_type == "monthly":
            filename = f"团队绩效报告_{year}年{month}月.pdf"
        else:
            filename = f"团队年度绩效报告_{year}年.pdf"
        
        filename = filename.encode('utf-8').decode('latin1')  # 处理中文文件名
        
        logger.info(f"✅ [TeamExport] 报告生成成功: {filename}")
        
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
        logger.error(f"❌ [TeamExport] 生成报告失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"生成报告失败: {str(e)}"
        )


def _calculate_team_overview(tasks: list, db: Session, start_date: datetime, end_date: datetime) -> dict:
    """计算团队概览数据"""
    # 统计参与任务的用户数（去重）
    user_ids = set()
    for task in tasks:
        if task.assigned_to:
            user_ids.add(task.assigned_to)
    
    total_members = len(user_ids)
    total_tasks = len(tasks)
    
    # 统计跳过的任务
    skipped_tasks = db.query(Task).filter(
        and_(
            Task.status == 'skipped',
            Task.skipped_at >= start_date,
            Task.skipped_at < end_date
        )
    ).count()
    
    # 统计完成的项目数（去重）
    project_ids = set()
    for task in tasks:
        if task.project_id:
            project_ids.add(task.project_id)
    
    completed_projects = len(project_ids)
    
    return {
        'total_members': total_members,
        'total_tasks': total_tasks,
        'skipped_tasks': skipped_tasks,
        'completed_projects': completed_projects
    }


def _calculate_ranking(tasks: list, db: Session) -> list:
    """计算绩效排行榜"""
    # 统计每个用户的任务数和评分
    user_stats = {}
    
    for task in tasks:
        if not task.assigned_to:
            continue
        
        user_id = task.assigned_to
        if user_id not in user_stats:
            user_stats[user_id] = {
                'user_id': user_id,
                'tasks': 0,
                'total_score': 0,
                'score_count': 0
            }
        
        user_stats[user_id]['tasks'] += 1
        if task.score:
            user_stats[user_id]['total_score'] += task.score
            user_stats[user_id]['score_count'] += 1
    
    # 计算平均评分并排序
    ranking_list = []
    for user_id, stats in user_stats.items():
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue
        
        avg_score = stats['total_score'] / stats['score_count'] if stats['score_count'] > 0 else 0
        
        ranking_list.append({
            'user_id': user_id,
            'name': user.real_name or user.username,
            'tasks': stats['tasks'],
            'score': avg_score
        })
    
    # 按任务数降序排序
    ranking_list.sort(key=lambda x: (x['tasks'], x['score']), reverse=True)
    
    # 添加排名
    for idx, item in enumerate(ranking_list, 1):
        item['rank'] = idx
    
    return ranking_list


def _calculate_member_details(tasks: list, db: Session) -> list:
    """计算成员详细数据"""
    # 分类中英文映射
    category_display_map = {
        'case': '病例',
        'ai_annotation': 'AI标注'
    }
    
    sub_category_display_map = {
        'trial': '试用',
        'research': '研发',
        'paid': '收费',
        'research_ai': '科研',
        'daily': '日常'
    }
    
    # 统计每个用户的任务数和分类
    user_stats = {}
    
    for task in tasks:
        if not task.assigned_to:
            continue
        
        user_id = task.assigned_to
        if user_id not in user_stats:
            user_stats[user_id] = {
                'user_id': user_id,
                'tasks': 0,
                'categories': {}
            }
        
        user_stats[user_id]['tasks'] += 1
        
        # 统计分类（使用中文）
        if hasattr(task, 'project') and task.project:
            category = getattr(task.project, 'category', None)
            sub_category = getattr(task.project, 'sub_category', None)
            
            if category:
                # 构建中文分类名称
                category_cn = category_display_map.get(category, category)
                
                if sub_category:
                    sub_category_cn = sub_category_display_map.get(sub_category, sub_category)
                    category_name = f"{category_cn}-{sub_category_cn}"
                else:
                    category_name = category_cn
            else:
                category_name = '未分类'
        else:
            category_name = '未分类'
        
        user_stats[user_id]['categories'][category_name] = user_stats[user_id]['categories'].get(category_name, 0) + 1
    
    # 转换为列表格式
    member_list = []
    for user_id, stats in user_stats.items():
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue
        
        # 获取主要分类（任务数最多的前3个）
        top_categories = sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)[:3]
        categories_str = ', '.join([f"{cat}({count})" for cat, count in top_categories])
        
        member_list.append({
            'user_id': user_id,
            'name': user.real_name or user.username,
            'tasks': stats['tasks'],
            'categories': categories_str or '无'
        })
    
    # 按任务数降序排序
    member_list.sort(key=lambda x: x['tasks'], reverse=True)
    
    return member_list


@router.get("/project/{project_id}/export")
async def export_project_report(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    导出项目报告PDF
    权限要求：登录用户即可
    """
    try:
        logger.info(f"📊 [ProjectExport] 开始生成项目报告: 用户={current_user.username}, 项目ID={project_id}")
        
        # 1. 查询项目信息
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 2. 查询项目的所有任务
        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        logger.info(f"📋 [ProjectExport] 查询到任务数: {len(tasks)}")
        
        # 3. 准备项目信息
        project_info = {
            'name': project.name,
            'status': project.status,
            'priority': project.priority,
            'category': project.category,
            'sub_category': project.sub_category,
            'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else '-',
            'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else '-',
            'description': project.description or '-',
            'created_at': project.created_at.isoformat() if project.created_at else '-'
        }
        
        # 4. 计算任务统计
        task_stats = {
            'total': len(tasks),
            'pending': len([t for t in tasks if t.status == 'pending']),
            'in_progress': len([t for t in tasks if t.status == 'in_progress']),
            'submitted': len([t for t in tasks if t.status == 'submitted']),
            'completed': len([t for t in tasks if t.status == 'approved']),
            'rejected': len([t for t in tasks if t.status == 'rejected']),
            'skipped': len([t for t in tasks if t.status == 'skipped']),
        }
        
        # 计算完成率
        if task_stats['total'] > 0:
            task_stats['completion_rate'] = round((task_stats['completed'] / task_stats['total']) * 100)
        else:
            task_stats['completion_rate'] = 0
        
        # 5. 计算任务状态分布
        task_status_distribution = []
        status_names = {
            'pending': '待分配',
            'in_progress': '进行中',
            'submitted': '已提交',
            'approved': '已完成',
            'rejected': '已驳回',
            'skipped': '已跳过'
        }
        
        for status_key, status_name in status_names.items():
            count = len([t for t in tasks if t.status == status_key])
            if count > 0:
                task_status_distribution.append({'name': status_name, 'value': count})
        
        # 6. 计算标注员完成分布
        annotator_stats = {}
        logger.info(f"📊 [ProjectExport] 开始统计标注员完成分布，总任务数: {len(tasks)}")
        
        for task in tasks:
            # 只统计已完成的任务
            if task.status == 'approved':
                # 优先使用 assigned_to_name
                name = task.assigned_to_name
                
                # 如果 assigned_to_name 为空或为"-"，尝试从 assigned_to 查询
                if (not name or name == '-') and task.assigned_to:
                    user = db.query(User).filter(User.id == task.assigned_to).first()
                    if user:
                        name = user.real_name or user.username
                
                # 如果有有效的标注员名称（不为空且不为"-"），则统计
                if name and name != '-':
                    annotator_stats[name] = annotator_stats.get(name, 0) + 1
                    logger.info(f"  ✅ 任务 {task.title[:20]} | 状态: {task.status} | 标注员: {name}")
                else:
                    logger.warning(f"  ⚠️ 任务 {task.title[:20]} | 状态: {task.status} | 标注员为空或为'-'！assigned_to={task.assigned_to}, assigned_to_name={task.assigned_to_name}")
        
        annotator_distribution = [
            {'name': name, 'value': count}
            for name, count in sorted(annotator_stats.items(), key=lambda x: x[1], reverse=True)
        ]
        
        logger.info(f"📊 [ProjectExport] 标注员完成分布汇总: {annotator_distribution}")
        
        # 7. 计算标注员任务统计（包含所有状态）
        annotator_task_stats_map = {}
        logger.info(f"📊 [ProjectExport] 开始统计标注员任务统计（所有状态）")
        
        for task in tasks:
            # 优先使用 assigned_to_name
            name = task.assigned_to_name
            
            # 如果 assigned_to_name 为空或为"-"，尝试从 assigned_to 查询
            if (not name or name == '-') and task.assigned_to:
                user = db.query(User).filter(User.id == task.assigned_to).first()
                if user:
                    name = user.real_name or user.username
            
            # 如果有有效的标注员名称（不为空且不为"-"），则统计
            if name and name != '-':
                if name not in annotator_task_stats_map:
                    annotator_task_stats_map[name] = {
                        'name': name,
                        'pending': 0,
                        'in_progress': 0,
                        'submitted': 0,
                        'completed': 0,
                        'rejected': 0,
                        'skipped': 0
                    }
                
                if task.status == 'pending' or task.status == 'assigned':
                    annotator_task_stats_map[name]['pending'] += 1
                elif task.status == 'in_progress':
                    annotator_task_stats_map[name]['in_progress'] += 1
                elif task.status == 'submitted':
                    annotator_task_stats_map[name]['submitted'] += 1
                elif task.status == 'approved':
                    annotator_task_stats_map[name]['completed'] += 1
                elif task.status == 'rejected':
                    annotator_task_stats_map[name]['rejected'] += 1
                elif task.status == 'skipped':
                    annotator_task_stats_map[name]['skipped'] += 1
        
        # 按总任务数排序
        annotator_task_stats = sorted(
            annotator_task_stats_map.values(),
            key=lambda x: sum([x['pending'], x['in_progress'], x['submitted'], x['completed'], x['rejected'], x['skipped']]),
            reverse=True
        )
        
        logger.info(f"📊 [ProjectExport] 标注员任务统计汇总: {[(s['name'], sum([s['pending'], s['in_progress'], s['submitted'], s['completed'], s['rejected'], s['skipped']])) for s in annotator_task_stats]}")
        
        # 8. 准备任务列表数据
        task_list = []
        for task in tasks:
            # 使用任务中存储的标注员名称
            assigned_to_name = task.assigned_to_name or '-'
            if not assigned_to_name or assigned_to_name == '-':
                if task.assigned_to:
                    user = db.query(User).filter(User.id == task.assigned_to).first()
                    if user:
                        assigned_to_name = user.real_name or user.username
            
            task_list.append({
                'title': task.title,
                'status': task.status,
                'assigned_to_name': assigned_to_name,
                'priority': task.priority,
                'created_at': task.created_at.isoformat() if task.created_at else '-'
            })
        
        # 9. 计算文章统计
        logger.info(f"📄 [ProjectExport] 开始统计项目文章")
        articles = db.query(Article).filter(Article.project_id == project_id).all()
        
        # 文章类型映射（支持更多类型）
        article_type_map = {
            'meeting': '会议记录',
            'model_test': '模型测试',
            'research': '科研文档',
            'report': '报告',
            '需求文档': '需求文档',
            '设计文档': '设计文档',
            '技术文档': '技术文档',
            '测试文档': '测试文档',
            'other': '其他'
        }
        
        # 按类型统计文章
        article_type_stats = {}
        for article in articles:
            article_type = article.type or 'other'
            # 如果映射中没有该类型，则直接使用原始类型名称
            type_name = article_type_map.get(article_type, article_type)
            
            if type_name not in article_type_stats:
                article_type_stats[type_name] = {
                    'type': type_name,
                    'count': 0,
                    'articles': []
                }
            
            article_type_stats[type_name]['count'] += 1
            article_type_stats[type_name]['articles'].append({
                'title': article.title,
                'author': article.author_name,
                'status': '已发布' if article.status == 'published' else '草稿',
                'created_at': article.created_at.isoformat() if article.created_at else '-'
            })
        
        # 转换为列表并排序
        article_stats = sorted(
            article_type_stats.values(),
            key=lambda x: x['count'],
            reverse=True
        )
        
        # 提取用于柱状图的数据
        article_chart_data = [
            {'type': stat['type'], 'count': stat['count']}
            for stat in article_stats
        ]
        
        logger.info(f"📄 [ProjectExport] 文章统计完成: 共 {len(articles)} 篇文章，{len(article_stats)} 种类型")
        
        # 10. 生成PDF
        pdf_buffer = project_pdf_service.generate_project_report(
            project_info=project_info,
            task_stats=task_stats,
            task_status_distribution=task_status_distribution,
            annotator_distribution=annotator_distribution,
            annotator_task_stats=annotator_task_stats,
            task_list=task_list,
            article_chart_data=article_chart_data,
            article_stats=article_stats
        )
        
        # 11. 构建文件名
        filename = f"{project.name}_项目报告.pdf"
        filename = filename.encode('utf-8').decode('latin1')  # 处理中文文件名
        
        logger.info(f"✅ [ProjectExport] 报告生成成功: {filename}")
        
        # 12. 返回PDF文件
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
        logger.error(f"❌ [ProjectExport] 生成报告失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"生成报告失败: {str(e)}"
        )

