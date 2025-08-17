from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class TenantUser(Base):
    """Relacionamento entre usuários e tenants"""
    __tablename__ = "tenant_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Role e permissões
    role = Column(String(50), nullable=False, default="user")  # admin, lawyer, assistant, secretary, receptionist
    permissions = Column(JSON, default=dict)
    
    # Configurações específicas
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_primary_admin = Column(Boolean, default=False)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="users")
    user = relationship("User", back_populates="tenants")
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'user_id', name='unique_tenant_user'),
    )
