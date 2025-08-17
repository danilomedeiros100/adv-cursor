from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.models.superadmin import SuperAdmin
import jwt
from datetime import datetime, timedelta
import os

security = HTTPBearer()

class SuperAdminAuth:
    """Sistema de autenticação específico para Super Admin"""
    
    def __init__(self):
        self.secret_key = os.getenv("SUPERADMIN_SECRET_KEY", "your-secret-key-here-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 horas
    
    def create_access_token(self, data: dict) -> str:
        """Cria token de acesso para Super Admin"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verifica token de Super Admin"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    
    def authenticate_superadmin(self, email: str, password: str, db: Session) -> SuperAdmin:
        """Autentica Super Admin"""
        superadmin = db.query(SuperAdmin).filter(SuperAdmin.email == email).first()
        if not superadmin:
            return None
        
        if not superadmin.verify_password(password):
            return None
        
        return superadmin

# Instância global
superadmin_auth = SuperAdminAuth()

async def get_current_superadmin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Dependency para obter Super Admin atual"""
    token = credentials.credentials
    payload = superadmin_auth.verify_token(token)
    
    superadmin_id = payload.get("sub")
    if superadmin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    superadmin = db.query(SuperAdmin).filter(SuperAdmin.id == superadmin_id).first()
    if superadmin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Super Admin não encontrado"
        )
    
    if not superadmin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Super Admin inativo"
        )
    
    return {
        "superadmin_id": str(superadmin.id),
        "email": superadmin.email,
        "name": superadmin.name,
        "permissions": superadmin.permissions
    }

async def require_super_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Dependency para verificar se é Super Admin"""
    return await get_current_superadmin(credentials, db)

def require_superadmin_permission(permission: str):
    """Decorator para verificar permissão específica do Super Admin"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Verifica se o usuário tem a permissão necessária
            current_admin = kwargs.get("current_admin")
            if not current_admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Autenticação necessária"
                )
            
            admin_permissions = current_admin.get("permissions", {})
            if permission not in admin_permissions or not admin_permissions[permission]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão '{permission}' necessária"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
