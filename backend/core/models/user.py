from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    """Modelo para usuários do sistema"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Informações básicas
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Informações pessoais
    phone = Column(String(20), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    cpf = Column(String(14), unique=True, nullable=True)
    
    # Informações profissionais
    oab_number = Column(String(20), nullable=True)  # Número OAB
    oab_state = Column(String(2), nullable=True)  # Estado da OAB
    position = Column(String(255), nullable=True)  # Cargo
    department = Column(String(255), nullable=True)  # Departamento
    
    # Configurações
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    
    # Preferências
    preferences = Column(JSON, default=dict)
    timezone = Column(String(50), default="America/Sao_Paulo")
    language = Column(String(10), default="pt-BR")
    
    # Segurança
    last_login = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relacionamentos
    tenants = relationship("TenantUser", back_populates="user")
    specialties = relationship("UserSpecialty", back_populates="user")
    # notifications = relationship("Notification", back_populates="user")
    # notification_preferences = relationship("NotificationPreference", back_populates="user")
    # audit_logs = relationship("AuditLog", back_populates="user")
    # data_access_logs = relationship("DataAccessLog", back_populates="user")
    # security_events = relationship("SecurityEvent", foreign_keys="SecurityEvent.user_id")
    
    def set_password(self, password: str):
        """Define senha criptografada"""
        self.password_hash = generate_password_hash(password)
        self.last_password_change = func.now()
    
    def verify_password(self, password: str) -> bool:
        """Verifica senha"""
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self) -> bool:
        """Verifica se o usuário está bloqueado"""
        if self.locked_until and self.locked_until > func.now():
            return True
        return False
    
    def increment_failed_login(self):
        """Incrementa tentativas de login falhadas"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Bloqueia por 30 minutos
            from datetime import datetime, timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_login(self):
        """Reseta tentativas de login falhadas"""
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "cpf": self.cpf,
            "oab_number": self.oab_number,
            "oab_state": self.oab_state,
            "position": self.position,
            "department": self.department,
            "is_active": self.is_active,
            "is_super_admin": self.is_super_admin,
            "email_verified": self.email_verified,
            "phone_verified": self.phone_verified,
            "preferences": self.preferences,
            "timezone": self.timezone,
            "language": self.language,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class UserProfile(Base):
    """Perfil estendido do usuário"""
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Informações profissionais
    bio = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    education = Column(JSON, default=list)  # Lista de formações
    certifications = Column(JSON, default=list)  # Lista de certificações
    
    # Informações de contato
    address = Column(JSON, nullable=True)
    emergency_contact = Column(JSON, nullable=True)
    
    # Configurações de trabalho
    working_hours = Column(JSON, default=dict)  # Horários de trabalho
    availability = Column(JSON, default=dict)  # Disponibilidade
    
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
            "bio": self.bio,
            "experience_years": self.experience_years,
            "education": self.education,
            "certifications": self.certifications,
            "address": self.address,
            "emergency_contact": self.emergency_contact,
            "working_hours": self.working_hours,
            "availability": self.availability,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
