from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class Specialty(Base):
    """Modelo para especialidades do direito"""
    __tablename__ = "specialties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relacionamento com tenant (empresa)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Informações da especialidade
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    code = Column(String(50), nullable=True)  # Código interno da empresa
    
    # Configurações
    is_active = Column(Boolean, default=True)
    color = Column(String(7), nullable=True)  # Cor para identificação visual (ex: #FF5733)
    icon = Column(String(100), nullable=True)  # Ícone para identificação visual
    
    # Ordem de exibição
    display_order = Column(String(10), default="0")
    
    # Configurações específicas
    requires_oab = Column(Boolean, default=False)  # Se requer OAB para atuar
    min_experience_years = Column(String(10), nullable=True)  # Anos mínimos de experiência
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="specialties")
    
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "description": self.description,
            "code": self.code,
            "is_active": self.is_active,
            "color": self.color,
            "icon": self.icon,
            "display_order": self.display_order,
            "requires_oab": self.requires_oab,
            "min_experience_years": self.min_experience_years,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
