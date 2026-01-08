"""
团队协作文档相关的 Pydantic 模式
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# 枚举类型
class CollaborationStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CollaborationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class CollaboratorRole(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class EditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOCK = "lock"
    UNLOCK = "unlock"


# 基础模式
class CollaboratorBase(BaseModel):
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None
    role: CollaboratorRole


class CollaboratorCreate(BaseModel):
    user_id: str
    role: CollaboratorRole = CollaboratorRole.EDITOR


class CollaboratorUpdate(BaseModel):
    role: CollaboratorRole


class CollaboratorResponse(CollaboratorBase):
    id: str
    document_id: str
    joined_at: datetime
    last_active_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 文档编辑历史
class DocumentEditHistoryResponse(BaseModel):
    id: str
    document_id: str
    editor_id: str
    editor_name: str
    action: EditAction
    changes_summary: Optional[str] = None
    content_diff: Optional[str] = None
    version_before: Optional[int] = None
    version_after: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# 文档评论
class DocumentCommentCreate(BaseModel):
    content: str
    position: Optional[int] = None
    parent_id: Optional[str] = None


class DocumentCommentResponse(BaseModel):
    id: str
    document_id: str
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None
    content: str
    position: Optional[int] = None
    parent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 协作文档
class CollaborationDocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    description: Optional[str] = Field(None, max_length=1000, description="文档描述")
    content: Optional[str] = Field("", description="文档内容")
    priority: CollaborationPriority = CollaborationPriority.NORMAL
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100, description="文档分类")
    tags: List[str] = Field(default_factory=list, description="标签列表")


class CollaborationDocumentCreate(CollaborationDocumentBase):
    collaborator_ids: Optional[List[str]] = Field(default_factory=list, description="初始协作者ID列表")


class CollaborationDocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    content: Optional[str] = None
    status: Optional[CollaborationStatus] = None
    priority: Optional[CollaborationPriority] = None
    project_id: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None


class CollaborationDocumentResponse(CollaborationDocumentBase):
    id: str
    status: CollaborationStatus
    owner_id: str
    owner_name: str
    collaborators: List[CollaboratorResponse] = []
    last_edited_by: Optional[str] = None
    last_edited_at: Optional[datetime] = None
    view_count: int = 0
    edit_count: int = 0
    version: int = 1
    is_locked: bool = False
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 查询参数
class CollaborationDocumentQueryParams(BaseModel):
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    status: Optional[CollaborationStatus] = None
    priority: Optional[CollaborationPriority] = None
    project_id: Optional[str] = None
    category: Optional[str] = None
    tag: Optional[str] = None
    search: Optional[str] = Field(None, description="搜索关键词")
    owner_id: Optional[str] = None
    collaborator_id: Optional[str] = None
    created_start: Optional[datetime] = None
    created_end: Optional[datetime] = None
    sort_by: str = Field("updated_at", description="排序字段")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="排序方向")


# 列表响应
class CollaborationDocumentListResponse(BaseModel):
    items: List[CollaborationDocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# 协作状态
class ActiveEditor(BaseModel):
    user_id: str
    user_name: str
    cursor_position: Optional[int] = None
    selection_range: Optional[Dict[str, int]] = None
    last_active: datetime


class CollaborationStateResponse(BaseModel):
    document_id: str
    active_editors: List[ActiveEditor] = []
    is_locked: bool = False
    locked_by: Optional[str] = None


# 统计信息
class RecentActivity(BaseModel):
    document_id: str
    document_title: str
    action: str
    user_name: str
    created_at: str


class CollaborationStatisticsResponse(BaseModel):
    total_documents: int
    active_documents: int
    total_collaborators: int
    documents_by_status: Dict[str, int]
    documents_by_priority: Dict[str, int]
    recent_activities: List[RecentActivity]


# 内容更新
class DocumentContentUpdate(BaseModel):
    content: str = Field(..., description="文档内容")


# 锁定响应
class DocumentLockResponse(BaseModel):
    message: str
    locked_by: str


# 解锁响应
class DocumentUnlockResponse(BaseModel):
    message: str


# 搜索响应
class SearchResult(BaseModel):
    documents: List[CollaborationDocumentResponse]
    total: int
    query: str
    filters: Dict[str, Any]


# 导出配置
class ExportConfig(BaseModel):
    format: str = Field("html", pattern="^(html|pdf|docx|markdown)$")
    include_comments: bool = False
    include_history: bool = False


# WebSocket 消息类型
class WSMessageType(str, Enum):
    JOIN_DOCUMENT = "join_document"
    LEAVE_DOCUMENT = "leave_document"
    CONTENT_CHANGE = "content_change"
    CURSOR_POSITION = "cursor_position"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    DOCUMENT_LOCKED = "document_locked"
    DOCUMENT_UNLOCKED = "document_unlocked"


class WSMessage(BaseModel):
    type: WSMessageType
    document_id: str
    user_id: str
    user_name: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# 实时协作消息
class ContentChangeMessage(BaseModel):
    document_id: str
    user_id: str
    user_name: str
    content: str
    cursor_position: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class CursorPositionMessage(BaseModel):
    document_id: str
    user_id: str
    user_name: str
    cursor_position: int
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class UserPresenceMessage(BaseModel):
    document_id: str
    user_id: str
    user_name: str
    action: str  # "joined" or "left"
    timestamp: datetime = Field(default_factory=datetime.now)
