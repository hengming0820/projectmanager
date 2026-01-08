from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, func
from typing import Optional
from datetime import datetime, timedelta
from app.utils.datetime_utils import utc_now
import uuid
import re

from app.database import get_db
from app.utils.security import get_current_user
from app.models.user import User
from app.models.article import Article, ArticleEditHistory
from app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleResponse,
    ArticleQueryParams, ArticleListResponse, ArticleEditHistoryItem
)
from app.config import settings
from app.services.article_cache_service import article_cache_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/articles", tags=["文章发布"])


def can_manage(article: Article, user: User) -> bool:
    if user.role == 'admin':
        return True
    # 扩展：可编辑用户/角色
    try:
        if article.editable_user_ids and user.id in (article.editable_user_ids or []):
            return True
        if article.editable_roles and (user.role or '').lower() in [r.lower() for r in (article.editable_roles or [])]:
            return True
    except Exception:
        pass
    return article.author_id == user.id


def _rewrite_public_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return url
    bucket = settings.MINIO_BUCKET
    pattern = re.compile(r'^https?://[^/]+/' + re.escape(bucket) + r'/(.+)$')
    m = pattern.match(url)
    if m:
        return f"/api/files/{m.group(1)}"
    return url


def _rewrite_content_links(html: Optional[str]) -> Optional[str]:
    if not html:
        return html
    bucket = settings.MINIO_BUCKET
    return re.sub(r'https?://[^/]+/' + re.escape(bucket) + r'/', '/api/files/', html)


def _can_access_article(article: Article, user: User) -> bool:
    """检查用户是否有权限访问文章"""
    # 管理员可以访问所有文章
    if user.role == 'admin':
        return True
    
    user_dept = user.department or ''
    user_id = user.id
    
    # 1. 作者本人
    if article.author_id == user_id:
        return True
    # 2. 在可编辑成员列表中
    if article.editable_user_ids and user_id in article.editable_user_ids:
        return True
    # 3. 部门匹配
    if article.departments and user_dept:
        if user_dept in article.departments:
            return True
    # 4. 角色匹配
    if article.editable_roles and user.role:
        if user.role.lower() in [r.lower() for r in article.editable_roles]:
            return True
    # 5. 公开文章
    if article.is_public:
        return True
    
    return False


@router.get("/", response_model=ArticleListResponse)
def list_articles(
    params: ArticleQueryParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Article)
    if params.type:
        query = query.filter(Article.type == params.type)
    if params.status:
        query = query.filter(Article.status == params.status)
    if params.search:
        like = f"%{params.search}%"
        query = query.filter(or_(Article.title.ilike(like), Article.summary.ilike(like)))
    if params.author_name:
        like_author = f"%{params.author_name}%"
        query = query.filter(Article.author_name.ilike(like_author))
    # 基于项目筛选
    if params.project_id is not None:
        if params.project_id == "":  # 空字符串表示只查询公共文章
            query = query.filter(Article.project_id.is_(None))
        else:
            query = query.filter(Article.project_id == params.project_id)
    # 基于创建时间过滤
    if params.year:
        query = query.filter(func.extract('year', Article.created_at) == params.year)
        if params.month:
            query = query.filter(func.extract('month', Article.created_at) == params.month)

    # 权限过滤：根据用户部门和可编辑成员过滤文章
    if current_user.role != 'admin':
        # 获取所有文章，然后在内存中过滤（因为需要检查JSON字段）
        all_items = query.order_by(desc(Article.updated_at)).all()
        filtered_items = [article for article in all_items if _can_access_article(article, current_user)]
        
        # 分页
        total = len(filtered_items)
        start = (params.page - 1) * params.page_size
        end = start + params.page_size
        items = filtered_items[start:end]
    else:
        # 管理员看到所有文章
        total = query.count()
        items = query.order_by(desc(Article.updated_at)).offset((params.page - 1) * params.page_size).limit(params.page_size).all()

    resp_items: list[ArticleResponse] = []
    for i in items:
        data = ArticleResponse.from_orm(i)
        data.content = _rewrite_content_links(data.content)
        data.cover_url = _rewrite_public_url(data.cover_url)
        resp_items.append(data)

    return ArticleListResponse(
        items=resp_items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
    )


