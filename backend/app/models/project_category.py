"""
项目分类模型
用于存储项目的自定义文章分类（如会议记录、模型测试等）
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import uuid


class ProjectCategory(Base):
    """项目分类模型"""
    __tablename__ = "project_categories"
    __table_args__ = {'comment': '项目文章分类表'}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="分类ID")
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, comment="所属项目ID")
    name = Column(String(100), nullable=False, comment="分类名称（显示名）")
    type = Column(String(50), nullable=False, comment="分类类型标识（用于article.type）")
    icon = Column(String(50), nullable=True, comment="图标")
    description = Column(Text, nullable=True, comment="分类描述")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    project = relationship("Project", backref="categories")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "type": self.type,
            "icon": self.icon,
            "description": self.description,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

