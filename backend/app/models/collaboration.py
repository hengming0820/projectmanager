"""
团队协作文档相关数据模型
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.user import User
import uuid


class CollaborationDocument(Base):
    """协作文档模型"""
    __tablename__ = "collaboration_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, comment="文档标题")
    description = Column(Text, comment="文档描述")
    content = Column(Text, default="", comment="文档内容（富文本HTML）")
    
    # 状态和优先级
    status = Column(String(20), default="draft", comment="状态: draft, active, completed, archived")
    priority = Column(String(20), default="normal", comment="优先级: low, normal, high, urgent")
    
    # 所有者信息
    owner_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="所有者ID")
    owner_name = Column(String(100), nullable=False, comment="所有者姓名")
    
    # 项目关联
    project_id = Column(String(50), comment="关联项目ID")
    project_name = Column(String(200), comment="关联项目名称")
    
    # 分类和标签
    category = Column(String(100), comment="文档分类")
    tags = Column(JSON, default=list, comment="标签列表")
    
    # 编辑信息
    last_edited_by = Column(String(100), comment="最后编辑者")
    last_edited_at = Column(DateTime(timezone=True), comment="最后编辑时间")
    
    # 统计信息
    view_count = Column(Integer, default=0, comment="查看次数")
    edit_count = Column(Integer, default=0, comment="编辑次数")
    
    # 版本控制
    version = Column(Integer, default=1, comment="文档版本")
    is_locked = Column(Boolean, default=False, comment="是否被锁定")
    locked_by = Column(String(50), comment="锁定者ID")
    locked_at = Column(DateTime(timezone=True), comment="锁定时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    owner = relationship("User", foreign_keys=[owner_id])
    collaborators = relationship("DocumentCollaborator", back_populates="document", cascade="all, delete-orphan")
    edit_history = relationship("DocumentEditHistory", back_populates="document", cascade="all, delete-orphan")
    comments = relationship("DocumentComment", back_populates="document", cascade="all, delete-orphan")


class DocumentCollaborator(Base):
    """文档协作者模型"""
    __tablename__ = "document_collaborators"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(50), ForeignKey("collaboration_documents.id"), nullable=False, comment="文档ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="用户ID")
    user_name = Column(String(100), nullable=False, comment="用户姓名")
    user_avatar = Column(String(500), comment="用户头像")
    
    role = Column(String(20), default="editor", comment="角色: owner, editor, viewer")
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), comment="加入时间")
    last_active_at = Column(DateTime(timezone=True), comment="最后活跃时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    document = relationship("CollaborationDocument", back_populates="collaborators")
    user = relationship("User", foreign_keys=[user_id])


class DocumentEditHistory(Base):
    """文档编辑历史模型"""
    __tablename__ = "document_edit_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(50), ForeignKey("collaboration_documents.id"), nullable=False, comment="文档ID")
    editor_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="编辑者ID")
    editor_name = Column(String(100), nullable=False, comment="编辑者姓名")
    
    action = Column(String(20), nullable=False, comment="操作类型: create, update, delete, lock, unlock")
    changes_summary = Column(Text, comment="变更摘要")
    content_diff = Column(Text, comment="内容差异")
    
    # 版本信息
    version_before = Column(Integer, comment="变更前版本")
    version_after = Column(Integer, comment="变更后版本")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    document = relationship("CollaborationDocument", back_populates="edit_history")
    editor = relationship("User", foreign_keys=[editor_id])


class DocumentComment(Base):
    """文档评论模型"""
    __tablename__ = "document_comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(50), ForeignKey("collaboration_documents.id"), nullable=False, comment="文档ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="用户ID")
    user_name = Column(String(100), nullable=False, comment="用户姓名")
    user_avatar = Column(String(500), comment="用户头像")
    
    content = Column(Text, nullable=False, comment="评论内容")
    position = Column(Integer, comment="在文档中的位置")
    parent_id = Column(String(50), ForeignKey("document_comments.id"), comment="父评论ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    document = relationship("CollaborationDocument", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])
    parent = relationship("DocumentComment", remote_side="DocumentComment.id")
    replies = relationship("DocumentComment", remote_side="DocumentComment.parent_id")


class CollaborationSession(Base):
    """协作会话模型（用于实时协作状态）"""
    __tablename__ = "collaboration_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(50), ForeignKey("collaboration_documents.id"), nullable=False, comment="文档ID")
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="用户ID")
    user_name = Column(String(100), nullable=False, comment="用户姓名")
    
    # 会话信息
    session_id = Column(String(100), nullable=False, comment="会话ID")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    
    # 编辑状态
    cursor_position = Column(Integer, comment="光标位置")
    selection_start = Column(Integer, comment="选择开始位置")
    selection_end = Column(Integer, comment="选择结束位置")
    
    # 时间信息
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now(), comment="最后心跳时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    document = relationship("CollaborationDocument")
    user = relationship("User", foreign_keys=[user_id])
