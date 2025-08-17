from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

class TemporaryPermission(Base):
    """Permissões temporárias com expiração automática"""
    __tablename__ = "temporary_permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Permissões temporárias
    granted_permissions = Column(JSON, nullable=False)  # Permissões concedidas
    original_permissions = Column(JSON, nullable=False)  # Permissões originais (backup)
    
    # Configurações
    reason = Column(Text, nullable=False)  # Motivo da permissão temporária
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # Quem concedeu
    granted_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)  # Data de expiração
    
    # Status
    is_active = Column(Boolean, default=True)
    automatically_expired = Column(Boolean, default=False)
    
    # Relacionamentos
    user = relationship("User", foreign_keys=[user_id])
    tenant = relationship("Tenant")
    granter = relationship("User", foreign_keys=[granted_by])

class PermissionOverride(Base):
    """Sobreposições específicas de permissões"""
    __tablename__ = "permission_overrides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    temporary_permission_id = Column(UUID(as_uuid=True), ForeignKey("temporary_permissions.id"), nullable=False)
    
    # Permissão específica
    module = Column(String(100), nullable=False)  # clients, processes, etc.
    action = Column(String(100), nullable=False)  # read, create, update, delete
    granted = Column(Boolean, nullable=False)  # True = permite, False = nega
    
    # Relacionamento
    # temporary_permission = relationship("TemporaryPermission", back_populates="overrides")  # Temporariamente comentado

class TemporaryRoleAssignment(Base):
    """Atribuição temporária de roles"""
    __tablename__ = "temporary_role_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Role temporário
    temporary_role = Column(String(100), nullable=False)  # admin, lawyer, etc.
    original_role = Column(String(100), nullable=False)  # Role original
    
    # Configurações
    reason = Column(Text, nullable=False)
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    granted_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relacionamentos
    user = relationship("User", foreign_keys=[user_id])
    tenant = relationship("Tenant")
    granter = relationship("User", foreign_keys=[granted_by])

