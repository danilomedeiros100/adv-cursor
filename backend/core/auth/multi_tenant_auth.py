from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from core.database import get_db
from core.models.tenant import Tenant
from core.models.tenant_user import TenantUser
from core.models.user import User
from core.config import settings
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class MultiTenantAuth:
    """Sistema de autenticação multi-tenant com isolamento completo"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Cria token JWT com informações do tenant"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_current_user_with_tenant(
        self, 
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Obtém usuário atual com informações do tenant"""
        payload = self.verify_token(token)
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Busca usuário
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        # Buscar tenant
        tenant = None
        tenant_user = None
        
        if tenant_id:
            # Se tenant_id está especificado no token, validar
            tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant or not tenant.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Empresa inativa ou não encontrada"
                )
            
            # Verifica se usuário pertence ao tenant
            tenant_user = db.query(TenantUser).filter(
                TenantUser.tenant_id == tenant_id,
                TenantUser.user_id == user_id,
                TenantUser.is_active == True
            ).first()
            
            if not tenant_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuário não tem acesso a esta empresa"
                )
        else:
            # Se não há tenant_id no token, buscar o primeiro tenant ativo do usuário
            tenant_user = db.query(TenantUser).filter(
                TenantUser.user_id == user_id,
                TenantUser.is_active == True
            ).first()
            
            if tenant_user:
                tenant = db.query(Tenant).filter(
                    Tenant.id == tenant_user.tenant_id,
                    Tenant.is_active == True
                ).first()
            
            # Se não encontrou tenant, mas é necessário para as APIs da empresa
            if not tenant or not tenant_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuário não tem acesso a nenhuma empresa"
                )
        
        return {
            "user": user,
            "tenant": tenant,
            "tenant_user": tenant_user,
            "permissions": tenant_user.permissions
        }
    
    def require_permission(self, permission: str):
        """Decorator para verificar permissões específicas"""
        def permission_checker(current_user_data: Dict = Depends(self.get_current_user_with_tenant)):
            permissions = current_user_data.get("permissions", {})
            if not permissions.get(permission, False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão '{permission}' necessária"
                )
            return current_user_data
        return permission_checker
    
    def require_role(self, role: str):
        """Decorator para verificar roles específicas"""
        def role_checker(current_user_data: Dict = Depends(self.get_current_user_with_tenant)):
            tenant_user = current_user_data.get("tenant_user")
            if tenant_user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{role}' necessária"
                )
            return current_user_data
        return role_checker

# Instância global
auth = MultiTenantAuth()

# Dependências comuns
get_current_user = auth.get_current_user_with_tenant
require_permission = auth.require_permission
require_admin = auth.require_role("admin")
require_lawyer = auth.require_role("lawyer")
