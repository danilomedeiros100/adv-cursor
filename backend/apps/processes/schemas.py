from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProcessCreate(BaseModel):
    subject: str
    cnj_number: Optional[str] = None
    court: Optional[str] = None
    jurisdiction: Optional[str] = None
    client_id: str
    specialty_id: Optional[str] = None  # Mantido para compatibilidade
    specialty_ids: Optional[List[str]] = None  # Novas especialidades
    priority: str = "normal"
    estimated_value: Optional[int] = None  # Em centavos
    notes: Optional[str] = None
    is_confidential: bool = False
    requires_attention: bool = False
    lawyers: List[Dict[str, Any]] = []

class ProcessUpdate(BaseModel):
    subject: Optional[str] = None
    cnj_number: Optional[str] = None
    court: Optional[str] = None
    jurisdiction: Optional[str] = None
    client_id: Optional[str] = None
    specialty_id: Optional[str] = None  # Mantido para compatibilidade
    specialty_ids: Optional[List[str]] = None  # Novas especialidades
    priority: Optional[str] = None
    estimated_value: Optional[int] = None  # Em centavos
    notes: Optional[str] = None
    is_confidential: Optional[bool] = None
    requires_attention: Optional[bool] = None
    status: Optional[str] = None

class ProcessResponse(BaseModel):
    id: str
    tenant_id: str
    subject: str
    cnj_number: Optional[str]
    court: Optional[str]
    jurisdiction: Optional[str]
    client_id: str
    specialty_id: Optional[str]  # Mantido para compatibilidade
    priority: str
    estimated_value: Optional[int]  # Em centavos
    notes: Optional[str]
    is_confidential: bool
    requires_attention: bool
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    
    # Relacionamentos
    client: Optional[Dict[str, Any]] = None
    specialty: Optional[Dict[str, Any]] = None  # Mantido para compatibilidade
    specialties: Optional[List[Dict[str, Any]]] = None  # Novas especialidades
    lawyers: Optional[List[Dict[str, Any]]] = None

class ProcessLawyerCreate(BaseModel):
    lawyer_id: str
    role: str = "lawyer"  # lawyer, assistant, coordinator
    is_primary: bool = False
    can_sign_documents: bool = True
    can_manage_process: bool = True
    can_view_financial: bool = False
