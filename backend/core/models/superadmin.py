from sqlalchemy import Column, String, Boolean, JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class SuperAdmin(Base):
    """Modelo para Super Administrador do SaaS"""
    __tablename__ = "super_admins"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Permissões específicas do Super Admin
    permissions = Column(JSON, default={
        "manage_tenants": True,
        "view_analytics": True,
        "manage_system": True,
        "view_reports": True,
        "manage_backups": True,
        "view_security": True,
        "manage_compliance": True
    })
    
    # Configurações
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Informações adicionais
    phone = Column(String(20))
    notes = Column(Text)
    
    def set_password(self, password: str):
        """Define senha criptografada"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verifica senha"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def update_last_login(self):
        """Atualiza último login"""
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if session:
            self.last_login = func.now()
            session.commit()
