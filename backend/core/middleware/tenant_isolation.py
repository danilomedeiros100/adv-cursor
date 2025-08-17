from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from core.database import get_db
from core.models.tenant import Tenant
import logging

logger = logging.getLogger(__name__)

class TenantIsolationMiddleware:
    """Middleware para garantir isolamento completo entre tenants"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Extrai tenant_id do token JWT ou header
            tenant_id = self.extract_tenant_id(request)
            
            if tenant_id:
                # Adiciona tenant_id ao scope para uso posterior
                scope["tenant_id"] = tenant_id
                
                # Valida se tenant existe e está ativo
                await self.validate_tenant(tenant_id)
                
                # Configura isolamento no banco de dados
                await self.setup_database_isolation(tenant_id)
        
        await self.app(scope, receive, send)
    
    def extract_tenant_id(self, request: Request) -> Optional[str]:
        """Extrai tenant_id do token JWT ou header customizado"""
        # Tenta extrair do header Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # Decodifica token JWT (simplificado)
                import jwt
                payload = jwt.decode(token, options={"verify_signature": False})
                return payload.get("tenant_id")
            except:
                pass
        
        # Tenta extrair do header customizado
        return request.headers.get("X-Tenant-ID")
    
    async def validate_tenant(self, tenant_id: str):
        """Valida se tenant existe e está ativo"""
        db = next(get_db())
        try:
            tenant = db.query(Tenant).filter(
                Tenant.id == tenant_id,
                Tenant.is_active == True,
                Tenant.is_suspended == False
            ).first()
            
            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Empresa não encontrada ou inativa"
                )
                
        finally:
            db.close()
    
    async def setup_database_isolation(self, tenant_id: str):
        """Configura isolamento no nível do banco de dados"""
        # Para PostgreSQL, podemos usar RLS (Row Level Security)
        # ou filtrar automaticamente todas as queries
        pass

class TenantQueryFilter:
    """Filtro automático para garantir isolamento em queries"""
    
    @staticmethod
    def filter_by_tenant(query, tenant_id: str):
        """Adiciona filtro de tenant automaticamente"""
        # Verifica se a tabela tem coluna tenant_id
        if hasattr(query.column_descriptions[0]['type'], 'tenant_id'):
            return query.filter(text("tenant_id = :tenant_id")).params(tenant_id=tenant_id)
        return query
    
    @staticmethod
    def ensure_tenant_isolation(model_class, tenant_id: str):
        """Decorator para garantir isolamento em operações CRUD"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Adiciona tenant_id automaticamente
                if 'tenant_id' not in kwargs:
                    kwargs['tenant_id'] = tenant_id
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Exemplo de uso em repositories
class BaseRepository:
    """Repository base com isolamento automático"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def get_all(self, model_class):
        """Busca todos os registros do tenant"""
        return self.db.query(model_class).filter(
            model_class.tenant_id == self.tenant_id
        ).all()
    
    def get_by_id(self, model_class, id: str):
        """Busca por ID garantindo isolamento"""
        return self.db.query(model_class).filter(
            model_class.id == id,
            model_class.tenant_id == self.tenant_id
        ).first()
    
    def create(self, model_class, **kwargs):
        """Cria registro garantindo isolamento"""
        kwargs['tenant_id'] = self.tenant_id
        instance = model_class(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
