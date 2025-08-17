from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class AuditLog(Base):
    """Log de auditoria para todas as ações do sistema"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)  # Null para ações do Super Admin
    
    # Informações da ação
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    resource_type = Column(String(100), nullable=False)  # user, process, client, etc.
    resource_id = Column(String(255), nullable=True)  # ID do recurso afetado
    
    # Usuário que executou a ação
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)  # Backup do email
    
    # Detalhes da ação
    details = Column(JSON, default=dict)  # Dados detalhados da ação
    old_values = Column(JSON, nullable=True)  # Valores anteriores (para updates)
    new_values = Column(JSON, nullable=True)  # Novos valores
    
    # Informações do contexto
    ip_address = Column(String(45), nullable=True)  # IPv4 ou IPv6
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    
    # Relacionamento
    user = relationship("User")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "user_id": str(self.user_id) if self.user_id else None,
            "user_email": self.user_email,
            "details": self.details,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat()
        }

class DataAccessLog(Base):
    """Log de acesso a dados sensíveis (LGPD)"""
    __tablename__ = "data_access_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações do acesso
    access_type = Column(String(50), nullable=False)  # view, export, delete
    data_type = Column(String(100), nullable=False)  # personal_data, sensitive_data
    
    # Usuário que acessou
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    
    # Recurso acessado
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    
    # Detalhes
    reason = Column(Text, nullable=True)  # Motivo do acesso
    data_scope = Column(JSON, default=dict)  # Escopo dos dados acessados
    
    # Informações do contexto
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    
    # Relacionamento
    user = relationship("User")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "access_type": self.access_type,
            "data_type": self.data_type,
            "user_id": str(self.user_id) if self.user_id else None,
            "user_email": self.user_email,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "reason": self.reason,
            "data_scope": self.data_scope,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat()
        }

class SecurityEvent(Base):
    """Eventos de segurança do sistema"""
    __tablename__ = "security_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)  # Null para eventos globais
    
    # Informações do evento
    event_type = Column(String(100), nullable=False)  # failed_login, suspicious_activity, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Usuário envolvido
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    
    # Detalhes
    description = Column(Text, nullable=False)
    details = Column(JSON, default=dict)
    
    # Informações do contexto
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    location = Column(JSON, nullable=True)  # Dados de geolocalização
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    
    # Relacionamentos
    user = relationship("User", foreign_keys=[user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "event_type": self.event_type,
            "severity": self.severity,
            "user_id": str(self.user_id) if self.user_id else None,
            "user_email": self.user_email,
            "description": self.description,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "location": self.location,
            "is_resolved": self.is_resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": str(self.resolved_by) if self.resolved_by else None,
            "resolution_notes": self.resolution_notes,
            "created_at": self.created_at.isoformat()
        }
