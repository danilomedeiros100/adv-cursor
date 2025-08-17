from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from werkzeug.security import check_password_hash as werkzeug_check_password_hash
from core.database import get_db
from core.models.user import User
from core.models.tenant import Tenant
from core.models.superadmin import SuperAdmin
from core.models.tenant_user import TenantUser
from pydantic import BaseModel

router = APIRouter(tags=["autenticação"])

# Configurações de segurança
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Modelos Pydantic
class LoginRequest(BaseModel):
    email: str
    password: str
    tenant_slug: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict
    tenant: Optional[dict] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    oab_number: Optional[str]
    oab_state: Optional[str]
    position: Optional[str]
    department: Optional[str]
    is_active: bool
    is_super_admin: bool
    email_verified: bool
    phone_verified: bool
    preferences: dict
    timezone: str
    language: str
    created_at: datetime

class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    email: str
    phone: Optional[str]
    plan_type: str
    plan_features: dict
    max_users: int
    max_processes: int
    is_active: bool
    is_suspended: bool
    settings: dict
    branding: dict
    created_at: datetime

# Funções de autenticação
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta - suporta bcrypt e Werkzeug"""
    try:
        # Tentar primeiro com bcrypt (passlib)
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        try:
            # Se falhar, tentar com Werkzeug (para compatibilidade com hashes antigos)
            return werkzeug_check_password_hash(hashed_password, plain_password)
        except Exception:
            # Se ambos falharem, senha inválida
            return False

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str, tenant_slug: Optional[str] = None):
    """Autentica usuário"""
    # Primeiro, tentar autenticar como Super Admin
    super_admin = db.query(SuperAdmin).filter(SuperAdmin.email == email).first()
    if super_admin and verify_password(password, super_admin.password_hash):
        return {
            "user": super_admin,
            "tenant": None,
            "is_super_admin": True
        }
    
    # Se não for Super Admin, buscar usuário normal
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    
    # Se usuário especificou tenant, verificar se tem acesso
    if tenant_slug:
        tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
        if not tenant:
            return None
        
        # Verificar se usuário tem acesso ao tenant
        tenant_user = db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant.id,
            TenantUser.user_id == user.id,
            TenantUser.is_active == True
        ).first()
        
        if not tenant_user:
            return None
        
        return {
            "user": user,
            "tenant": tenant,
            "tenant_user": tenant_user,
            "is_super_admin": False
        }
    
    # Se não especificou tenant, buscar o tenant principal do usuário
    # Buscar a primeira associação ativa do usuário
    tenant_user = db.query(TenantUser).filter(
        TenantUser.user_id == user.id,
        TenantUser.is_active == True
    ).first()
    
    if tenant_user:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_user.tenant_id).first()
        return {
            "user": user,
            "tenant": tenant,
            "tenant_user": tenant_user,
            "is_super_admin": False
        }
    
    # Se não tem nenhum tenant associado, retornar sem tenant
    return {
        "user": user,
        "tenant": None,
        "is_super_admin": False
    }

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Obtém usuário atual baseado no token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Verificar se é Super Admin
    super_admin = db.query(SuperAdmin).filter(SuperAdmin.id == user_id).first()
    if super_admin:
        return {
            "user": super_admin,
            "tenant": None,
            "is_super_admin": True
        }
    
    # Verificar se é usuário normal
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Buscar tenant se especificado no token
    tenant_id = payload.get("tenant_id")
    tenant = None
    tenant_user = None
    
    if tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant:
            # Buscar também a associação tenant_user
            tenant_user = db.query(TenantUser).filter(
                TenantUser.tenant_id == tenant_id,
                TenantUser.user_id == user.id,
                TenantUser.is_active == True
            ).first()
    
    return {
        "user": user,
        "tenant": tenant,
        "tenant_user": tenant_user,
        "is_super_admin": False
    }

# Rotas
@router.post("/login", response_model=LoginResponse)
async def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    """Endpoint de login"""
    auth_result = authenticate_user(db, form_data.email, form_data.password, form_data.tenant_slug)
    
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_result["user"]
    tenant = auth_result.get("tenant")
    is_super_admin = auth_result.get("is_super_admin", False)
    
    # Criar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "is_super_admin": is_super_admin
    }
    
    if tenant:
        token_data["tenant_id"] = str(tenant.id)
        token_data["tenant_slug"] = tenant.slug
    
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    # Preparar resposta
    if is_super_admin:
        # Para Super Admin, usar apenas campos disponíveis
        user_data = {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_super_admin": True,
            "permissions": getattr(user, 'permissions', {}),
            "created_at": user.created_at
        }
    else:
        # Para usuários normais, usar todos os campos
        user_data = {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "oab_number": user.oab_number,
            "oab_state": user.oab_state,
            "position": user.position,
            "department": user.department,
            "is_active": user.is_active,
            "is_super_admin": False,
            "email_verified": user.email_verified,
            "phone_verified": user.phone_verified,
            "preferences": user.preferences,
            "timezone": user.timezone,
            "language": user.language,
            "created_at": user.created_at
        }
    
    tenant_data = None
    if tenant:
        # Buscar permissões do usuário no tenant
        tenant_user = None
        if not is_super_admin:
            tenant_user = db.query(TenantUser).filter(
                TenantUser.tenant_id == tenant.id,
                TenantUser.user_id == user.id,
                TenantUser.is_active == True
            ).first()
        
        tenant_data = {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "email": tenant.email,
            "phone": tenant.phone,
            "plan_type": tenant.plan_type,
            "plan_features": tenant.plan_features,
            "max_users": tenant.max_users,
            "max_processes": tenant.max_processes,
            "is_active": tenant.is_active,
            "is_suspended": tenant.is_suspended,
            "settings": tenant.settings,
            "branding": tenant.branding,
            "created_at": tenant.created_at,
            # Incluir permissões do usuário
            "permissions": tenant_user.permissions if tenant_user else {},
            "role": tenant_user.role if tenant_user else None,
            "allowed_modules": list(tenant_user.permissions.keys()) if tenant_user and tenant_user.permissions else []
        }
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_data,
        tenant=tenant_data
    )

@router.post("/superadmin/login", response_model=LoginResponse)
async def superadmin_login(form_data: LoginRequest, db: Session = Depends(get_db)):
    """Endpoint específico para login do Super Admin"""
    # Verificar se é Super Admin
    super_admin = db.query(SuperAdmin).filter(SuperAdmin.email == form_data.email).first()
    if not super_admin or not verify_password(form_data.password, super_admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not super_admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Super Admin account is inactive"
        )
    
    # Criar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_data = {
        "sub": str(super_admin.id),
        "email": super_admin.email,
        "is_super_admin": True
    }
    
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    # Preparar resposta
    user_data = {
        "id": str(super_admin.id),
        "name": super_admin.name,
        "email": super_admin.email,
        "is_active": super_admin.is_active,
        "is_super_admin": True,
        "permissions": super_admin.permissions,
        "created_at": super_admin.created_at
    }
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_data,
        tenant=None
    )

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtém informações do usuário atual"""
    user = current_user["user"]
    tenant = current_user.get("tenant")
    is_super_admin = current_user.get("is_super_admin", False)
    
    user_data = {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "oab_number": user.oab_number,
        "oab_state": user.oab_state,
        "position": user.position,
        "department": user.department,
        "is_active": user.is_active,
        "is_super_admin": is_super_admin,
        "email_verified": user.email_verified,
        "phone_verified": user.phone_verified,
        "preferences": user.preferences,
        "timezone": user.timezone,
        "language": user.language,
        "created_at": user.created_at
    }
    
    tenant_data = None
    if tenant:
        tenant_data = {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "email": tenant.email,
            "phone": tenant.phone,
            "plan_type": tenant.plan_type,
            "plan_features": tenant.plan_features,
            "max_users": tenant.max_users,
            "max_processes": tenant.max_processes,
            "is_active": tenant.is_active,
            "is_suspended": tenant.is_suspended,
            "settings": tenant.settings,
            "branding": tenant.branding,
            "created_at": tenant.created_at
        }
    
    return {
        "user": user_data,
        "tenant": tenant_data,
        "is_super_admin": is_super_admin
    }