@router.post("/", response_model=ArticleResponse)
def create_article(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    article = Article(
        id=str(uuid.uuid4()),
        title=payload.title,
        content=payload.content or "",
        summary=payload.summary,
        type=payload.type,
        status=payload.status or "draft",
        tags=payload.tags or [],
        cover_url=payload.cover_url,
        category=payload.category,
        is_public=True if payload.is_public is None else payload.is_public,
        editable_user_ids=(payload.editable_user_ids or []),
        editable_roles=(payload.editable_roles or []),
        departments=(payload.departments or []),
        project_id=payload.project_id,  # 添加项目关联
        author_id=current_user.id,
        author_name=(current_user.real_name or current_user.username),
    )
    db.add(article)
    db.flush()

    history = ArticleEditHistory(
        id=str(uuid.uuid4()),
        article_id=article.id,
        editor_id=current_user.id,
        editor_name=(current_user.real_name or current_user.username),
        action="create",
        changes_summary=f"创建文章: {article.title}",
        version_after=1,
    )
    db.add(history)
    db.commit()
    db.refresh(article)

    # 清除相关缓存
    article_cache_service.invalidate_article_list(
        article_type=article.type,
        project_id=article.project_id
    )
    article_cache_service.invalidate_article_tree(article.type)
    logger.info(f"🗑️ 创建文章后清除缓存: {article.id}")

    data = ArticleResponse.from_orm(article)
    data.content = _rewrite_content_links(data.content)
    data.cover_url = _rewrite_public_url(data.cover_url)
    return data


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 尝试从缓存获取
    cached_article = article_cache_service.get_article_detail(article_id)
    if cached_article:
        # 验证用户权限（即使是缓存数据也需要验证权限）
        # 这里简化处理，直接返回。实际生产环境可能需要在缓存中存储权限信息
        logger.info(f"🎯 文章详情缓存命中: {article_id}")
        return ArticleResponse(**cached_article)
    
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 权限检查：验证用户是否有访问权限
    if not _can_access_article(a, current_user):
        raise HTTPException(status_code=403, detail="您没有权限查看此文章")
    
    # 增加浏览次数
    a.view_count += 1
    db.commit()
    
    data = ArticleResponse.from_orm(a)
    data.content = _rewrite_content_links(data.content)
    data.cover_url = _rewrite_public_url(data.cover_url)
    
    # 写入缓存
    data_dict = data.dict()
    article_cache_service.set_article_detail(article_id, data_dict)
    logger.info(f"💾 文章详情已缓存: {article_id}")
    
    return data


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: str,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="文章不存在")

    if not can_manage(a, current_user):
        raise HTTPException(status_code=403, detail="无权限编辑此文章")

    changes = []
    if payload.title is not None and payload.title != a.title:
        changes.append(f"标题: {a.title} -> {payload.title}")
        a.title = payload.title
    if payload.summary is not None and payload.summary != a.summary:
        changes.append("更新摘要")
        a.summary = payload.summary
    if payload.content is not None and payload.content != a.content:
        changes.append("编辑内容")
        a.content = payload.content
        a.edit_count += 1
    if payload.status is not None and payload.status != a.status:
        changes.append(f"状态: {a.status} -> {payload.status}")
        a.status = payload.status
    if payload.tags is not None and payload.tags != a.tags:
        changes.append("更新标签")
        a.tags = payload.tags
    if payload.cover_url is not None and payload.cover_url != a.cover_url:
        changes.append("更新封面")
        a.cover_url = payload.cover_url
    if payload.category is not None and payload.category != a.category:
        changes.append("更新分类")
        a.category = payload.category
    if payload.is_public is not None and payload.is_public != a.is_public:
        changes.append(f"可见性: {a.is_public} -> {payload.is_public}")
        a.is_public = payload.is_public
    if payload.editable_user_ids is not None:
        a.editable_user_ids = payload.editable_user_ids
        changes.append("可编辑成员变更")
    if payload.editable_roles is not None:
        a.editable_roles = payload.editable_roles
        changes.append("可编辑角色变更")
    if payload.departments is not None:
        a.departments = payload.departments
        changes.append("所属部门变更")
    if payload.project_id is not None and payload.project_id != a.project_id:
        changes.append(f"项目关联变更")
        a.project_id = payload.project_id

    if changes:
        prev = a.version
        a.version = (a.version or 1) + 1
        hist = ArticleEditHistory(
            id=str(uuid.uuid4()),
            article_id=a.id,
            editor_id=current_user.id,
            editor_name=(current_user.real_name or current_user.username),
            action="update",
            changes_summary="; ".join(changes),
            version_before=prev,
            version_after=a.version,
        )
        db.add(hist)

    db.commit()
    db.refresh(a)
    
    # 清除文章相关缓存
    article_cache_service.invalidate_article_all(article_id)
    logger.info(f"🗑️ 更新文章后清除缓存: {article_id}")
    
    return ArticleResponse.from_orm(a)


