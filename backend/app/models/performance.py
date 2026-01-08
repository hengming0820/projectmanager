from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class PerformanceStats(Base):
    __tablename__ = "performance_stats"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    period = Column(String(20), nullable=False)  # 'daily', 'weekly', 'monthly', 'yearly'
    date = Column(String(10), nullable=False)  # YYYY-MM-DD or YYYY-MM or YYYY
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    approved_tasks = Column(Integer, default=0)
    rejected_tasks = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    average_score = Column(DECIMAL(5, 2), default=0)
    total_hours = Column(DECIMAL(5, 2), default=0)
    average_hours = Column(DECIMAL(5, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="performance_stats")

class ProjectStats(Base):
    __tablename__ = "project_stats"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    total_tasks = Column(Integer, default=0)
    pending_tasks = Column(Integer, default=0)
    in_progress_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    approved_tasks = Column(Integer, default=0)
    rejected_tasks = Column(Integer, default=0)
    completion_rate = Column(DECIMAL(5, 2), default=0)
    average_score = Column(DECIMAL(5, 2), default=0)
    total_hours = Column(DECIMAL(8, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    project = relationship("Project", back_populates="stats") 