from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PerformanceStatsResponse(BaseModel):
    id: str
    user_id: str
    period: str
    date: str
    total_tasks: int
    completed_tasks: int
    approved_tasks: int
    rejected_tasks: int
    total_score: int
    average_score: Decimal
    total_hours: Decimal
    average_hours: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectStatsResponse(BaseModel):
    id: str
    project_id: str
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    approved_tasks: int
    rejected_tasks: int
    completion_rate: Decimal
    average_score: Decimal
    total_hours: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PersonalPerformanceResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    total_score: int
    average_score: float
    completion_rate: float 