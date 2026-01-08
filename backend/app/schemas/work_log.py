from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

class WorkLogStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"

class WorkLogPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class WorkWeekStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

# 工作日志类型相关
class WorkLogTypeBase(BaseModel):
    name: str = Field(..., max_length=100, description="类型名称")
    description: Optional[str] = Field(None, description="类型描述")
    color: str = Field("#409EFF", max_length=7, description="显示颜色")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    is_active: bool = Field(True, description="是否启用")
    sort_order: int = Field(0, description="排序")

class WorkLogTypeCreate(WorkLogTypeBase):
    pass

class WorkLogTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None

class WorkLogTypeResponse(WorkLogTypeBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 工作周相关
class WorkWeekBase(BaseModel):
    title: str = Field(..., max_length=255, description="工作周标题")
    week_start_date: date = Field(..., description="周开始日期（周一）")
    week_end_date: date = Field(..., description="周结束日期（周五）")
    description: Optional[str] = Field(None, description="工作周描述")
    config: Optional[Dict[str, Any]] = Field(None, description="周配置信息")

class WorkWeekCreate(WorkWeekBase):
    @validator('week_start_date', 'week_end_date', pre=True)
    def _coerce_date(cls, value):
        """Accept 'YYYY-MM-DD' strings and convert to date."""
        if isinstance(value, str):
            try:
                # Prefer ISO format
                return datetime.strptime(value, '%Y-%m-%d').date()
            except Exception:
                try:
                    # Fallback to fromisoformat if available formats differ
                    return date.fromisoformat(value)
                except Exception:
                    raise ValueError('Invalid date format, expected YYYY-MM-DD')
        return value

class WorkWeekUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[WorkWeekStatus] = None
    config: Optional[Dict[str, Any]] = None

class WorkWeekResponse(WorkWeekBase):
    id: str
    status: WorkWeekStatus
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    # 统计信息
    total_entries: Optional[int] = Field(None, description="总条目数")
    submitted_entries: Optional[int] = Field(None, description="已提交条目数")
    completion_rate: Optional[float] = Field(None, description="完成率")
    
    class Config:
        from_attributes = True

# 工作日志条目相关
class WorkLogEntryBase(BaseModel):
    work_date: date = Field(..., description="工作日期")
    work_content: Optional[str] = Field(None, description="工作内容描述")
    work_type: Optional[str] = Field(None, max_length=50, description="工作类型")
    priority: WorkLogPriority = Field(WorkLogPriority.NORMAL, description="优先级")
    planned_hours: int = Field(8, ge=0, le=24, description="计划工作小时数")
    actual_hours: Optional[int] = Field(None, ge=0, le=24, description="实际工作小时数")
    completion_rate: int = Field(0, ge=0, le=100, description="完成率")
    difficulties: Optional[str] = Field(None, description="遇到的困难")
    next_day_plan: Optional[str] = Field(None, description="次日计划")
    remarks: Optional[str] = Field(None, description="备注")

class WorkLogEntryCreate(WorkLogEntryBase):
    work_week_id: str = Field(..., description="工作周ID")

class WorkLogEntryUpdate(BaseModel):
    work_content: Optional[str] = None
    work_type: Optional[str] = Field(None, max_length=50)
    priority: Optional[WorkLogPriority] = None
    planned_hours: Optional[int] = Field(None, ge=0, le=24)
    actual_hours: Optional[int] = Field(None, ge=0, le=24)
    completion_rate: Optional[int] = Field(None, ge=0, le=100)
    difficulties: Optional[str] = None
    next_day_plan: Optional[str] = None
    remarks: Optional[str] = None

class WorkLogEntrySubmit(BaseModel):
    """提交工作日志"""
    actual_hours: int = Field(..., ge=0, le=24, description="实际工作小时数")
    completion_rate: int = Field(..., ge=0, le=100, description="完成率")
    remarks: Optional[str] = Field(None, description="提交备注")

class WorkLogEntryReview(BaseModel):
    """审核工作日志"""
    status: WorkLogStatus = Field(..., description="审核状态")
    review_comment: Optional[str] = Field(None, description="审核意见")

class WorkLogEntryResponse(WorkLogEntryBase):
    id: str
    work_week_id: str
    user_id: str
    day_of_week: int
    status: WorkLogStatus
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[str]
    review_comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    user_name: Optional[str] = Field(None, description="用户姓名")
    reviewer_name: Optional[str] = Field(None, description="审核人姓名")
    work_type_info: Optional[WorkLogTypeResponse] = Field(None, description="工作类型信息")
    
    class Config:
        from_attributes = True

# 工作周汇总统计
class WorkWeekSummary(BaseModel):
    work_week_id: str
    user_id: str
    user_name: str
    total_planned_hours: int
    total_actual_hours: int
    average_completion_rate: float
    submitted_days: int
    total_days: int
    status_summary: Dict[str, int]  # 各状态的天数统计
    total_entries: int = 0  # 日志条目总数
    work_type_hours: Dict[str, int] = {}  # 按工作类型统计的工时

class WorkWeekStatistics(BaseModel):
    work_week: WorkWeekResponse
    user_summaries: List[WorkWeekSummary]
    overall_stats: Dict[str, Any]

# 批量操作
class WorkLogBatchCreate(BaseModel):
    """批量创建工作日志条目（为工作周的所有用户创建空白条目）"""
    work_week_id: str
    user_ids: List[str]
    
class WorkLogBatchUpdate(BaseModel):
    """批量更新工作日志条目"""
    entry_ids: List[str]
    updates: WorkLogEntryUpdate

# 查询参数
class WorkLogQueryParams(BaseModel):
    work_week_id: Optional[str] = None
    user_id: Optional[str] = None
    work_date_start: Optional[date] = None
    work_date_end: Optional[date] = None
    status: Optional[List[WorkLogStatus]] = None
    work_type: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

class WorkWeekQueryParams(BaseModel):
    status: Optional[WorkWeekStatus] = None
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    created_by: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

