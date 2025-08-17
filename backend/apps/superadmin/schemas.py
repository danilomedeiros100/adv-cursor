from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Schemas para Tenant
class TenantCreate(BaseModel):
    name: str
    slug: str
    email: str
    phone: Optional[str] = None
    plan_type: str = "free"
    max_users: int = 5
    max_processes: int = 100
    # Campos para criar usuário owner automaticamente
    owner_name: Optional[str] = None
    owner_password: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_oab_number: Optional[str] = None
    owner_oab_state: Optional[str] = None
    owner_position: Optional[str] = None
    owner_department: Optional[str] = None

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    plan_type: Optional[str] = None
    max_users: Optional[int] = None
    max_processes: Optional[int] = None
    is_active: Optional[bool] = None
    is_suspended: Optional[bool] = None

class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    email: str
    phone: Optional[str]
    plan_type: str
    plan_features: Dict[str, Any]
    max_users: int
    max_processes: int
    is_active: bool
    is_suspended: bool
    settings: Dict[str, Any]
    branding: Dict[str, Any]
    created_at: datetime
    owner_created: Optional[bool] = None
    owner_email: Optional[str] = None

# Schemas para User
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    oab_number: Optional[str] = None
    oab_state: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    oab_number: Optional[str]
    oab_state: Optional[str]
    position: Optional[str]
    department: Optional[str]
    is_active: bool
    is_super_admin: bool
    email_verified: bool
    phone_verified: bool
    preferences: Dict[str, Any]
    timezone: str
    language: str
    created_at: datetime

# Schemas para TenantUser
class TenantUserCreate(BaseModel):
    user_id: str
    role: str = "user"
    permissions: Dict[str, bool] = {}
    department: Optional[str] = None
    position: Optional[str] = None

class TenantSuspendRequest(BaseModel):
    reason: str
