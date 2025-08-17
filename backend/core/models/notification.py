from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class Notification(Base):
    """Modelo para notificações do sistema"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações básicas
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # deadline, process, financial, system
    
    # Destinatário
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True)
    
    # Relacionamentos
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    
    # Configurações
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    channels = Column(JSON, default=list)  # email, push, sms, whatsapp
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamentos
    user = relationship("User")
    client = relationship("Client")
    process = relationship("Process")
    document = relationship("Document")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "user_id": str(self.user_id) if self.user_id else None,
            "client_id": str(self.client_id) if self.client_id else None,
            "process_id": str(self.process_id) if self.process_id else None,
            "document_id": str(self.document_id) if self.document_id else None,
            "priority": self.priority,
            "channels": self.channels,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "is_sent": self.is_sent,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
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
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Configurações por tipo
    notification_types = Column(JSON, default=dict)  # Configurações por tipo
    
    # Canais preferidos
    preferred_channels = Column(JSON, default=list)
    
    # Configurações gerais
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    whatsapp_notifications = Column(Boolean, default=False)
    
    # Horários
    quiet_hours_start = Column(String(5), nullable=True)  # HH:MM
    quiet_hours_end = Column(String(5), nullable=True)  # HH:MM
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relacionamento
    user = relationship("User")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "tenant_id": str(self.tenant_id),
            "notification_types": self.notification_types,
            "preferred_channels": self.preferred_channels,
            "email_notifications": self.email_notifications,
            "push_notifications": self.push_notifications,
            "sms_notifications": self.sms_notifications,
            "whatsapp_notifications": self.whatsapp_notifications,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
