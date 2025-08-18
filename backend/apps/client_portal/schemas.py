from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ClientProcessResponse(BaseModel):
    """Schema para resposta de processo do cliente"""
    id: str
    subject: str
    cnj_number: Optional[str] = None
    court: Optional[str] = None
    jurisdiction: Optional[str] = None
    status: str
    priority: str
    estimated_value: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ClientDocumentResponse(BaseModel):
    """Schema para resposta de documento do cliente"""
    id: str
    title: str
    description: Optional[str] = None
    file_type: str
    file_size: int
    uploaded_at: str
    is_shared: bool

class ClientMessageCreate(BaseModel):
    """Schema para criação de mensagem do cliente"""
    subject: str
    message: str
    priority: Optional[str] = "normal"

class ClientMessageResponse(BaseModel):
    """Schema para resposta de mensagem do cliente"""
    id: str
    subject: str
    message: str
    priority: str
    status: str
    created_at: str
    replied_at: Optional[str] = None
