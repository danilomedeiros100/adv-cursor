from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class SpecialtyCreate(BaseModel):
    """Schema para criação de especialidade"""
    name: str
    description: Optional[str] = None
    code: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[str] = "0"
    requires_oab: Optional[bool] = False
    min_experience_years: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Nome da especialidade é obrigatório")
        if len(v) > 255:
            raise ValueError("Nome da especialidade deve ter no máximo 255 caracteres")
        return v.strip()
    
    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError("Cor deve estar no formato hexadecimal (#RRGGBB)")
        return v
    
    @validator('code')
    def validate_code(cls, v):
        if v and len(v) > 50:
            raise ValueError("Código deve ter no máximo 50 caracteres")
        return v

class SpecialtyUpdate(BaseModel):
    """Schema para atualização de especialidade"""
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[str] = None
    requires_oab: Optional[bool] = None
    min_experience_years: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Nome da especialidade não pode estar vazio")
            if len(v) > 255:
                raise ValueError("Nome da especialidade deve ter no máximo 255 caracteres")
            return v.strip()
        return v
    
    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError("Cor deve estar no formato hexadecimal (#RRGGBB)")
        return v
    
    @validator('code')
    def validate_code(cls, v):
        if v and len(v) > 50:
            raise ValueError("Código deve ter no máximo 50 caracteres")
        return v

class SpecialtyResponse(BaseModel):
    """Schema para resposta de especialidade"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    code: Optional[str]
    is_active: bool
    color: Optional[str]
    icon: Optional[str]
    display_order: str
    requires_oab: bool
    min_experience_years: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

class SpecialtyListResponse(BaseModel):
    """Schema para resposta de lista de especialidades"""
    specialties: List[SpecialtyResponse]
    total: int
    active_count: int
    inactive_count: int

class SpecialtyStats(BaseModel):
    """Schema para estatísticas de especialidades"""
    total_specialties: int
    active_specialties: int
    inactive_specialties: int
    specialties_with_oab_requirement: int
    specialties_with_experience_requirement: int
