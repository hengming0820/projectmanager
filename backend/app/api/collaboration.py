"""
团队协作文档 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional
import time
from datetime import datetime, timedelta
from app.utils.datetime_utils import utc_now
import uuid

from app.database import get_db
from app.utils.security import get_current_user
from app.utils.permissions import require_permission
from app.models.user import User
from app.models.article import Article
from app.models.collaboration import (
    CollaborationDocument, DocumentCollaborator, DocumentEditHistory,
    DocumentComment, CollaborationSession
)
from app.schemas.collaboration import (
    CollaborationDocumentResponse, CollaborationDocumentCreate, CollaborationDocumentUpdate,
    CollaborationDocumentQueryParams, CollaborationDocumentListResponse,
    CollaboratorResponse, CollaboratorCreate, CollaboratorUpdate,
    DocumentEditHistoryResponse, DocumentCommentResponse, DocumentCommentCreate,
    CollaborationStateResponse, CollaborationStatisticsResponse
)
from app.utils.redis_client import get_redis

router = APIRouter(prefix="/collaboration", tags=["协作文档"])

# 在线状态 TTL（秒）
PRESENCE_TTL_SECONDS = 20
# ==================== 简易内存房间（OT-lite） ====================
from collections import defaultdict
from typing import Dict, Any

class RoomState:
    def __init__(self):
        self.content: str = ""
        self.version: int = 1
        self.ops: list[dict] = []  # 仅保存最近若干条
        self.clients: set[WebSocket] = set()

ROOMS: Dict[str, RoomState] = defaultdict(RoomState)

def transform_position(pos: int, since_ops: list[dict]) -> int:
    new_pos = pos
    for op in since_ops:
        op_pos = op.get('pos', 0)
        ins = op.get('ins', "")
        dele = int(op.get('del', 0) or 0)
        if op_pos < new_pos:
            new_pos += len(ins) - dele
    return max(0, new_pos)

def apply_op_to_text(text: str, pos: int, dele: int, ins: str) -> str:
    pos = max(0, min(len(text), pos))
    dele = max(0, min(len(text) - pos, dele))
    return text[:pos] + (ins or "") + text[pos+dele:]

async def ws_broadcast(room: RoomState, message: Any, exclude: WebSocket | None = None):
    dead = []
    for ws in list(room.clients):
        if exclude is not None and ws is exclude:
            continue
        try:
            await ws.send_json(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        room.clients.discard(ws)

@router.websocket("/ws/{document_id}")
async def collaboration_ws(websocket: WebSocket, document_id: str):
    await websocket.accept()
    room = ROOMS[document_id]
    room.clients.add(websocket)
    try:
        # 首次发送初始化内容
        await websocket.send_json({
            "type": "init",
            "version": room.version,
            "content": room.content,
        })
        while True:
            data = await websocket.receive_json()
            mtype = data.get('type')
            if mtype == 'presence':
                await ws_broadcast(room, {
                    "type": "presence",
                    "user_id": data.get('user_id'),
                    "user_name": data.get('user_name'),
                    "cursor": data.get('cursor'),
                    "selection": data.get('selection')
                }, exclude=websocket)
            elif mtype == 'op':
                client_ver = int(data.get('version') or 1)
                pos = int(data.get('pos') or 0)
                dele = int(data.get('del') or 0)
                ins = data.get('ins') or ""
                # 将 pos 转换到当前最新版本
                if client_ver < room.version:
                    since_ops = room.ops[client_ver - 1:]
                    pos = transform_position(pos, since_ops)
                # 应用到服务端文本
                room.content = apply_op_to_text(room.content, pos, dele, ins)
                room.version += 1
                op_msg = {
                    "type": "op",
                    "version": room.version,
                    "pos": pos,
                    "del": dele,
                    "ins": ins,
                    "user_id": data.get('user_id'),
                    "user_name": data.get('user_name')
                }
                room.ops.append({"pos": pos, "del": dele, "ins": ins})
                if len(room.ops) > 500:
                    room.ops = room.ops[-500:]
                # 广播给所有客户端（包含发送者），以便发送端拿到最终版本号
                await ws_broadcast(room, op_msg, exclude=None)
            else:
                # 回退：广播原样数据
                await ws_broadcast(room, data, exclude=websocket)
    except WebSocketDisconnect:
        room.clients.discard(websocket)
    except Exception:
        room.clients.discard(websocket)


# ==================== 权限检查辅助函数 ====================

def check_document_permission(document: CollaborationDocument, current_user: User, action: str = "view") -> bool:
    """
    检查用户对文档的权限
    
    Args:
        document: 文档对象
        current_user: 当前用户
        action: 操作类型 ("view", "edit", "manage")
    
    Returns:
        bool: 是否有权限
    """
    print(f"🔐 [Permission] 检查权限:")
    print(f"   用户: {current_user.username} (ID: {current_user.id})")
    print(f"   用户角色: {current_user.role}")
    print(f"   操作: {action}")
    print(f"   文档所有者: {document.owner_id}")
    
    # 管理员拥有所有权限
    if current_user.role == 'admin':
        print(f"   ✅ 管理员权限，允许{action}")
        return True
    
    # 文档所有者拥有所有权限
    if document.owner_id == current_user.id:
        print(f"   ✅ 文档所有者，允许{action}")
        return True
    
    # 检查协作者权限
    collaborator = next((c for c in document.collaborators if c.user_id == current_user.id), None)
    if collaborator:
        if action == "view":
            print(f"   ✅ 协作者，允许查看")
            return True
        elif action == "edit" and collaborator.role == "editor":
            print(f"   ✅ 编辑者，允许编辑")
            return True
        elif action == "manage":
            print(f"   ❌ 协作者无管理权限")
            return False
        else:
            print(f"   ❌ 协作者权限不足: {collaborator.role}")
            return False
    
    print(f"   ❌ 无权限执行{action}")
    return False


# ==================== 协作文档管理 ====================

@router.get("/documents/recent")
async def get_recent_documents(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取最近访问的文档"""
    try:
        print(f"📋 [CollaborationAPI] 获取最近访问的文档，用户: {current_user.username}")
        
        # 这里可以根据用户的访问记录来获取，暂时返回最近更新的文档
        documents = db.query(CollaborationDocument).options(
            joinedload(CollaborationDocument.collaborators)
        ).filter(
            or_(
                CollaborationDocument.owner_id == current_user.id,
                CollaborationDocument.collaborators.any(
                    DocumentCollaborator.user_id == current_user.id
                )
            )
        ).order_by(desc(CollaborationDocument.updated_at)).limit(limit).all()
        
        print(f"✅ [CollaborationAPI] 找到 {len(documents)} 个最近文档")
        
        return [CollaborationDocumentResponse.from_orm(doc) for doc in documents]
        
    except Exception as e:
        print(f"❌ [CollaborationAPI] 获取最近文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取最近文档失败: {str(e)}"
        )


