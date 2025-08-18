from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class Process(Base):
    """Modelo para processos jurídicos"""
    __tablename__ = "processes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações básicas
    cnj_number = Column(String(50), nullable=True)  # Número CNJ
    court = Column(String(255), nullable=True)  # Tribunal
    jurisdiction = Column(String(255), nullable=True)  # Comarca
    subject = Column(Text, nullable=False)  # Assunto do processo
    status = Column(String(50), default="active")  # active, closed, suspended
    
    # Relacionamentos
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    
    # Especialidade do processo
    specialty_id = Column(UUID(as_uuid=True), ForeignKey("specialties.id"), nullable=True)
    
    # Informações adicionais
    priority = Column(String(50), default="normal")  # low, normal, high, urgent
    estimated_value = Column(Integer, nullable=True)  # Valor estimado em centavos
    notes = Column(Text, nullable=True)
    
    # Configurações
    is_confidential = Column(Boolean, default=False)
    requires_attention = Column(Boolean, default=False)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamentos
    client = relationship("Client", back_populates="processes")
    specialty = relationship("Specialty")  # Mantido para compatibilidade
    specialties = relationship("ProcessSpecialty", back_populates="process")
    lawyers = relationship("ProcessLawyer", back_populates="process")
    documents = relationship("Document", back_populates="process")
    # tasks = relationship("Task", back_populates="process")  # Temporariamente comentado
    financial_records = relationship("FinancialRecord", back_populates="process")

class ProcessLawyer(Base):
    """Relacionamento processo-advogado"""
    __tablename__ = "process_lawyers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Tipo de participação
    role = Column(String(50), default="lawyer")  # lawyer, assistant, coordinator
    is_primary = Column(Boolean, default=False)  # Advogado principal
    
    # Responsabilidades
    can_sign_documents = Column(Boolean, default=True)
    can_manage_process = Column(Boolean, default=True)
    can_view_financial = Column(Boolean, default=False)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    assigned_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamentos
    process = relationship("Process", back_populates="lawyers")
    lawyer = relationship("User")
    
    # __table_args__ = (
    #     UniqueConstraint('process_id', 'lawyer_id', name='unique_process_lawyer'),
    # )

class ProcessTimeline(Base):
    """Timeline de andamentos do processo"""
    __tablename__ = "process_timeline"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    
    # Informações do andamento
    date = Column(DateTime, nullable=False)
    type = Column(String(100), nullable=False)  # sentença, audiência, petição, etc.
    description = Column(Text, nullable=False)
    court_decision = Column(Text, nullable=True)
    
    # Classificação automática por IA
    ai_classification = Column(String(100), nullable=True)
    ai_confidence = Column(Integer, nullable=True)  # 0-100
    
    # Arquivos relacionados
    documents = Column(JSON, default=list)  # Lista de documentos relacionados
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamento
    process = relationship("Process")

class ProcessDeadline(Base):
    """Prazos críticos do processo"""
    __tablename__ = "process_deadlines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    
    # Informações do prazo
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    deadline_type = Column(String(50), nullable=False)  # legal, internal, client
    
    # Status
    status = Column(String(50), default="pending")  # pending, completed, overdue
    completed_at = Column(DateTime, nullable=True)
    completed_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Notificações
    notify_days_before = Column(Integer, default=3)  # Dias antes para notificar
    is_critical = Column(Boolean, default=False)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamento
    process = relationship("Process")


class ProcessSpecialty(Base):
    """Relacionamento processo-especialidade (muitos para muitos)"""
    __tablename__ = "process_specialties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    specialty_id = Column(UUID(as_uuid=True), ForeignKey("specialties.id"), nullable=False)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamentos
    process = relationship("Process", back_populates="specialties")
    specialty = relationship("Specialty")