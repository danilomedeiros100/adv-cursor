from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class ProcessNotification(Base):
    """Modelo para notificações de processos - focado na experiência do advogado"""
    __tablename__ = "process_notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Informações da notificação
    notification_type = Column(String(50), nullable=False)  # deadline, andamento, sentença, prazo, audiência, urgente
    priority = Column(String(20), default="normal")  # low, normal, high, critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status da notificação
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Configurações de entrega
    should_email = Column(Boolean, default=True)
    should_push = Column(Boolean, default=True)
    should_sms = Column(Boolean, default=False)
    
    # Dados específicos da notificação
    notification_data = Column(JSON, default=dict)  # Dados adicionais como URLs, IDs, etc.
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    read_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    tenant = relationship("Tenant")
    process = relationship("Process")
    user = relationship("User")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "process_id": str(self.process_id) if self.process_id else None,
            "user_id": str(self.user_id),
            "notification_type": self.notification_type,
            "priority": self.priority,
            "title": self.title,
            "message": self.message,
            "is_read": self.is_read,
            "is_archived": self.is_archived,
            "should_email": self.should_email,
            "should_push": self.should_push,
            "should_sms": self.should_sms,
            "metadata": self.notification_data,
            "created_at": self.created_at.isoformat(),
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None
        }

class NotificationTemplate(Base):
    """Templates de notificações"""
    __tablename__ = "notification_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações básicas
    name = Column(String(255), nullable=False)
    title_template = Column(String(255), nullable=False)
    message_template = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    
    # Configurações
    is_active = Column(Boolean, default=True)
    channels = Column(JSON, default=list)
    variables = Column(JSON, default=list)  # Variáveis disponíveis
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "title_template": self.title_template,
            "message_template": self.message_template,
            "notification_type": self.notification_type,
            "is_active": self.is_active,
            "channels": self.channels,
            "variables": self.variables,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class NotificationPreference(Base):
    """Preferências de notificação por usuário"""
    __tablename__ = "notification_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Preferências por tipo de notificação
    deadline_notifications = Column(Boolean, default=True)
    court_updates = Column(Boolean, default=True)
    hearing_reminders = Column(Boolean, default=True)
    judgment_notifications = Column(Boolean, default=True)
    urgent_processes = Column(Boolean, default=True)
    
    # Preferências de entrega
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    
    # Configurações de timing
    deadline_reminder_days = Column(Integer, default=3)  # Dias antes do prazo
    daily_summary = Column(Boolean, default=True)
    weekly_summary = Column(Boolean, default=True)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relacionamentos
    tenant = relationship("Tenant")
    user = relationship("User")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "user_id": str(self.user_id),
            "deadline_notifications": self.deadline_notifications,
            "court_updates": self.court_updates,
            "hearing_reminders": self.hearing_reminders,
            "judgment_notifications": self.judgment_notifications,
            "urgent_processes": self.urgent_processes,
            "email_enabled": self.email_enabled,
            "push_enabled": self.push_enabled,
            "sms_enabled": self.sms_enabled,
            "deadline_reminder_days": self.deadline_reminder_days,
            "daily_summary": self.daily_summary,
            "weekly_summary": self.weekly_summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
