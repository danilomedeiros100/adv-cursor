from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    LAWYER = "lawyer"
    ASSISTANT = "assistant"
    SECRETARY = "secretary"
    RECEPTIONIST = "receptionist"
    USER = "user"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    birth_date: Optional[datetime] = None
    cpf: Optional[str] = None
    oab_number: Optional[str] = None
    oab_state: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    preferences: Optional[Dict[str, Any]] = None
    timezone: str = "America/Sao_Paulo"
    language: str = "pt-BR"

    @validator('name')
    def validate_name(cls, v):
        """Valida nome do usuário"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Nome é obrigatório")
        if len(v) > 255:
            raise ValueError("Nome deve ter no máximo 255 caracteres")
        return v.strip()

    @validator('oab_number', 'oab_state')
    def validate_oab_fields(cls, v, values):
        """Valida campos OAB quando role é lawyer"""
        if values.get('role') == UserRole.LAWYER:
            if 'oab_number' in values and not values['oab_number']:
                raise ValueError("Número OAB é obrigatório para advogados")
            if 'oab_state' in values and not values['oab_state']:
                raise ValueError("Estado OAB é obrigatório para advogados")
        return v

    @validator('password')
    def validate_password(cls, v):
        """Valida senha"""
        if len(v) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        return v

    @validator('cpf')
    def validate_cpf(cls, v):
        """Valida CPF"""
        if v:
            # Remove caracteres não numéricos
            cpf_clean = ''.join(filter(str.isdigit, v))
            if len(cpf_clean) != 11:
                raise ValueError("CPF deve ter 11 dígitos")
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birth_date: Optional[datetime] = None
    cpf: Optional[str] = None
    oab_number: Optional[str] = None
    oab_state: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    language: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        """Valida nome do usuário"""
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Nome não pode estar vazio")
            if len(v) > 255:
                raise ValueError("Nome deve ter no máximo 255 caracteres")
            return v.strip()
        return v

    @validator('oab_number', 'oab_state')
    def validate_oab_fields(cls, v, values):
        """Valida campos OAB quando role é lawyer"""
        if values.get('role') == UserRole.LAWYER:
            if 'oab_number' in values and not values['oab_number']:
                raise ValueError("Número OAB é obrigatório para advogados")
            if 'oab_state' in values and not values['oab_state']:
                raise ValueError("Estado OAB é obrigatório para advogados")
        return v

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        """Valida nova senha"""
        if len(v) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        return v

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    birth_date: Optional[datetime]
    cpf: Optional[str]
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
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    role: Optional[str] = None
    tenant_permissions: Optional[Dict[str, Any]] = None

class TenantUserCreate(BaseModel):
    user_id: str
    role: UserRole
    department: Optional[str] = None
    position: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_primary_admin: bool = False

class TenantUserUpdate(BaseModel):
    role: Optional[UserRole] = None
    department: Optional[str] = None
    position: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_primary_admin: Optional[bool] = None

class TenantUserResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    role: str
    permissions: Dict[str, Any]
    department: Optional[str]
    position: Optional[str]
    is_active: bool
    is_primary_admin: bool
    created_at: datetime
    updated_at: Optional[datetime]
    user: UserResponse

class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class UserFilters(BaseModel):
    search: Optional[str] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    has_oab: Optional[bool] = None