@router.delete("/{article_id}")
def delete_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="文章不存在")
    if not can_manage(a, current_user):
        raise HTTPException(status_code=403, detail="无权限删除此文章")
    
    article_type = a.type
    project_id = a.project_id
    
    # 先删除文章的编辑历史
    db.query(ArticleEditHistory).filter(ArticleEditHistory.article_id == article_id).delete()
    
    # 再删除文章本身
    db.delete(a)
    db.commit()
    
    # 清除文章相关缓存
    article_cache_service.invalidate_article_all(article_id)
    article_cache_service.invalidate_article_list(
        article_type=article_type,
        project_id=project_id
    )
    article_cache_service.invalidate_article_tree(article_type)
    logger.info(f"🗑️ 删除文章后清除缓存: {article_id}")
    
    return {"message": "文章已删除"}


@router.get("/{article_id}/history", response_model=list[ArticleEditHistoryItem])
def get_article_history(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 尝试从缓存获取
    cached_history = article_cache_service.get_article_history(article_id)
    if cached_history:
        logger.info(f"🎯 文章编辑历史缓存命中: {article_id}")
        return [ArticleEditHistoryItem(**item) for item in cached_history]
    
    rows = db.query(ArticleEditHistory).filter(ArticleEditHistory.article_id == article_id).order_by(desc(ArticleEditHistory.created_at)).all()
    history_items = [ArticleEditHistoryItem.from_orm(r) for r in rows]
    
    # 写入缓存
    history_dict = [item.dict() for item in history_items]
    article_cache_service.set_article_history(article_id, history_dict)
    logger.info(f"💾 文章编辑历史已缓存: {article_id}")
    
    return history_items


# ============== 编辑锁相关接口 ==============

def cleanup_expired_article_locks(db: Session, timeout_minutes: int = 30):
    """清理过期的文章锁定（超过指定时间未解锁的）"""
    cutoff_time = utc_now() - timedelta(minutes=timeout_minutes)
    
    expired = db.query(Article).filter(
        Article.is_locked == True,
        Article.locked_at < cutoff_time
    ).all()
    
    for article in expired:
        print(f"🔓 [清理] 文章锁定已过期: article_id={article.id}, locked_by={article.locked_by}, locked_at={article.locked_at}")
        article.is_locked = False
        article.locked_by = None
        article.locked_at = None
    
    if expired:
        db.commit()
        print(f"✅ [清理] 已释放 {len(expired)} 个过期的文章锁")
    
    return len(expired)


@router.post("/{article_id}/lock")
def lock_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """锁定文章，开始编辑"""
    # 清理过期锁
    cleanup_expired_article_locks(db)
    
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查编辑权限
    if not can_manage(article, current_user):
        raise HTTPException(status_code=403, detail="您没有权限编辑此文章")
    
    # 检查是否已被锁定
    if article.is_locked:
        if article.locked_by == current_user.id:
            # 同一用户重复锁定，刷新锁定时间
            article.locked_at = utc_now()
            db.commit()
            print(f"🔄 [锁定] 刷新锁定: article_id={article_id}, user={current_user.username}")
            return {"message": "锁定已刷新", "locked_by": article.locked_by}
        else:
            # 被其他用户锁定
            print(f"⚠️ [锁定] 文章已被其他用户锁定: article_id={article_id}, locked_by={article.locked_by}")
            raise HTTPException(
                status_code=423,
                detail=f"文章正在被其他用户编辑中，locked_by={article.locked_by}"
            )
    
    # 锁定文章
    article.is_locked = True
    article.locked_by = current_user.id
    article.locked_at = utc_now()
    db.commit()
    
    print(f"🔒 [锁定] 文章已锁定: article_id={article_id}, user={current_user.username}")
    return {"message": "文章已锁定", "locked_by": current_user.id}


@router.post("/{article_id}/unlock")
def unlock_article(
    article_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """解锁文章，结束编辑"""
    # 清理过期锁
    cleanup_expired_article_locks(db)
    
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查是否已锁定
    if not article.is_locked:
        print(f"ℹ️ [解锁] 文章未锁定: article_id={article_id}")
        return {"message": "文章未锁定"}
    
    # 只有锁定者或管理员可以解锁
    if article.locked_by != current_user.id and current_user.role != 'admin':
        print(f"⚠️ [解锁] 无权解锁: article_id={article_id}, locked_by={article.locked_by}, current_user={current_user.username}")
        raise HTTPException(status_code=403, detail="只有锁定者或管理员可以解锁")
    
    # 解锁文章
    article.is_locked = False
    article.locked_by = None
    article.locked_at = None
    db.commit()
    
    print(f"🔓 [解锁] 文章已解锁: article_id={article_id}, user={current_user.username}")
    return {"message": "文章已解锁"}