class TemporaryPermissionService:
    """Serviço para gerenciar permissões temporárias"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def grant_temporary_permissions(
        self,
        user_id: str,
        tenant_id: str,
        permissions: dict,
        reason: str,
        granted_by: str,
        duration_hours: int = 24
    ) -> TemporaryPermission:
        """Concede permissões temporárias a um usuário"""
        
        # Busca permissões atuais do usuário
        from core.auth.permission_system import PermissionSystem
        permission_system = PermissionSystem(self.db)
        current_permissions = permission_system.get_user_permissions(user_id, tenant_id)
        
        # Calcula data de expiração
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        # Cria permissão temporária
        temp_permission = TemporaryPermission(
            user_id=user_id,
            tenant_id=tenant_id,
            granted_permissions=permissions,
            original_permissions=current_permissions,
            reason=reason,
            granted_by=granted_by,
            expires_at=expires_at
        )
        
        self.db.add(temp_permission)
        self.db.commit()
        self.db.refresh(temp_permission)
        
        return temp_permission
    
    async def grant_temporary_role(
        self,
        user_id: str,
        tenant_id: str,
        temporary_role: str,
        reason: str,
        granted_by: str,
        duration_hours: int = 24
    ) -> TemporaryRoleAssignment:
        """Concede role temporário a um usuário"""
        
        # Busca role atual
        from core.models.tenant import TenantUser
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.user_id == user_id,
            TenantUser.tenant_id == tenant_id
        ).first()
        
        if not tenant_user:
            raise ValueError("Usuário não encontrado no tenant")
        
        # Calcula data de expiração
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        # Cria atribuição temporária
        temp_role = TemporaryRoleAssignment(
            user_id=user_id,
            tenant_id=tenant_id,
            temporary_role=temporary_role,
            original_role=tenant_user.role,
            reason=reason,
            granted_by=granted_by,
            expires_at=expires_at
        )
        
        self.db.add(temp_role)
        self.db.commit()
        self.db.refresh(temp_role)
        
        return temp_role
    
    async def get_active_temporary_permissions(self, user_id: str, tenant_id: str) -> List[TemporaryPermission]:
        """Obtém permissões temporárias ativas de um usuário"""
        return self.db.query(TemporaryPermission).filter(
            TemporaryPermission.user_id == user_id,
            TemporaryPermission.tenant_id == tenant_id,
            TemporaryPermission.is_active == True,
            TemporaryPermission.expires_at > datetime.utcnow()
        ).all()
    
    async def get_active_temporary_roles(self, user_id: str, tenant_id: str) -> List[TemporaryRoleAssignment]:
        """Obtém roles temporários ativos de um usuário"""
        return self.db.query(TemporaryRoleAssignment).filter(
            TemporaryRoleAssignment.user_id == user_id,
            TemporaryRoleAssignment.tenant_id == tenant_id,
            TemporaryRoleAssignment.is_active == True,
            TemporaryRoleAssignment.expires_at > datetime.utcnow()
        ).all()
    
    async def revoke_temporary_permission(self, permission_id: str, revoked_by: str) -> bool:
        """Revoga permissão temporária antes da expiração"""
        permission = self.db.query(TemporaryPermission).filter(
            TemporaryPermission.id == permission_id
        ).first()
        
        if not permission:
            return False
        
        permission.is_active = False
        permission.automatically_expired = True
        
        # Log da revogação
        from core.models.audit import AuditLog
        audit_log = AuditLog(
            tenant_id=permission.tenant_id,
            user_id=revoked_by,
            action="revoke_temporary_permission",
            resource_type="temporary_permission",
            resource_id=str(permission.id),
            details={
                "permission_id": str(permission.id),
                "user_id": str(permission.user_id),
                "reason": "Manually revoked"
            }
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return True
    
    async def cleanup_expired_permissions(self):
        """Remove permissões temporárias expiradas"""
        expired_permissions = self.db.query(TemporaryPermission).filter(
            TemporaryPermission.is_active == True,
            TemporaryPermission.expires_at <= datetime.utcnow()
        ).all()
        
        for permission in expired_permissions:
            permission.is_active = False
            permission.automatically_expired = True
            
            # Log da expiração automática
            from core.models.audit import AuditLog
            audit_log = AuditLog(
                tenant_id=permission.tenant_id,
                user_id=permission.granted_by,
                action="expire_temporary_permission",
                resource_type="temporary_permission",
                resource_id=str(permission.id),
                details={
                    "permission_id": str(permission.id),
                    "user_id": str(permission.user_id),
                    "reason": "Automatically expired"
                }
            )
            
            self.db.add(audit_log)
        
        # Remove roles temporários expirados
        expired_roles = self.db.query(TemporaryRoleAssignment).filter(
            TemporaryRoleAssignment.is_active == True,
            TemporaryRoleAssignment.expires_at <= datetime.utcnow()
        ).all()
        
        for role in expired_roles:
            role.is_active = False
            
            # Log da expiração
            from core.models.audit import AuditLog
            audit_log = AuditLog(
                tenant_id=role.tenant_id,
                user_id=role.granted_by,
                action="expire_temporary_role",
                resource_type="temporary_role",
                resource_id=str(role.id),
                details={
                    "role_id": str(role.id),
                    "user_id": str(role.user_id),
                    "temporary_role": role.temporary_role,
                    "reason": "Automatically expired"
                }
            )
            
            self.db.add(audit_log)
        
        self.db.commit()
    
    async def get_permissions_with_temporary_overrides(self, user_id: str, tenant_id: str) -> dict:
        """Obtém permissões combinando originais + temporárias"""
        from core.auth.permission_system import PermissionSystem
        
        # Permissões base
        permission_system = PermissionSystem(self.db)
        base_permissions = permission_system.get_user_permissions(user_id, tenant_id)
        
        # Permissões temporárias ativas
        temp_permissions = await self.get_active_temporary_permissions(user_id, tenant_id)
        
        # Combina permissões
        final_permissions = base_permissions.copy()
        
        for temp_perm in temp_permissions:
            # Merge das permissões temporárias
            for module, permissions in temp_perm.granted_permissions.items():
                if module not in final_permissions:
                    final_permissions[module] = {}
                
                if isinstance(permissions, dict):
                    final_permissions[module].update(permissions)
                else:
                    final_permissions[module] = permissions
        
        return final_permissions
