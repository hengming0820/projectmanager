from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class WorkWeek(Base):
    """工作周模板表"""
    __tablename__ = "work_weeks"
    
    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="工作周标题")
    week_start_date = Column(Date, nullable=False, comment="周开始日期（周一）")
    week_end_date = Column(Date, nullable=False, comment="周结束日期（周五）")
    description = Column(Text, comment="工作周描述")
    status = Column(String(20), default="active", comment="状态: active, archived, deleted")
    
    # 配置信息
    config = Column(JSON, comment="周配置信息（如工作日类型、要求等）")
    
    # 创建信息
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    entries = relationship("WorkLogEntry", back_populates="work_week", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])

class WorkLogEntry(Base):
    """工作日志条目表"""
    __tablename__ = "work_log_entries"
    
    id = Column(String(36), primary_key=True, index=True)
    work_week_id = Column(String(36), ForeignKey("work_weeks.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    work_date = Column(Date, nullable=False, comment="工作日期")
    day_of_week = Column(Integer, nullable=False, comment="星期几(1-7, 1=周一)")
    
    # 工作内容
    work_content = Column(Text, comment="工作内容描述")
    work_type = Column(String(50), comment="工作类型（开发、测试、会议、学习等）")
    priority = Column(String(20), default="normal", comment="优先级: low, normal, high, urgent")
    
    # 时间统计
    planned_hours = Column(Integer, default=8, comment="计划工作小时数")
    actual_hours = Column(Integer, comment="实际工作小时数")
    
    # 状态
    status = Column(String(20), default="pending", comment="状态: pending, submitted, approved, rejected")
    completion_rate = Column(Integer, default=0, comment="完成率(0-100)")
    
    # 附加信息
    difficulties = Column(Text, comment="遇到的困难")
    next_day_plan = Column(Text, comment="次日计划")
    remarks = Column(Text, comment="备注")
    
    # 时间戳
    submitted_at = Column(DateTime, comment="提交时间")
    reviewed_at = Column(DateTime, comment="审核时间")
    reviewed_by = Column(String(36), ForeignKey("users.id"), comment="审核人")
    review_comment = Column(Text, comment="审核意见")
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    work_week = relationship("WorkWeek", back_populates="entries")
    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

class WorkLogType(Base):
    """工作日志类型配置表"""
    __tablename__ = "work_log_types"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="类型名称")
    description = Column(Text, comment="类型描述")
    color = Column(String(7), default="#409EFF", comment="显示颜色")
    icon = Column(String(50), comment="图标")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

