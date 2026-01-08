from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate, UserCreate, UserProfileUpdate, UserProfileResponse
from app.models.user import User
from app.utils.security import get_current_admin_user, get_current_user, verify_password, get_password_hash
from app.utils.permissions import require_permission
from fastapi import UploadFile, File
from app.utils.file_utils import file_service
import logging
from app.services.user_cache_service import user_cache_service

# 配置日志
logger = logging.getLogger(__name__)

# 添加redirect_slashes=False避免重定向问题
router = APIRouter(redirect_slashes=False)
@router.get("/me/profile", response_model=UserProfileResponse)
def get_my_profile(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 使用 Pydantic 的 model_validate 自动映射所有字段，包括 hire_date
    user_response = UserProfileResponse.model_validate(user)
    
    # 添加调试日志
    logger.info(f"👤 [UsersAPI] /me/profile - user.hire_date: {user.hire_date}")
    logger.info(f"📋 [UsersAPI] /me/profile - UserProfileResponse: {user_response.model_dump()}")
    
    return user_response

@router.put("/me/profile", response_model=UserProfileResponse)
def update_my_profile(payload: UserProfileUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    import json
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if payload.real_name is not None:
        user.real_name = payload.real_name
    if payload.email is not None:
        user.email = payload.email
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    if payload.department is not None:
        user.department = payload.department
    if payload.tags is not None:
        user.tags = json.dumps(payload.tags, ensure_ascii=False)
    db.commit()
    db.refresh(user)
    
    # ✅ 清除用户缓存
    user_cache_service.invalidate_user_cache(user.id)
    
    # 返回包含解析后标签的数据
    user_dict = {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "email": user.email,
        "role": user.role,
        "avatar_url": user.avatar_url,
        "department": user.department,
        "status": user.status,
        "tags": json.loads(user.tags) if user.tags else [],
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }
    return user_dict

@router.post("/me/avatar")
async def upload_my_avatar(file: UploadFile = File(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    url = await file_service.upload_avatar(current_user.id, file)
    user.avatar_url = url
    db.commit()
    db.refresh(user)
    
    # ✅ 清除用户缓存
    user_cache_service.invalidate_user_cache(user.id)
    
    # 返回简单的响应，避免 tags 字段的序列化问题
    return {
        "code": 200,
        "message": "头像上传成功",
        "avatar_url": url
    }

@router.put("/me/change-password")
def change_my_password(
    payload: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """修改当前用户密码：需要提供 current_password 与 new_password"""
    current_password = payload.get("current_password")
    new_password = payload.get("new_password")

    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="缺少必要参数")

    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 校验当前密码
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="当前密码不正确")

    # 更新为新密码
    user.password_hash = get_password_hash(new_password)
    db.commit()
    
    # ✅ 清除用户缓存
    user_cache_service.invalidate_user_cache(user.id)
    
    return { "code": 200, "msg": "密码修改成功", "data": None }

@router.get("/basic")
def get_users_basic(
    status: str | None = None,
    size: int = 9999,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取用户基本信息列表（所有已登录用户可访问，用于工作日志等功能，带Redis缓存）"""
    from app.models.role import Role
    
    # 使用用户缓存服务
    if status == "active" or not status:
        user_list = user_cache_service.get_active_users(db)
        
        # 如果指定了size限制
        if size < len(user_list):
            user_list = user_list[:size]
        
        # JOIN 角色表，获取角色中文名称
        # 获取所有角色信息
        roles_dict = {r.role: r.name for r in db.query(Role).all()}
        
        # 为每个用户添加角色中文名称
        for user in user_list:
            user['role_name'] = roles_dict.get(user.get('role'), user.get('role', ''))
        
        # 返回统一格式
        return {
            "code": 200,
            "msg": "成功",
            "data": {
                "list": user_list,
                "total": len(user_list)
            }
        }
    
    # 非active状态，直接查询数据库并 JOIN 角色表
    query = db.query(
        User.id, 
        User.username, 
        User.real_name, 
        User.department, 
        User.role, 
        User.status,
        Role.name.label('role_name')
    ).outerjoin(Role, User.role == Role.role)
    
    if status:
        query = query.filter(User.status == status)
    
    # 获取用户数据
    users = query.limit(size).all()
    
    # 转换为字典列表
    user_list = [
        {
            "id": u.id,
            "username": u.username,
            "real_name": u.real_name,
            "department": u.department,
            "role": u.role,
            "role_name": u.role_name or u.role,  # 如果没有匹配的角色名称，使用编码
            "status": u.status
        }
        for u in users
    ]
    
    # 返回统一格式
    return {
        "code": 200,
        "msg": "成功",
        "data": {
            "list": user_list,
            "total": len(user_list)
        }
    }

@router.get("/simple")
def get_simple_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # 所有登录用户都可以访问
):
    """获取简化的用户列表（所有登录用户可访问，仅返回基本信息）"""
    users = db.query(User).filter(User.status == "active").all()
    return {
        "code": 200,
        "msg": "成功",
        "data": [
            {
                "id": u.id,
                "username": u.username,
                "real_name": u.real_name,
                "department": u.department
            }
            for u in users
        ]
    }

@router.get("/")
def get_users(
    current: int = 1,  # 前端传递的页码
    size: int = 20,    # 前端传递的页大小
    skip: int = 0,
    limit: int = 100,
    role: str | None = None,
    status: str | None = None,
    level: str | None = None,  # 前端传递的level参数
    name: str | None = None,   # 新增：按用户名/真实姓名模糊查询
    department: str | None = None,  # 新增：按部门筛选
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("UserManagement"))
):
    """获取用户列表（仅管理员）"""
    # 将前端分页参数转换为后端参数
    actual_skip = (current - 1) * size
    actual_limit = size
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    if name:
        like = f"%{name}%"
        query = query.filter((User.username.like(like)) | (User.real_name.like(like)))
    if department:
        query = query.filter(User.department == department)
    if level:  # 处理前端的level参数
        if level == 'vip':
            # 假设vip对应admin角色
            query = query.filter(User.role == 'admin')
    
    # 获取总数
    total = query.count()
    
    # 获取分页数据
    users = query.offset(actual_skip).limit(actual_limit).all()
    
    # 返回统一格式
    return {
        "code": 200,
        "msg": "成功",
        "data": {
            "list": users,
            "total": total,
            "current": current,
            "size": size
        }
    }

@router.get("/{user_id}")
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("UserManagement"))
):
    """获取用户详情（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "code": 200,
        "msg": "成功",
        "data": user
    }

@router.post("/")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("UserManagement"))
):
    """创建用户（仅管理员）"""
    from app.utils.security import get_password_hash
    
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    # 生成自增式字符串ID: user1, user2, ...
    try:
        existing_ids = [row[0] for row in db.query(User.id).filter(User.id.like('user%')).all()]
        numbers = [int(x.replace('user', '')) for x in existing_ids if x.replace('user', '').isdigit()]
        next_number = (max(numbers) + 1) if numbers else 1
        next_user_id = f"user{next_number}"
    except Exception:
        # 回退使用UUID默认
        next_user_id = None

    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    from datetime import date
    db_user = User(
        id=next_user_id,
        username=user_data.username,
        real_name=user_data.real_name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        department=user_data.department,
        avatar_url=user_data.avatar_url,
        hire_date=user_data.hire_date if user_data.hire_date else date.today()  # 如果没有提供，使用今天
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # ✅ 清除用户列表缓存
    user_cache_service.invalidate_all_users_cache()
    
    return {
        "code": 200,
        "msg": "用户创建成功",
        "data": db_user
    }

@router.put("/{user_id}")
def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("UserManagement"))
):
    """更新用户信息（仅管理员）"""
    logger.info(f"📝 [UsersAPI] 开始更新用户: user_id={user_id}")
    logger.info(f"📦 [UsersAPI] 接收到的数据: {user_data.model_dump(exclude_unset=True)}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    logger.info(f"🔍 [UsersAPI] 更新前的 hire_date: {user.hire_date}")
    
    # 检查是否尝试修改自己的角色或状态
    if user_id == current_user.id and user_data.role:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")
    
    # 更新用户信息
    update_data = user_data.model_dump(exclude_unset=True)
    logger.info(f"🔄 [UsersAPI] 准备更新的字段: {list(update_data.keys())}")
    
    for field, value in update_data.items():
        old_value = getattr(user, field, None)
        setattr(user, field, value)
        logger.info(f"  ✏️ {field}: {old_value} -> {value}")
    
    db.commit()
    db.refresh(user)
    
    # ✅ 清除用户缓存
    user_cache_service.invalidate_user_cache(user_id)
    
    logger.info(f"✅ [UsersAPI] 更新后的 hire_date: {user.hire_date}")
    logger.info(f"✅ [UsersAPI] 用户更新完成: {user_id}")
    
    return {
        "code": 200,
        "msg": "用户更新成功",
        "data": user
    }

@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("UserManagement"))
):
    """删除用户（仅管理员）"""
    logger.info(f"🗑️ [UsersAPI] 收到删除用户请求: user_id={user_id}")
    
    # 不能删除自己
    if user_id == current_user.id:
        logger.warning(f"⚠️ [UsersAPI] 用户尝试删除自己: {user_id}")
        raise HTTPException(status_code=400, detail="不能删除自己的账户")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"⚠️ [UsersAPI] 用户不存在: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查用户关联的数据
    from app.models.task import Task, TaskAttachment
    from app.models.project import Project
    from app.models.article import Article, ArticleEditHistory
    from app.models.work_log import WorkLogEntry, WorkWeek
    from app.models.performance import PerformanceStats
    from app.models.collaboration import CollaborationDocument, DocumentCollaborator
    
    # 查找系统管理员（用于接管被删除用户创建的数据）
    system_admin = db.query(User).filter(
        User.role == "admin",
        User.status == "active",
        User.id != user_id  # 不能是要删除的用户自己
    ).first()
    
    if not system_admin:
        logger.error(f"❌ [UsersAPI] 没有找到可用的系统管理员来接管数据")
        raise HTTPException(
            status_code=500, 
            detail="系统错误：没有找到可用的管理员账号来接管数据，请先确保系统中至少有一个活跃的管理员账号"
        )
    
    logger.info(f"ℹ️ [UsersAPI] 使用管理员 {system_admin.username} ({system_admin.id}) 接管数据")
    
    # 统计需要转移的数据（created_by/author_id 等 NOT NULL 字段）
    transfer_info = []
    auto_handle_info = []
    
    # 1. 统计用户创建的项目（将转移给管理员）
    created_projects_count = db.query(Project).filter(Project.created_by == user_id).count()
    if created_projects_count > 0:
        transfer_info.append(f"创建的项目: {created_projects_count} 个")
    
    # 2. 统计用户创建的任务（将转移给管理员）
    created_tasks_count = db.query(Task).filter(Task.created_by == user_id).count()
    if created_tasks_count > 0:
        transfer_info.append(f"创建的任务: {created_tasks_count} 个")
    
    # 3. 统计用户发布的文章（将转移给管理员）
    articles_count = db.query(Article).filter(Article.author_id == user_id).count()
    if articles_count > 0:
        transfer_info.append(f"发布的文章: {articles_count} 篇")
    
    # 4. 统计用户创建的工作周（将转移给管理员）
    work_weeks_count = db.query(WorkWeek).filter(WorkWeek.created_by == user_id).count()
    if work_weeks_count > 0:
        transfer_info.append(f"创建的工作周: {work_weeks_count} 个")
    
    # 5. 统计用户拥有的协作文档（将转移给管理员）
    collab_docs_count = db.query(CollaborationDocument).filter(CollaborationDocument.owner_id == user_id).count()
    if collab_docs_count > 0:
        transfer_info.append(f"协作文档: {collab_docs_count} 个")
    
    # 6. 统计用户上传的任务附件（将转移给管理员）
    task_attachments_count = db.query(TaskAttachment).filter(TaskAttachment.uploaded_by == user_id).count()
    if task_attachments_count > 0:
        transfer_info.append(f"任务附件: {task_attachments_count} 个")
    
    # 7. 统计用户的文章编辑历史（将转移给管理员）
    article_edit_history_count = db.query(ArticleEditHistory).filter(ArticleEditHistory.editor_id == user_id).count()
    if article_edit_history_count > 0:
        transfer_info.append(f"文章编辑历史: {article_edit_history_count} 条")
    
    if transfer_info:
        logger.info(f"ℹ️ [UsersAPI] 将转移以下数据给管理员: {transfer_info}")
    
    # 统计可以自动处理的关联（供日志记录）
    # 只处理非完成状态的任务（approved 和 skipped 是已完成状态，应保留）
    incomplete_statuses = ['pending', 'assigned', 'in_progress', 'submitted', 'rejected', 'skip_pending']
    incomplete_tasks_count = db.query(Task).filter(
        Task.assigned_to == user_id,
        Task.status.in_(incomplete_statuses)
    ).count()
    
    # 统计已完成的任务（保留作为历史记录）
    completed_tasks_count = db.query(Task).filter(
        Task.assigned_to == user_id,
        Task.status.in_(['approved', 'skipped'])
    ).count()
    
    if incomplete_tasks_count > 0:
        auto_handle_info.append(f"进行中的任务: {incomplete_tasks_count} 个（将设为未分配）")
    
    if completed_tasks_count > 0:
        auto_handle_info.append(f"已完成的任务: {completed_tasks_count} 个（保留历史记录）")
    
    reviewed_tasks_count = db.query(Task).filter(Task.reviewed_by == user_id).count()
    if reviewed_tasks_count > 0:
        auto_handle_info.append(f"审核的任务: {reviewed_tasks_count} 个（保留历史记录）")
    
    work_logs_count = db.query(WorkLogEntry).filter(WorkLogEntry.user_id == user_id).count()
    if work_logs_count > 0:
        auto_handle_info.append(f"工作日志: {work_logs_count} 条（将被删除）")
    
    performance_count = db.query(PerformanceStats).filter(PerformanceStats.user_id == user_id).count()
    if performance_count > 0:
        auto_handle_info.append(f"绩效统计: {performance_count} 条（保留历史记录）")
    
    document_collaborator_count = db.query(DocumentCollaborator).filter(DocumentCollaborator.user_id == user_id).count()
    if document_collaborator_count > 0:
        auto_handle_info.append(f"文档协作关系: {document_collaborator_count} 条（将被删除）")
    
    if auto_handle_info:
        logger.info(f"ℹ️ [UsersAPI] 用户有可自动处理的关联数据: {user_id}, {auto_handle_info}")
    
    try:
        # === 第一步：转移创建的数据给管理员 ===
        
        # 1. 转移创建的项目
        if created_projects_count > 0:
            db.query(Project).filter(Project.created_by == user_id).update({
                "created_by": system_admin.id
            }, synchronize_session=False)
            logger.info(f"✅ [UsersAPI] 已将 {created_projects_count} 个项目转移给管理员 {system_admin.username}")
        
        # 2. 转移创建的任务
        if created_tasks_count > 0:
            db.query(Task).filter(Task.created_by == user_id).update({
                "created_by": system_admin.id,
                "created_by_name": system_admin.real_name
            }, synchronize_session=False)
            logger.info(f"✅ [UsersAPI] 已将 {created_tasks_count} 个任务转移给管理员 {system_admin.username}")
        
        # 3. 转移发布的文章
        if articles_count > 0:
            db.query(Article).filter(Article.author_id == user_id).update({
                "author_id": system_admin.id,
                "author_name": system_admin.real_name
            }, synchronize_session=False)
            logger.info(f"✅ [UsersAPI] 已将 {articles_count} 篇文章转移给管理员 {system_admin.username}")
        
        # 4. 转移创建的工作周
        if work_weeks_count > 0:
            db.query(WorkWeek).filter(WorkWeek.created_by == user_id).update({
                "created_by": system_admin.id
            }, synchronize_session=False)
            logger.info(f"✅ [UsersAPI] 已将 {work_weeks_count} 个工作周转移给管理员 {system_admin.username}")
        
        # 5. 转移协作文档
        if collab_docs_count > 0:
            db.query(CollaborationDocument).filter(CollaborationDocument.owner_id == user_id).update({
                "owner_id": system_admin.id,
                "owner_name": system_admin.real_name
            }, synchronize_session=False)
            logger.info(f"✅ [UsersAPI] 已将 {collab_docs_count} 个协作文档转移给管理员 {system_admin.username}")
        
        # 6. 转移任务附件
        if task_attachments_count > 0:
            db.query(TaskAttachment).filter(TaskAttachment.uploaded_by == user_id).update({
                "uploaded_by": system_admin.id
            }, synchronize_session=False)
            logger.info(f"✅ [UsersAPI] 已将 {task_attachments_count} 个任务附件转移给管理员 {system_admin.username}")
        
        # 7. 转移文章编辑历史
        if article_edit_history_count > 0:
            db.query(ArticleEditHistory).filter(ArticleEditHistory.editor_id == user_id).update({
                "editor_id": system_admin.id,
                "editor_name": system_admin.real_name
            }, synchronize_session=False)
            logger.info(f"✅ [UsersAPI] 已将 {article_edit_history_count} 条文章编辑历史转移给管理员 {system_admin.username}")
        
        # === 第二步：处理分配的任务 ===
        
        # 6. 只将非完成状态的任务设为未分配（已完成的任务保留历史记录）
        if incomplete_tasks_count > 0:
            updated_count = db.query(Task).filter(
                Task.assigned_to == user_id,
                Task.status.in_(incomplete_statuses)
            ).update({
                "assigned_to": None,
                "assigned_to_name": None,
                "status": "pending"  # 恢复为待分配状态
            }, synchronize_session=False)
            logger.info(f"✅ [UsersAPI] 已将 {updated_count} 个进行中的任务设为未分配")
        
        # 已完成的任务（approved, skipped）保留，不做任何修改
        if completed_tasks_count > 0:
            logger.info(f"ℹ️ [UsersAPI] 保留 {completed_tasks_count} 个已完成的任务作为历史记录")
        
        # 2. 审核过的任务不需要处理（reviewed_by 可以为 NULL，保留历史记录）
        # 如果需要清除审核记录，可以取消注释下面的代码：
        # if reviewed_tasks_count > 0:
        #     db.query(Task).filter(Task.reviewed_by == user_id).update({
        #         "reviewed_by": None,
        #         "reviewed_by_name": None
        #     })
        
        # 3. 删除用户的工作日志
        if work_logs_count > 0:
            db.query(WorkLogEntry).filter(WorkLogEntry.user_id == user_id).delete()
            logger.info(f"✅ [UsersAPI] 已删除 {work_logs_count} 条工作日志")
        
        # 4. 保留用户的绩效统计（作为历史记录）
        if performance_count > 0:
            logger.info(f"ℹ️ [UsersAPI] 保留 {performance_count} 条绩效统计记录作为历史数据")
        
        # 5. 删除用户的文档协作关系
        if document_collaborator_count > 0:
            db.query(DocumentCollaborator).filter(DocumentCollaborator.user_id == user_id).delete()
            logger.info(f"✅ [UsersAPI] 已删除 {document_collaborator_count} 条文档协作关系")
        
        # 6. 删除用户
        db.delete(user)
        db.commit()
        logger.info(f"✅ [UsersAPI] 用户删除成功: {user_id} ({user.username})")
        
        # ✅ 清除用户缓存
        user_cache_service.invalidate_all_users_cache()
        
        # 同时撤销该用户的所有 Token（如果 Redis 可用）
        try:
            from app.utils.token_manager import token_manager
            token_manager.revoke_user_tokens(user_id)
            logger.info(f"✅ [UsersAPI] 已撤销用户的所有 Token: {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ [UsersAPI] 撤销 Token 失败（Redis 可能未连接）: {str(e)}")
        
        return {
            "code": 200,
            "msg": "用户删除成功",
            "data": None
        }
    except Exception as e:
        db.rollback()
        logger.error(f"❌ [UsersAPI] 删除用户失败: {user_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")

