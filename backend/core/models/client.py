from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class Client(Base):
    """Modelo para clientes das empresas"""
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações básicas
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    cpf_cnpj = Column(String(18), nullable=True)  # CPF ou CNPJ
    
    # Tipo de pessoa
    person_type = Column(String(10), nullable=False)  # PF (Pessoa Física) ou PJ (Pessoa Jurídica)
    
    # Endereço
    address = Column(JSON, nullable=True)  # Endereço completo em JSON
    
    # Informações adicionais
    birth_date = Column(DateTime, nullable=True)  # Para PF
    occupation = Column(String(255), nullable=True)  # Profissão
    company_name = Column(String(255), nullable=True)  # Para PJ
    company_role = Column(String(255), nullable=True)  # Cargo na empresa
    
    # Representantes (para PJ)
    representatives = Column(JSON, default=list)  # Lista de representantes
    
    # Status
    is_active = Column(Boolean, default=True)
    is_vip = Column(Boolean, default=False)  # Cliente VIP
    
    # Configurações
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)  # Tags para categorização
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamentos
    processes = relationship("Process", back_populates="client")
    documents = relationship("Document", back_populates="client")
    financial_records = relationship("FinancialRecord", back_populates="client")
    # communications = relationship("Communication", back_populates="client")  # Temporariamente comentado
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "cpf_cnpj": self.cpf_cnpj,
            "person_type": self.person_type,
            "address": self.address,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "occupation": self.occupation,
            "company_name": self.company_name,
            "company_role": self.company_role,
            "representatives": self.representatives,
            "is_active": self.is_active,
            "is_vip": self.is_vip,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
