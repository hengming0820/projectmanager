from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: str
    priority: str = "medium"
    image_url: Optional[str] = None
    score: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    image_url: Optional[str] = None
    score: Optional[int] = None
    # 跳过相关可选字段
    skip_reason: Optional[str] = None
    skip_images: Optional[List[str]] = None

class TaskSubmit(BaseModel):
    annotation_data: Dict[str, Any]
    comment: Optional[str] = None  # 标注说明改为可选
    organ_count: int

class TaskReview(BaseModel):
    action: str  # 'approve' or 'reject'
    comment: Optional[str] = None  # 审核意见改为可选（通过时可选，驳回时在业务逻辑中验证）
    score: Optional[int] = None  # 任务评分
    reject_images: Optional[List[str]] = None  # 审核打回截图URL列表（可选）

class TaskSkip(BaseModel):
    reason: str
    images: Optional[List[str]] = None

class TaskSkipRequest(BaseModel):
    reason: str
    images: Optional[List[str]] = None

class TaskSkipReview(BaseModel):
    approved: bool
    comment: str

class TaskAttachmentResponse(BaseModel):
    id: str
    file_name: str
    file_url: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    attachment_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskResponse(TaskBase):
    id: str
    status: str
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    created_by: str
    created_by_name: Optional[str] = None
    annotation_data: Optional[Dict[str, Any]] = None
    assigned_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_by_name: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_comment: Optional[str] = None
    # 跳过相关
    skipped_at: Optional[datetime] = None
    skip_reason: Optional[str] = None
    skip_images: Optional[List[str]] = None
    # 跳过申请相关
    skip_requested_at: Optional[datetime] = None
    skip_request_reason: Optional[str] = None
    skip_request_images: Optional[List[str]] = None
    skip_requested_by: Optional[str] = None
    skip_reviewed_at: Optional[datetime] = None
    skip_reviewed_by: Optional[str] = None
    skip_review_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    attachments: List[TaskAttachmentResponse] = []
    timeline: Optional[List[Dict[str, Any]]] = None
    
    # 添加计算属性以包含项目名称
    project_name: Optional[str] = None
    
    @property
    def projectName(self) -> Optional[str]:
        """为前端兼容性提供项目名称"""
        return self.project_name
    
    class Config:
        from_attributes = True 