@router.post("/{user_id}/toggle-status")
def toggle_user_status(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("UserManagement"))
):
    """切换用户状态（启用/禁用）"""
    # 不能修改自己的状态
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能修改自己的状态")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 切换状态
    user.status = "inactive" if user.status == "active" else "active"
    db.commit()
    
    # ✅ 清除用户缓存
    user_cache_service.invalidate_user_cache(user_id)
    
    status_text = "启用" if user.status == "active" else "禁用"
    return {
        "code": 200,
        "msg": f"用户已{status_text}",
        "data": None
    }

@router.get("/stats/summary")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("UserManagement"))
):
    """获取用户统计信息（仅管理员）"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.status == "active").count()
    admin_users = db.query(User).filter(User.role == "admin").count()
    annotator_users = db.query(User).filter(User.role == "annotator").count()
    
    return {
        "code": 200,
        "msg": "成功",
        "data": {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "admin_users": admin_users,
            "annotator_users": annotator_users
        }
    }


@router.get("/basic")
def get_users_basic(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取用户基本信息列表（所有登录用户可访问）
    用于文章编辑时选择可编辑用户、部门等
    返回简化的用户信息：id, username, real_name, department, role
    """
    query = db.query(User)
    
    # 默认只返回active用户
    if status:
        query = query.filter(User.status == status)
    else:
        query = query.filter(User.status == "active")
    
    users = query.all()
    
    return {
        "code": 200,
        "msg": "成功",
        "data": {
            "users": [
                {
                    "id": u.id,
                    "username": u.username,
                    "real_name": u.real_name,
                    "department": u.department,
                    "role": u.role
                }
                for u in users
            ],
            "total": len(users)
        }
    }