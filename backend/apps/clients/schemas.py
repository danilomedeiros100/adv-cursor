from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class ClientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    person_type: str = "PF"  # PF ou PJ
    address: Optional[Dict[str, Any]] = None
    birth_date: Optional[datetime] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    company_role: Optional[str] = None
    is_vip: bool = False
    notes: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Nome é obrigatório")
        if len(v) > 255:
            raise ValueError("Nome deve ter no máximo 255 caracteres")
        return v.strip()

    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError("Email inválido")
        return v

    @validator('person_type')
    def validate_person_type(cls, v):
        if v not in ["PF", "PJ"]:
            raise ValueError("Tipo de pessoa deve ser PF ou PJ")
        return v

    @validator('cpf_cnpj')
    def validate_cpf_cnpj(cls, v):
        if v:
            # Remove caracteres não numéricos
            clean = ''.join(filter(str.isdigit, v))
            if len(clean) not in [11, 14]:  # CPF = 11, CNPJ = 14
                raise ValueError("CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos")
        return v

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    birth_date: Optional[datetime] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    company_role: Optional[str] = None
    is_vip: Optional[bool] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Nome não pode estar vazio")
            if len(v) > 255:
                raise ValueError("Nome deve ter no máximo 255 caracteres")
            return v.strip()
        return v

    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError("Email inválido")
        return v

    @validator('cpf_cnpj')
    def validate_cpf_cnpj(cls, v):
        if v:
            # Remove caracteres não numéricos
            clean = ''.join(filter(str.isdigit, v))
            if len(clean) not in [11, 14]:  # CPF = 11, CNPJ = 14
                raise ValueError("CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos")
        return v

class ClientResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    cpf_cnpj: Optional[str]
    person_type: str
    address: Optional[Dict[str, Any]]
    birth_date: Optional[datetime]
    occupation: Optional[str]
    company_name: Optional[str]
    company_role: Optional[str]
    is_active: bool
    is_vip: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

class ClientListResponse(BaseModel):
    """Schema para resposta de lista de clientes"""
    clients: List[ClientResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class ClientStats(BaseModel):
    """Schema para estatísticas de clientes"""
    total_clients: int
    active_clients: int
    inactive_clients: int
    pf_clients: int
    pj_clients: int
    vip_clients: int
