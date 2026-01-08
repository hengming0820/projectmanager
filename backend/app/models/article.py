"""
文章发布模块数据模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Article(Base):
    __tablename__ = "articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, default="", comment="内容（富文本HTML）")
    summary = Column(Text, comment="摘要")
    type = Column(String(50), nullable=False, comment="类型：支持任意值，如meeting、model_test、需求文档、设计文档等")
    status = Column(String(20), default="draft", comment="状态：draft, published")
    tags = Column(JSON, default=list, comment="标签")
    # 新增：封面、分类、可见性
    cover_url = Column(String(500), comment="封面图片URL")
    category = Column(String(50), comment="文章分类标签")
    is_public = Column(Boolean, default=True, comment="是否公开可见")

    # 访问与归属扩展
    editable_user_ids = Column(JSON, default=list, comment="可编辑用户ID列表")
    editable_roles = Column(JSON, default=list, comment="可编辑角色编码列表，如 reviewer/annotator/admin")
    departments = Column(JSON, default=list, comment="文章所属部门（名称或编码）")

    author_id = Column(String(50), ForeignKey("users.id"), nullable=False, comment="作者ID")
    author_name = Column(String(100), nullable=False, comment="作者姓名")

    # 项目关联（可选，为空表示公共文章）
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, comment="所属项目ID")

    view_count = Column(Integer, default=0)
    edit_count = Column(Integer, default=0)
    version = Column(Integer, default=1)

    # 编辑锁机制
    is_locked = Column(Boolean, default=False, comment="是否被锁定（有人正在编辑）")
    locked_by = Column(String(50), nullable=True, comment="锁定者用户ID")
    locked_at = Column(DateTime(timezone=True), nullable=True, comment="锁定时间")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系：级联删除编辑历史
    edit_history = relationship("ArticleEditHistory", cascade="all, delete-orphan", backref="article")
    
    # 关系：所属项目
    project = relationship("Project", backref="articles")


class ArticleEditHistory(Base):
    __tablename__ = "article_edit_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), ForeignKey("articles.id"), nullable=False)
    editor_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    editor_name = Column(String(100), nullable=False)
    action = Column(String(30), nullable=False, comment="create, update, publish, delete, edit_content")
    changes_summary = Column(Text)
    version_before = Column(Integer)
    version_after = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


