from sqlalchemy import Column, String, DateTime, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    real_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'admin' or 'annotator'
    avatar_url = Column(String(500))
    department = Column(String(100))
    status = Column(String(20), default="active")  # 'active' or 'inactive'
    tags = Column(Text)  # 存储用户标签的JSON字符串
    hire_date = Column(Date)  # 入职日期
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    created_projects = relationship("Project", back_populates="creator", foreign_keys="Project.created_by")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assigned_to")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by")
    reviewed_tasks = relationship("Task", back_populates="reviewer", foreign_keys="Task.reviewed_by")
    performance_stats = relationship("PerformanceStats", back_populates="user") 