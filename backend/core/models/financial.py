from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class FinancialRecord(Base):
    """Modelo para registros financeiros"""
    __tablename__ = "financial_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações básicas
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)  # Valor em centavos
    currency = Column(String(3), default="BRL")
    
    # Tipo de registro
    record_type = Column(String(50), nullable=False)  # income, expense, fee, cost
    category = Column(String(100), nullable=True)  # Categoria financeira
    
    # Relacionamentos
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Datas
    due_date = Column(DateTime, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, paid, overdue, cancelled
    
    # Configurações
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(50), nullable=True)  # monthly, quarterly, yearly
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamentos
    process = relationship("Process", back_populates="financial_records")
    client = relationship("Client", back_populates="financial_records")
    lawyer = relationship("User")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "title": self.title,
            "description": self.description,
            "amount": float(self.amount),
            "currency": self.currency,
            "record_type": self.record_type,
            "category": self.category,
            "process_id": str(self.process_id) if self.process_id else None,
            "client_id": str(self.client_id) if self.client_id else None,
            "lawyer_id": str(self.lawyer_id) if self.lawyer_id else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "paid_date": self.paid_date.isoformat() if self.paid_date else None,
            "status": self.status,
            "is_recurring": self.is_recurring,
            "recurring_frequency": self.recurring_frequency,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class FeeStructure(Base):
    """Estrutura de honorários por especialidade"""
    __tablename__ = "fee_structures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações básicas
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    specialty_id = Column(UUID(as_uuid=True), ForeignKey("legal_specialties.id"), nullable=True)
    
    # Estrutura de preços
    base_fee = Column(Numeric(10, 2), nullable=False)  # Honorário base
    hourly_rate = Column(Numeric(10, 2), nullable=True)  # Taxa por hora
    success_fee_percentage = Column(Numeric(5, 2), nullable=True)  # Percentual de sucesso
    
    # Configurações
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Estrutura padrão
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamento
    specialty = relationship("LegalSpecialty")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "description": self.description,
            "specialty_id": str(self.specialty_id) if self.specialty_id else None,
            "base_fee": float(self.base_fee),
            "hourly_rate": float(self.hourly_rate) if self.hourly_rate else None,
            "success_fee_percentage": float(self.success_fee_percentage) if self.success_fee_percentage else None,
            "is_active": self.is_active,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class PaymentMethod(Base):
    """Métodos de pagamento"""
    __tablename__ = "payment_methods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações básicas
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # pix, boleto, credit_card, bank_transfer
    provider = Column(String(100), nullable=True)  # Asaas, Iugu, etc.
    
    # Configurações
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    settings = Column(JSON, default=dict)  # Configurações específicas
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "type": self.type,
            "provider": self.provider,
            "is_active": self.is_active,
            "is_default": self.is_default,
            "settings": self.settings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
