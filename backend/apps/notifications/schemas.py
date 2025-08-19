from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class NotificationResponse(BaseModel):
    """Schema para resposta de notificação"""
    id: str
    tenant_id: str
    process_id: Optional[str]
    user_id: str
    notification_type: str
    priority: str
    title: str
    message: str
    is_read: bool
    is_archived: bool
    should_email: bool
    should_push: bool
    should_sms: bool
    metadata: Dict[str, Any]
    created_at: datetime
    read_at: Optional[datetime]
    archived_at: Optional[datetime]

class NotificationListResponse(BaseModel):
    """Schema para resposta de lista de notificações"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    per_page: int
    total_pages: int

class NotificationPreferenceResponse(BaseModel):
    """Schema para resposta de preferências de notificação"""
    id: str
    tenant_id: str
    user_id: str
    deadline_notifications: bool
    court_updates: bool
    hearing_reminders: bool
    judgment_notifications: bool
    urgent_processes: bool
    email_enabled: bool
    push_enabled: bool
    sms_enabled: bool
    deadline_reminder_days: int
    daily_summary: bool
    weekly_summary: bool
    created_at: datetime
    updated_at: Optional[datetime]

class NotificationPreferenceUpdate(BaseModel):
    """Schema para atualização de preferências"""
    deadline_notifications: Optional[bool] = None
    court_updates: Optional[bool] = None
    hearing_reminders: Optional[bool] = None
    judgment_notifications: Optional[bool] = None
    urgent_processes: Optional[bool] = None
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    deadline_reminder_days: Optional[int] = None
    daily_summary: Optional[bool] = None
    weekly_summary: Optional[bool] = None
    
    @validator('deadline_reminder_days')
    def validate_deadline_reminder_days(cls, v):
        if v is not None and (v < 1 or v > 30):
            raise ValueError("Dias de lembrança devem estar entre 1 e 30")
        return v

class NotificationStats(BaseModel):
    """Schema para estatísticas de notificações"""
    total_notifications: int
    unread_notifications: int
    notifications_today: int
    notifications_this_week: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]

class MarkNotificationReadRequest(BaseModel):
    """Schema para marcar notificação como lida"""
    notification_id: str

class ArchiveNotificationRequest(BaseModel):
    """Schema para arquivar notificação"""
    notification_id: str
