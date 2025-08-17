from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProcessCreate(BaseModel):
    title: str
    description: Optional[str] = None
    process_number: Optional[str] = None
    court: Optional[str] = None
    specialty_id: Optional[str] = None
    client_id: Optional[str] = None
    status: str = "pending"
    priority: str = "normal"
    estimated_value: Optional[float] = None
    start_date: Optional[datetime] = None
    expected_end_date: Optional[datetime] = None

class ProcessUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    process_number: Optional[str] = None
    court: Optional[str] = None
    specialty_id: Optional[str] = None
    client_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_value: Optional[float] = None
    start_date: Optional[datetime] = None
    expected_end_date: Optional[datetime] = None

class ProcessResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: Optional[str]
    process_number: Optional[str]
    court: Optional[str]
    specialty_id: Optional[str]
    client_id: Optional[str]
    status: str
    priority: str
    estimated_value: Optional[float]
    start_date: Optional[datetime]
    expected_end_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

class ProcessLawyerCreate(BaseModel):
    lawyer_id: str
    role: str = "primary"  # primary, secondary, assistant
