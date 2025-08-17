from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base
import uuid
from sqlalchemy.orm import relationship

class Tenant(Base):
    """Modelo para empresas/tenants do sistema"""
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)  # identificador único
    cnpj = Column(String(18), unique=True, nullable=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(JSON, nullable=True)
    
    # Configurações do plano
    plan_type = Column(String(50), default="free")  # free, premium, enterprise
    plan_features = Column(JSON, default=dict)  # funcionalidades ativas
    max_users = Column(Integer, default=5)
    max_processes = Column(Integer, default=100)
    
    # Status e controle
    is_active = Column(Boolean, default=True)
    is_suspended = Column(Boolean, default=False)
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)  # super admin que criou
    
    # Configurações específicas
    settings = Column(JSON, default=dict)  # configurações customizadas
    branding = Column(JSON, default=dict)  # logo, cores, etc.
    
    # Relacionamentos
    users = relationship("TenantUser", back_populates="tenant")
    specialties = relationship("Specialty", back_populates="tenant")