@router.get("/documents/my", response_model=CollaborationDocumentListResponse)
async def get_my_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我参与的文档"""
    try:
        print(f"📋 [CollaborationAPI] 获取我参与的文档，用户: {current_user.username}")
        
        # 查询我拥有的文档和我参与的文档
        query = db.query(CollaborationDocument).options(
            joinedload(CollaborationDocument.collaborators)
        ).filter(
            or_(
                CollaborationDocument.owner_id == current_user.id,
                CollaborationDocument.collaborators.any(
                    DocumentCollaborator.user_id == current_user.id
                )
            )
        ).order_by(desc(CollaborationDocument.updated_at))
        
        total = query.count()
        documents = query.offset((page - 1) * page_size).limit(page_size).all()
        
        print(f"✅ [CollaborationAPI] 找到 {len(documents)} 个我参与的文档")
        
        return CollaborationDocumentListResponse(
            items=[CollaborationDocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
        
    except Exception as e:
        print(f"❌ [CollaborationAPI] 获取我参与的文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档失败: {str(e)}"
        )


@router.get("/documents", response_model=CollaborationDocumentListResponse)
async def get_documents(
    params: CollaborationDocumentQueryParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取协作文档列表"""
    try:
        print(f"📋 [CollaborationAPI] 获取协作文档列表，用户: {current_user.username}")
        
        query = db.query(CollaborationDocument).options(
            joinedload(CollaborationDocument.collaborators),
            joinedload(CollaborationDocument.owner)
        )
        
        # 过滤条件
        if params.status:
            query = query.filter(CollaborationDocument.status == params.status)
        if params.priority:
            query = query.filter(CollaborationDocument.priority == params.priority)
        if params.project_id:
            query = query.filter(CollaborationDocument.project_id == params.project_id)
        if params.category:
            query = query.filter(CollaborationDocument.category == params.category)
        if params.tag:
            query = query.filter(CollaborationDocument.tags.contains([params.tag]))
        if params.owner_id:
            query = query.filter(CollaborationDocument.owner_id == params.owner_id)
        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    CollaborationDocument.title.ilike(search_term),
                    CollaborationDocument.description.ilike(search_term),
                    CollaborationDocument.content.ilike(search_term)
                )
            )
        if params.created_start:
            query = query.filter(CollaborationDocument.created_at >= params.created_start)
        if params.created_end:
            query = query.filter(CollaborationDocument.created_at <= params.created_end)
        
        # 协作者过滤
        if params.collaborator_id:
            query = query.join(DocumentCollaborator).filter(
                DocumentCollaborator.user_id == params.collaborator_id
            )
        
        # 排序
        sort_field = getattr(CollaborationDocument, params.sort_by, CollaborationDocument.updated_at)
        if params.sort_order == 'asc':
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # 分页
        total = query.count()
        documents = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()

        # 覆盖展示名称为真实姓名（不落库）
        for d in documents:
            try:
                if getattr(d, 'owner', None):
                    display = getattr(d.owner, 'real_name', None) or getattr(d.owner, 'username', None)
                    if display:
                        d.owner_name = display
            except Exception:
                pass
        
        print(f"✅ [CollaborationAPI] 找到 {len(documents)} 个文档，总计 {total} 个")
        
        return CollaborationDocumentListResponse(
            items=[CollaborationDocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size
        )
        
    except Exception as e:
        print(f"❌ [CollaborationAPI] 获取协作文档列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档列表失败: {str(e)}"
        )


@router.get("/documents/{document_id}", response_model=CollaborationDocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取协作文档详情"""
    try:
        print(f"📄 [CollaborationAPI] 获取协作文档详情: {document_id}")
        
        document = db.query(CollaborationDocument).options(
            joinedload(CollaborationDocument.collaborators),
            joinedload(CollaborationDocument.owner)
        ).filter(CollaborationDocument.id == document_id).first()
        
        if not document:
            # Fallback: 查找 articles 表中是否有对应的 collaboration 类型文章
            print(f"📋 [CollaborationAPI] 协作文档不存在，尝试从 articles 表创建: {document_id}")
            article = db.query(Article).filter(Article.id == document_id).first()
            
            if article and article.type == 'collaboration':
                print(f"✅ [CollaborationAPI] 找到对应的 article，创建协作文档: {article.title}")
                # 从 article 创建协作文档
                document = CollaborationDocument(
                    id=article.id,  # 使用相同的 ID
                    title=article.title,
                    description=article.summary or "",
                    content=article.content or "",
                    status="active",
                    priority="normal",
                    owner_id=article.author_id,
                    owner_name=article.author_name,
                    project_id=article.project_id,
                    project_name=None,  # 需要的话可以从 project 表查询
                    category=article.category,
                    tags=article.tags or [],
                    last_edited_by=article.author_name,
                    last_edited_at=article.updated_at,
                    view_count=article.view_count or 0,
                    edit_count=article.edit_count or 0,
                    version=article.version or 1,
                    is_locked=False,
                    locked_by=None,
                    locked_at=None
                )
                db.add(document)
                
                # 添加创建者作为协作者
                collaborator = DocumentCollaborator(
                    document_id=document.id,
                    user_id=current_user.id,
                    user_name=current_user.real_name or current_user.username,
                    role="owner"
                )
                db.add(collaborator)
                
                db.commit()
                db.refresh(document)
                
                # 重新加载文档（包含关联数据）
                document = db.query(CollaborationDocument).options(
                    joinedload(CollaborationDocument.collaborators),
                    joinedload(CollaborationDocument.owner)
                ).filter(CollaborationDocument.id == document_id).first()
                
                print(f"✅ [CollaborationAPI] 协作文档创建成功: {document.title}")
            else:
                raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查查看权限
        if not check_document_permission(document, current_user, "view"):
            raise HTTPException(status_code=403, detail="无权限查看此文档")
        
        # 覆盖展示名称为真实姓名（不落库）
        try:
            if getattr(document, 'owner', None):
                display = getattr(document.owner, 'real_name', None) or getattr(document.owner, 'username', None)
                if display:
                    document.owner_name = display
        except Exception:
            pass

        # 增加查看次数
        document.view_count += 1
        db.commit()
        
        print(f"✅ [CollaborationAPI] 找到文档: {document.title}")
        
        return CollaborationDocumentResponse.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [CollaborationAPI] 获取协作文档详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档详情失败: {str(e)}"
        )


@router.get("/documents/{document_id}/state", response_model=CollaborationStateResponse)
async def get_document_state(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文档协作状态"""
    try:
        print(f"📊 [CollaborationAPI] 获取文档协作状态: {document_id}")
        
        # 行级锁，防止并发获取锁
        document = db.query(CollaborationDocument).with_for_update(nowait=True).filter(
            CollaborationDocument.id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查查看权限
        if not check_document_permission(document, current_user, "view"):
            raise HTTPException(status_code=403, detail="无权限查看此文档")
        
        # 活跃编辑者（心跳30秒内）
        threshold = utc_now() - timedelta(seconds=30)
        sessions = db.query(CollaborationSession).filter(
            CollaborationSession.document_id == document_id,
            CollaborationSession.is_active == True,
            CollaborationSession.last_heartbeat >= threshold,
        ).all()
        active = []
        for s in sessions:
            active.append({
                "user_id": s.user_id,
                "user_name": s.user_name,
                "cursor_position": s.cursor_position,
                "selection_range": {
                    "start": s.selection_start or 0,
                    "end": s.selection_end or 0
                } if (s.selection_start is not None and s.selection_end is not None) else None,
                "last_active": (s.last_heartbeat or utc_now()).isoformat(),
            })

        # 构建协作状态响应（返回真实锁状态）
        state = CollaborationStateResponse(
            document_id=document.id,
            is_locked=getattr(document, 'is_locked', False) or False,
            locked_by=getattr(document, 'locked_by', None),
            active_editors=active
        )
        
        print(f"✅ [CollaborationAPI] 协作状态获取成功")
        
        return state
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [CollaborationAPI] 获取协作状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取协作状态失败: {str(e)}"
        )


@router.get("/documents/{document_id}/history")
async def get_document_history(
    document_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文档编辑历史"""
    try:
        print(f"📜 [CollaborationAPI] 获取文档编辑历史: {document_id}")

        document = db.query(CollaborationDocument).filter(
            CollaborationDocument.id == document_id
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 权限：可查看者均可查看历史
        if not check_document_permission(document, current_user, "view"):
            raise HTTPException(status_code=403, detail="无权限查看此文档历史")

        query = db.query(DocumentEditHistory).filter(
            DocumentEditHistory.document_id == document_id
        ).order_by(desc(DocumentEditHistory.created_at))

        total = query.count()
        records = query.offset((page - 1) * page_size).limit(page_size).all()

        # 确保返回 editor_name 为真实姓名（若有）
        user_ids = {r.editor_id for r in records if r.editor_id}
        id_to_realname = {}
        if user_ids:
            users = db.query(User).filter(User.id.in_(list(user_ids))).all()
            id_to_realname = {u.id: (u.real_name or u.username) for u in users}

        items = []
        for r in records:
            editor_display = id_to_realname.get(r.editor_id, r.editor_name)
            items.append({
                "id": r.id,
                "document_id": r.document_id,
                "editor_id": r.editor_id,
                "editor_name": editor_display,
                "action": r.action,
                "changes_summary": r.changes_summary,
                "version_before": getattr(r, 'version_before', None),
                "version_after": getattr(r, 'version_after', None),
                "created_at": r.created_at.isoformat() if r.created_at else utc_now().isoformat()
            })

        return {"items": items, "total": total}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [CollaborationAPI] 获取编辑历史失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取编辑历史失败: {str(e)}"
        )


@router.post("/documents", response_model=CollaborationDocumentResponse)
async def create_document(
    document_data: CollaborationDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建协作文档"""
    try:
        print(f"➕ [CollaborationAPI] 创建协作文档: {document_data.title}")
        
        # 创建文档
        document = CollaborationDocument(
            id=str(uuid.uuid4()),
            title=document_data.title,
            description=document_data.description,
            content=document_data.content or "",
            priority=document_data.priority or "normal",
            owner_id=current_user.id,
            owner_name=(current_user.real_name or current_user.username),
            project_id=document_data.project_id,
            category=document_data.category,
            tags=document_data.tags or [],
            last_edited_by=(current_user.real_name or current_user.username),
            last_edited_at=utc_now()
        )
        
        db.add(document)
        db.flush()  # 获取文档ID
        
        # 添加初始协作者
        if document_data.collaborator_ids:
            for user_id in document_data.collaborator_ids:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    collaborator = DocumentCollaborator(
                        id=str(uuid.uuid4()),
                        document_id=document.id,
                        user_id=user.id,
                        user_name=(user.real_name or user.username),
                        role="editor"
                    )
                    db.add(collaborator)
        
        # 记录创建历史
        history = DocumentEditHistory(
            id=str(uuid.uuid4()),
            document_id=document.id,
            editor_id=current_user.id,
            editor_name=(current_user.real_name or current_user.username),
            action="create",
            changes_summary=f"创建文档: {document.title}",
            version_after=1
        )
        db.add(history)
        
        db.commit()
        db.refresh(document)
        
        print(f"✅ [CollaborationAPI] 协作文档创建成功: {document.id}")
        
        return CollaborationDocumentResponse.from_orm(document)
        
    except Exception as e:
        print(f"❌ [CollaborationAPI] 创建协作文档失败: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建文档失败: {str(e)}"
        )


@router.put("/documents/{document_id}", response_model=CollaborationDocumentResponse)
async def update_document(
    document_id: str,
    document_data: CollaborationDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新协作文档"""
    try:
        print(f"✏️ [CollaborationAPI] 更新协作文档: {document_id}")
        
        document = db.query(CollaborationDocument).filter(
            CollaborationDocument.id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查编辑权限
        if not check_document_permission(document, current_user, "edit"):
            raise HTTPException(status_code=403, detail="无权限编辑此文档")
        
        # 更新字段
        changes = []
        if document_data.title is not None and document_data.title != document.title:
            changes.append(f"标题: {document.title} -> {document_data.title}")
            document.title = document_data.title
        
        if document_data.description is not None and document_data.description != document.description:
            changes.append("描述已更新")
            document.description = document_data.description
        
        if document_data.content is not None and document_data.content != document.content:
            changes.append("内容已更新")
            document.content = document_data.content
            document.edit_count += 1
        
        if document_data.status is not None and document_data.status != document.status:
            changes.append(f"状态: {document.status} -> {document_data.status}")
            document.status = document_data.status
        
        if document_data.priority is not None and document_data.priority != document.priority:
            changes.append(f"优先级: {document.priority} -> {document_data.priority}")
            document.priority = document_data.priority
        
        if document_data.category is not None and document_data.category != document.category:
            changes.append(f"分类: {document.category} -> {document_data.category}")
            document.category = document_data.category
        
        if document_data.tags is not None and document_data.tags != document.tags:
            changes.append("标签已更新")
            document.tags = document_data.tags
        
        if changes:
            document.last_edited_by = (current_user.real_name or current_user.username)
            document.last_edited_at = datetime.now()
            document.version += 1
            
            # 记录编辑历史
            history = DocumentEditHistory(
                id=str(uuid.uuid4()),
                document_id=document.id,
                editor_id=current_user.id,
                editor_name=(current_user.real_name or current_user.username),
                action="update",
                changes_summary="; ".join(changes),
                version_before=document.version - 1,
                version_after=document.version
            )
            db.add(history)
        
        db.commit()
        db.refresh(document)
        
        print(f"✅ [CollaborationAPI] 协作文档更新成功: {document.title}")
        
        return CollaborationDocumentResponse.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [CollaborationAPI] 更新协作文档失败: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新文档失败: {str(e)}"
        )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除协作文档"""
    try:
        print(f"🗑️ [CollaborationAPI] 删除协作文档: {document_id}")
        
        document = db.query(CollaborationDocument).filter(
            CollaborationDocument.id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查管理权限（所有者和管理员可以删除）
        if not check_document_permission(document, current_user, "manage"):
            raise HTTPException(status_code=403, detail="无权限删除此文档")
        
        # 删除文档（级联删除相关数据）
        db.delete(document)
        db.commit()
        
        print(f"✅ [CollaborationAPI] 协作文档删除成功: {document.title}")
        
        return {"message": "文档已删除"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [CollaborationAPI] 删除协作文档失败: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文档失败: {str(e)}"
        )


# ==================== 协作者管理 ====================

@router.post("/documents/{document_id}/collaborators", response_model=CollaboratorResponse)
async def add_collaborator(
    document_id: str,
    collaborator_data: CollaboratorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加协作者"""
    try:
        print(f"👥 [CollaborationAPI] 添加协作者: {document_id}, {collaborator_data.user_id}")
        
        document = db.query(CollaborationDocument).filter(
            CollaborationDocument.id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查管理权限（所有者和管理员可以添加协作者）
        if not check_document_permission(document, current_user, "manage"):
            raise HTTPException(status_code=403, detail="无权限添加协作者")
        
        # 检查用户是否存在
        user = db.query(User).filter(User.id == collaborator_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 检查是否已经是协作者
        existing = db.query(DocumentCollaborator).filter(
            and_(
                DocumentCollaborator.document_id == document_id,
                DocumentCollaborator.user_id == collaborator_data.user_id
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="用户已经是协作者")
        
        # 创建协作者
        collaborator = DocumentCollaborator(
            id=str(uuid.uuid4()),
            document_id=document_id,
            user_id=user.id,
            user_name=user.username,
            role=collaborator_data.role
        )
        
        db.add(collaborator)
        
        # 记录历史
        history = DocumentEditHistory(
            id=str(uuid.uuid4()),
            document_id=document_id,
            editor_id=current_user.id,
            editor_name=current_user.username,
            action="update",
            changes_summary=f"添加协作者: {user.username} ({collaborator_data.role})"
        )
        db.add(history)
        
        db.commit()
        db.refresh(collaborator)
        
        print(f"✅ [CollaborationAPI] 协作者添加成功: {user.username}")
        
        return CollaboratorResponse.from_orm(collaborator)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [CollaborationAPI] 添加协作者失败: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加协作者失败: {str(e)}"
        )


@router.put("/documents/{document_id}/collaborators/{user_id}", response_model=CollaboratorResponse)
async def update_collaborator_role(
    document_id: str,
    user_id: str,
    collaborator_data: CollaboratorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新协作者角色"""
    try:
        print(f"🔄 [CollaborationAPI] 更新协作者角色: {document_id}, {user_id}")
        
        document = db.query(CollaborationDocument).filter(
            CollaborationDocument.id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查管理权限
        if not check_document_permission(document, current_user, "manage"):
            raise HTTPException(status_code=403, detail="无权限修改协作者角色")
        
        collaborator = db.query(DocumentCollaborator).filter(
            and_(
                DocumentCollaborator.document_id == document_id,
                DocumentCollaborator.user_id == user_id
            )
        ).first()
        
        if not collaborator:
            raise HTTPException(status_code=404, detail="协作者不存在")
        
        old_role = collaborator.role
        collaborator.role = collaborator_data.role
        
        # 记录历史
        history = DocumentEditHistory(
            id=str(uuid.uuid4()),
            document_id=document_id,
            editor_id=current_user.id,
            editor_name=current_user.username,
            action="update",
            changes_summary=f"更新协作者角色: {collaborator.user_name} ({old_role} -> {collaborator_data.role})"
        )
        db.add(history)
        
        db.commit()
        db.refresh(collaborator)
        
        print(f"✅ [CollaborationAPI] 协作者角色更新成功: {collaborator.user_name}")
        
        return CollaboratorResponse.from_orm(collaborator)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [CollaborationAPI] 更新协作者角色失败: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新协作者角色失败: {str(e)}"
        )


@router.delete("/documents/{document_id}/collaborators/{user_id}")
async def remove_collaborator(
    document_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """移除协作者"""
    try:
        print(f"❌ [CollaborationAPI] 移除协作者: {document_id}, {user_id}")
        
        document = db.query(CollaborationDocument).filter(
            CollaborationDocument.id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查管理权限
        if not check_document_permission(document, current_user, "manage"):
            raise HTTPException(status_code=403, detail="无权限移除协作者")
        
        collaborator = db.query(DocumentCollaborator).filter(
            and_(
                DocumentCollaborator.document_id == document_id,
                DocumentCollaborator.user_id == user_id
            )
        ).first()
        
        if not collaborator:
            raise HTTPException(status_code=404, detail="协作者不存在")
        
        user_name = collaborator.user_name
        db.delete(collaborator)
        
        # 记录历史
        history = DocumentEditHistory(
            id=str(uuid.uuid4()),
            document_id=document_id,
            editor_id=current_user.id,
            editor_name=current_user.username,
            action="update",
            changes_summary=f"移除协作者: {user_name}"
        )
        db.add(history)
        
        db.commit()
        
        print(f"✅ [CollaborationAPI] 协作者移除成功: {user_name}")
        
        return {"message": "协作者已移除"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [CollaborationAPI] 移除协作者失败: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"移除协作者失败: {str(e)}"
        )


# ==================== 实时协作 ====================

@router.post("/documents/{document_id}/lock")
async def lock_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """开始编辑（独占锁）：若他人已锁定则拒绝。"""
    try:
        print(f"🔒 [CollaborationAPI] 申请独占锁: {document_id}")
        
        # 先清理超时的锁
        cleanup_expired_locks(db)
        
        document = db.query(CollaborationDocument).filter(
            CollaborationDocument.id == document_id
        ).first()
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        if not check_document_permission(document, current_user, "edit"):
            raise HTTPException(status_code=403, detail="无权限编辑此文档")

        # 已被他人锁定，直接拒绝
        if getattr(document, 'is_locked', False) and getattr(document, 'locked_by', None) not in (None, current_user.id):
            raise HTTPException(status_code=423, detail="文档已被他人编辑中")

        # 设置独占锁
        document.is_locked = True
        document.locked_by = current_user.id
        document.locked_at = datetime.now()

        # 可选：记录/激活会话（不影响锁机制）
        session = db.query(CollaborationSession).filter(
            CollaborationSession.document_id == document_id,
            CollaborationSession.user_id == current_user.id
        ).first()
        if not session:
            session = CollaborationSession(
                id=str(uuid.uuid4()),
                document_id=document_id,
                user_id=current_user.id,
                user_name=(current_user.real_name or current_user.username),
                session_id=str(uuid.uuid4()),
                is_active=True,
                last_heartbeat=datetime.now(),
            )
            db.add(session)
        else:
            session.is_active = True
            session.last_heartbeat = datetime.now()

        db.commit()
        return {"message": "已锁定", "locked_by": current_user.id, "locked_at": (document.locked_at or datetime.now()).isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"开始编辑失败: {str(e)}")


def cleanup_expired_locks(db: Session, timeout_minutes: int = 30):
    """
    清理超时的文档锁
    
    Args:
        db: 数据库会话
        timeout_minutes: 超时时间（分钟），默认30分钟
    """
    try:
        from datetime import timedelta
        timeout_time = datetime.now() - timedelta(minutes=timeout_minutes)
        
        # 查找所有超时的锁定文档
        expired_locks = db.query(CollaborationDocument).filter(
            CollaborationDocument.is_locked == True,
            CollaborationDocument.locked_at < timeout_time
        ).all()
        
        if expired_locks:
            print(f"🧹 [CollaborationAPI] 发现 {len(expired_locks)} 个超时的锁，正在清理...")
            for doc in expired_locks:
                print(f"   - 解锁文档: {doc.title} (ID: {doc.id}), 锁定时间: {doc.locked_at}")
                doc.is_locked = False
                doc.locked_by = None
                doc.locked_at = None
                
                # 同时清理相关的活跃会话
                sessions = db.query(CollaborationSession).filter(
                    CollaborationSession.document_id == doc.id,
                    CollaborationSession.is_active == True
                ).all()
                for session in sessions:
                    session.is_active = False
            
            db.commit()
            print(f"✅ [CollaborationAPI] 已清理 {len(expired_locks)} 个超时的锁")
            return len(expired_locks)
        else:
            print("✅ [CollaborationAPI] 没有发现超时的锁")
            return 0
    except Exception as e:
        print(f"❌ [CollaborationAPI] 清理超时锁失败: {e}")
        db.rollback()
        return 0


@router.post("/documents/{document_id}/unlock")
async def unlock_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """结束编辑：释放独占锁，并将当前用户的会话置为非活跃。"""
    try:
        print(f"🔓 [CollaborationAPI] 结束编辑: {document_id}")
        
        # 先清理一次超时的锁
        cleanup_expired_locks(db)
        
        document = db.query(CollaborationDocument).filter(
            CollaborationDocument.id == document_id
        ).first()
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 仅锁持有者、所有者或管理员可解锁
        can_force = current_user.role == 'admin' or document.owner_id == current_user.id
        if getattr(document, 'is_locked', False) and document.locked_by not in (None, current_user.id):
            if not can_force:
                raise HTTPException(status_code=423, detail="仅锁持有者可解锁")

        document.is_locked = False
        document.locked_by = None
        document.locked_at = None

        session = db.query(CollaborationSession).filter(
            CollaborationSession.document_id == document_id,
            CollaborationSession.user_id == current_user.id
        ).first()
        if session:
            session.is_active = False
            session.last_heartbeat = datetime.now()

        db.commit()
        return {"message": "已退出编辑"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"结束编辑失败: {str(e)}")

@router.post("/documents/{document_id}/presence")
async def heartbeat_presence(
    document_id: str,
    cursor_position: Optional[int] = None,
    selection_start: Optional[int] = None,
    selection_end: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """编辑心跳与光标位置上报（前端每 5-10 秒调用一次）。"""
    try:
        session = db.query(CollaborationSession).filter(
            CollaborationSession.document_id == document_id,
            CollaborationSession.user_id == current_user.id
        ).first()
        if not session:
            session = CollaborationSession(
                id=str(uuid.uuid4()),
                document_id=document_id,
                user_id=current_user.id,
                user_name=(current_user.real_name or current_user.username),
                session_id=str(uuid.uuid4()),
                is_active=True
            )
            db.add(session)
        session.is_active = True
        session.last_heartbeat = datetime.now()
        if cursor_position is not None:
            session.cursor_position = cursor_position
        if selection_start is not None:
            session.selection_start = selection_start
        if selection_end is not None:
            session.selection_end = selection_end
        db.commit()

        # --- 同步到 Redis：记录用户全局在线与文档在线 ---
        try:
            r = get_redis()
            now = int(time.time())
            # 全局在线标记
            r.set(f"presence:user:{current_user.id}", now, ex=PRESENCE_TTL_SECONDS)
            # 文档在线集合（用 hash 保存 user_id -> ts，给整个 hash 设置 TTL）
            doc_hash = f"presence:doc:{document_id}"
            r.hset(doc_hash, str(current_user.id), now)
            r.expire(doc_hash, PRESENCE_TTL_SECONDS)
        except Exception:
            # 忽略 Redis 错误，不影响主流程
            pass

        return {"ok": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/documents/{document_id}/content")
async def update_document_content(
    document_id: str,
    content_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新文档内容（实时保存）"""
    try:
        print(f"💾 [CollaborationAPI] 更新文档内容: {document_id}")
        
        document = db.query(CollaborationDocument).filter(
            CollaborationDocument.id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查编辑权限
        if not check_document_permission(document, current_user, "edit"):
            raise HTTPException(status_code=403, detail="无权限编辑此文档")
        # 独占锁校验：若被他人锁定，禁止保存
        if getattr(document, 'is_locked', False) and document.locked_by not in (None, current_user.id):
            raise HTTPException(status_code=423, detail="文档已被他人编辑中")
        
        # 更新内容
        document.content = content_data.get("content", "")
        document.last_edited_by = current_user.username
        document.last_edited_at = datetime.now()
        document.edit_count += 1
        # 版本号自增
        previous_version = document.version or 1
        document.version = previous_version + 1

        # 记录编辑内容历史
        history = DocumentEditHistory(
            id=str(uuid.uuid4()),
            document_id=document.id,
            editor_id=current_user.id,
            editor_name=current_user.username,
            action="edit_content",
            changes_summary="编辑内容",
            version_before=previous_version,
            version_after=document.version
        )
        db.add(history)
        
        db.commit()
        
        print(f"✅ [CollaborationAPI] 文档内容更新成功")
        
        return {"message": "内容已保存"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [CollaborationAPI] 更新文档内容失败: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新内容失败: {str(e)}"
        )


@router.get("/documents/{document_id}/content")
async def get_document_content(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文档内容与版本，用于前端轮询同步"""
    doc = db.query(CollaborationDocument).filter(CollaborationDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {
        "content": doc.content or "",
        "version": doc.version or 1,
        "updated_at": (doc.updated_at or datetime.now()).isoformat(),
        "last_edited_by": doc.last_edited_by,
    }


@router.get("/documents/{document_id}/online-users")
async def get_document_online_users(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取某文档的在线用户列表（基于 Redis TTL 与 DB 心跳兜底）。"""
    # 权限：能看文档的人即可查看在线列表
    doc = db.query(CollaborationDocument).filter(CollaborationDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    if not check_document_permission(doc, current_user, "view"):
        raise HTTPException(status_code=403, detail="无权限查看")

    online_map = {}
    try:
        r = get_redis()
        doc_hash = f"presence:doc:{document_id}"
        entries = r.hgetall(doc_hash) or {}
        now_ts = int(time.time())
        for uid, ts in entries.items():
            try:
                ts_int = int(ts)
            except Exception:
                ts_int = 0
            online_map[str(uid)] = (now_ts - ts_int) <= PRESENCE_TTL_SECONDS
    except Exception:
        online_map = {}

    # DB 兜底：最近心跳 <= TTL 的也算在线
    threshold = datetime.now() - timedelta(seconds=PRESENCE_TTL_SECONDS)
    sessions = db.query(CollaborationSession).filter(
        CollaborationSession.document_id == document_id,
        CollaborationSession.last_heartbeat != None,
        CollaborationSession.last_heartbeat >= threshold
    ).all()

    # 汇总用户信息
    result = []
    seen = set()
    for s in sessions:
        uid = str(s.user_id)
        seen.add(uid)
        result.append({
            "user_id": uid,
            "user_name": s.user_name,
            "is_online": online_map.get(uid, True),
            "last_heartbeat": s.last_heartbeat.isoformat() if s.last_heartbeat else None
        })

    # 若 Redis 有而 DB 无，补充在线用户
    for uid, is_on in online_map.items():
        if uid not in seen and is_on:
            user = db.query(User).filter(User.id == uid).first()
            result.append({
                "user_id": uid,
                "user_name": (user.real_name or user.username) if user else uid,
                "is_online": True,
                "last_heartbeat": None
            })

    result.sort(key=lambda x: (not x["is_online"], x["user_name"]))
    return {"users": result}


# ==================== 统计信息 ====================

@router.get("/statistics", response_model=CollaborationStatisticsResponse)
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取协作统计信息"""
    try:
        print(f"📊 [CollaborationAPI] 获取协作统计信息")
        
        # 总文档数
        total_documents = db.query(CollaborationDocument).count()
        
        # 活跃文档数
        active_documents = db.query(CollaborationDocument).filter(
            CollaborationDocument.status == "active"
        ).count()
        
        # 总协作者数（去重）
        total_collaborators = db.query(DocumentCollaborator.user_id).distinct().count()
        
        # 按状态统计
        status_stats = db.query(
            CollaborationDocument.status,
            func.count(CollaborationDocument.id)
        ).group_by(CollaborationDocument.status).all()
        
        documents_by_status = {status: count for status, count in status_stats}
        
        # 按优先级统计
        priority_stats = db.query(
            CollaborationDocument.priority,
            func.count(CollaborationDocument.id)
        ).group_by(CollaborationDocument.priority).all()
        
        documents_by_priority = {priority: count for priority, count in priority_stats}
        
        # 最近活动
        recent_activities = db.query(DocumentEditHistory).options(
            joinedload(DocumentEditHistory.document)
        ).order_by(desc(DocumentEditHistory.created_at)).limit(10).all()
        
        activities = [
            {
                "document_id": activity.document_id,
                "document_title": activity.document.title if activity.document else "未知文档",
                "action": activity.action,
                "user_name": activity.editor_name,
                "created_at": activity.created_at.isoformat()
            }
            for activity in recent_activities
        ]
        
        print(f"✅ [CollaborationAPI] 统计信息获取成功")
        
        return CollaborationStatisticsResponse(
            total_documents=total_documents,
            active_documents=active_documents,
            total_collaborators=total_collaborators,
            documents_by_status=documents_by_status,
            documents_by_priority=documents_by_priority,
            recent_activities=activities
        )
        
    except Exception as e:
        print(f"❌ [CollaborationAPI] 获取统计信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


