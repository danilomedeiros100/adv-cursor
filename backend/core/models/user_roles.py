from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class Role(Base):
    """Modelo para roles/papéis do sistema"""
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)  # admin, lawyer, assistant, secretary, receptionist
    display_name = Column(String(255), nullable=False)  # Nome para exibição
    description = Column(Text, nullable=True)
    
    # Permissões padrão do role
    default_permissions = Column(JSON, default=dict)
    
    # Configurações específicas
    can_manage_users = Column(Boolean, default=False)
    can_manage_financial = Column(Boolean, default=False)
    can_view_all_processes = Column(Boolean, default=False)
    can_manage_specialties = Column(Boolean, default=False)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)

class UserRole(Base):
    """Relacionamento usuário-role com permissões personalizadas"""
    __tablename__ = "user_roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    role_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Permissões personalizadas (sobrescrevem as padrão do role)
    custom_permissions = Column(JSON, default=dict)
    
    # Configurações específicas do usuário
    can_manage_users = Column(Boolean, nullable=True)  # null = usa padrão do role
    can_manage_financial = Column(Boolean, nullable=True)
    can_view_all_processes = Column(Boolean, nullable=True)
    can_manage_specialties = Column(Boolean, nullable=True)
    
    # Módulos específicos que o usuário pode acessar
    allowed_modules = Column(JSON, default=list)  # Lista de módulos permitidos
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )

class LegalSpecialty(Base):
    """Especialidades jurídicas da empresa"""
    __tablename__ = "legal_specialties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(255), nullable=False)  # Direito Civil, Trabalhista, etc.
    code = Column(String(50), nullable=False)  # Código único
    description = Column(Text, nullable=True)
    
    # Configurações
    is_active = Column(Boolean, default=True)
    requires_oab = Column(Boolean, default=True)  # Se requer OAB para atuar
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='unique_tenant_specialty_code'),
    )

class UserSpecialty(Base):
    """Especialidades de cada usuário"""
    __tablename__ = "user_specialties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    specialty_id = Column(UUID(as_uuid=True), ForeignKey("specialties.id"), nullable=False)
    
    # Nível de especialização
    expertise_level = Column(String(50), default="intermediate")  # beginner, intermediate, expert
    years_experience = Column(Integer, nullable=True)
    
    # Certificações
    certifications = Column(JSON, default=list)  # Lista de certificações
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="specialties")
    specialty = relationship("Specialty")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'specialty_id', name='unique_user_specialty'),
    )

# Permissões padrão por role
DEFAULT_ROLE_PERMISSIONS = {
    "admin": {
        "modules": ["*"],  # Todos os módulos
        "permissions": {
            "clients": {"read": True, "create": True, "update": True, "delete": True},
            "processes": {"read": True, "create": True, "update": True, "delete": True},
            "documents": {"read": True, "create": True, "update": True, "delete": True, "sign": True},
            "financial": {"read": True, "create": True, "update": True, "delete": True},
            "reports": {"read": True, "create": True, "export": True},
            "users": {"read": True, "create": True, "update": True, "delete": True},
            "specialties": {"read": True, "create": True, "update": True, "delete": True},
            "settings": {"read": True, "update": True}
        },
        "can_manage_users": True,
        "can_manage_financial": True,
        "can_view_all_processes": True,
        "can_manage_specialties": True
    },
    "lawyer": {
        "modules": ["clients", "processes", "documents", "tasks", "reports"],
        "permissions": {
            "clients": {"read": True, "create": True, "update": True, "delete": False},
            "processes": {"read": True, "create": True, "update": True, "delete": False},
            "documents": {"read": True, "create": True, "update": True, "delete": False, "sign": True},
            "tasks": {"read": True, "create": True, "update": True, "delete": False},
            "reports": {"read": True, "create": False, "export": False}
        },
        "can_manage_users": False,
        "can_manage_financial": False,
        "can_view_all_processes": False,  # Só vê seus processos
        "can_manage_specialties": False
    },
    "assistant": {
        "modules": ["clients", "processes", "documents", "tasks"],
        "permissions": {
            "clients": {"read": True, "create": True, "update": True, "delete": False},
            "processes": {"read": True, "create": False, "update": False, "delete": False},
            "documents": {"read": True, "create": True, "update": False, "delete": False, "sign": False},
            "tasks": {"read": True, "create": True, "update": True, "delete": False}
        },
        "can_manage_users": False,
        "can_manage_financial": False,
        "can_view_all_processes": False,
        "can_manage_specialties": False
    },
    "secretary": {
        "modules": ["clients", "processes", "tasks", "communications"],
        "permissions": {
            "clients": {"read": True, "create": True, "update": True, "delete": False},
            "processes": {"read": True, "create": False, "update": False, "delete": False},
            "tasks": {"read": True, "create": True, "update": True, "delete": False},
            "communications": {"read": True, "create": True, "update": True, "delete": False}
        },
        "can_manage_users": False,
        "can_manage_financial": False,
        "can_view_all_processes": False,
        "can_manage_specialties": False
    },
    "receptionist": {
        "modules": ["clients", "communications"],
        "permissions": {
            "clients": {"read": True, "create": True, "update": False, "delete": False},
            "communications": {"read": True, "create": True, "update": False, "delete": False}
        },
        "can_manage_users": False,
        "can_manage_financial": False,
        "can_view_all_processes": False,
        "can_manage_specialties": False
    }
}
