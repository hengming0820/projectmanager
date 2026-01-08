from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="pending", index=True)  # ✅ 添加索引 - 提升查询性能
    priority = Column(String(20), default="medium")  # 'low', 'medium', 'high'
    assigned_to = Column(String(36), ForeignKey("users.id"), index=True)  # ✅ 添加索引
    # 冗余存储真实姓名，便于列表直接展示
    assigned_to_name = Column(String(100))
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_by_name = Column(String(100))
    image_url = Column(String(500))
    annotation_data = Column(JSON)  # 存储标注数据
    score = Column(Integer)
    assigned_at = Column(DateTime)
    submitted_at = Column(DateTime)
    reviewed_by = Column(String(36), ForeignKey("users.id"))
    reviewed_by_name = Column(String(100))
    reviewed_at = Column(DateTime)
    review_comment = Column(Text)
    # 跳过相关
    skipped_at = Column(DateTime)
    skip_reason = Column(Text)
    skip_images = Column(JSON)  # 存储跳过原因截图URL列表
    # 跳过申请相关
    skip_requested_at = Column(DateTime)
    skip_request_reason = Column(Text)
    skip_request_images = Column(JSON)  # 存储跳过申请截图URL列表
    skip_requested_by = Column(String(36), ForeignKey("users.id"))
    skip_reviewed_at = Column(DateTime)
    skip_reviewed_by = Column(String(36), ForeignKey("users.id"))
    skip_review_comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), index=True)  # ✅ 添加索引 - 用于排序
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to])
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    reviewer = relationship("User", back_populates="reviewed_tasks", foreign_keys=[reviewed_by])
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
    # 时间轴事件（JSON 数组）
    timeline = Column(JSON, default=list)
    
    # ✅ 添加复合索引 - 针对常用查询组合优化
    __table_args__ = (
        Index('idx_task_project_status', 'project_id', 'status'),  # 按项目和状态查询
        Index('idx_task_status_assigned', 'status', 'assigned_to'),  # 按状态和分配人查询
    )

class TaskAttachment(Base):
    __tablename__ = "task_attachments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    attachment_type = Column(String(50))  # 'annotation_screenshot', 'review_screenshot', 'medical_image'
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    task = relationship("Task", back_populates="attachments")
    uploader = relationship("User") 