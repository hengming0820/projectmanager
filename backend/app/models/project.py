from sqlalchemy import Column, String, DateTime, Text, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(20), default="active", index=True)  # ✅ 添加索引 - 用于过滤完结项目
    priority = Column(String(20), default="medium")  # 'low', 'medium', 'high'
    category = Column(String(50))  # 'case', 'ai_annotation'
    sub_category = Column(String(50))  # case: 'trial', 'research', 'paid'; ai_annotation: 'research', 'daily'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    assigned_tasks = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    creator = relationship("User", back_populates="created_projects", foreign_keys=[created_by])
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    stats = relationship("ProjectStats", back_populates="project", uselist=False, cascade="all, delete-orphan") 