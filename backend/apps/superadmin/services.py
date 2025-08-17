from sqlalchemy.orm import Session
from core.models.tenant import Tenant
from core.models.user import User
from core.models.tenant_user import TenantUser
from apps.superadmin.schemas import TenantCreate, TenantUpdate, UserCreate, TenantUserCreate
from werkzeug.security import generate_password_hash
from fastapi import HTTPException
import uuid

class SuperAdminService:
    def __init__(self, db: Session):
        self.db = db

    async def create_tenant(self, tenant_data: TenantCreate):
        """Cria um novo tenant"""
        # Verificar se o slug já existe
        existing_tenant = self.db.query(Tenant).filter(Tenant.slug == tenant_data.slug).first()
        if existing_tenant:
            raise HTTPException(status_code=400, detail="Slug já existe")
        
        # Verificar se o email já existe
        existing_email = self.db.query(Tenant).filter(Tenant.email == tenant_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email já existe")
        
        # Criar o tenant
        tenant = Tenant(
            id=uuid.uuid4(),
            name=tenant_data.name,
            slug=tenant_data.slug,
            email=tenant_data.email,
            phone=tenant_data.phone,
            plan_type=tenant_data.plan_type,
            max_users=tenant_data.max_users,
            max_processes=tenant_data.max_processes,
            plan_features=self._get_plan_features(tenant_data.plan_type),
            settings={
                "timezone": "America/Sao_Paulo",
                "language": "pt_BR",
                "currency": "BRL"
            },
            branding={
                "logo_url": None,
                "primary_color": "#3B82F6",
                "company_name": tenant_data.name
            }
        )
        
        self.db.add(tenant)
        self.db.flush()
        
        # Criar usuário owner se os dados foram fornecidos
        owner_user = None
        if tenant_data.owner_password:
            # Verificar se o email da empresa já existe como usuário
            existing_owner = self.db.query(User).filter(User.email == tenant_data.email).first()
            if existing_owner:
                raise HTTPException(status_code=400, detail="Email da empresa já está sendo usado por outro usuário")
            
            # Criar usuário owner usando o email da empresa
            owner_user = User(
                id=uuid.uuid4(),
                name=tenant_data.owner_name or f"Admin {tenant_data.name}",
                email=tenant_data.email,  # Usar o email da empresa
                password_hash=generate_password_hash(tenant_data.owner_password),
                phone=tenant_data.owner_phone,
                oab_number=tenant_data.owner_oab_number,
                oab_state=tenant_data.owner_oab_state,
                position=tenant_data.owner_position or "Administrador",
                department=tenant_data.owner_department or "Administrativo",
                is_active=True,
                is_super_admin=False,
                email_verified=True,
                phone_verified=True,
                preferences={
                    "theme": "light",
                    "notifications": {
                        "email": True,
                        "push": True,
                        "sms": False
                    }
                },
                timezone="America/Sao_Paulo",
                language="pt_BR"
            )
            
            self.db.add(owner_user)
            self.db.flush()
            
            # Criar relacionamento tenant-user (owner)
            tenant_user = TenantUser(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                user_id=owner_user.id,
                role="admin",
                permissions={
                    "users.manage": True,
                    "processes.manage": True,
                    "clients.manage": True,
                    "financial.manage": True,
                    "settings.manage": True
                },
                department=tenant_data.owner_department or "Administrativo",
                position=tenant_data.owner_position or "Administrador",
                is_active=True,
                is_primary_admin=True
            )
            
            self.db.add(tenant_user)
        
        self.db.commit()
        self.db.refresh(tenant)
        
        # Converter para dicionário
        tenant_dict = {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "email": tenant.email,
            "phone": tenant.phone,
            "plan_type": tenant.plan_type,
            "plan_features": tenant.plan_features or {},
            "max_users": tenant.max_users,
            "max_processes": tenant.max_processes,
            "is_active": tenant.is_active,
            "is_suspended": tenant.is_suspended,
            "settings": tenant.settings or {},
            "branding": tenant.branding or {},
            "created_at": tenant.created_at,
            "owner_created": owner_user is not None,
            "owner_email": owner_user.email if owner_user else None
        }
        
        return tenant_dict

    def _get_plan_features(self, plan_type: str) -> dict:
        """Retorna as funcionalidades baseadas no tipo de plano"""
        features = {
            "free": {
                "max_users": 5,
                "max_processes": 100,
                "modules": ["clients", "processes"]
            },
            "premium": {
                "max_users": 50,
                "max_processes": 1000,
                "modules": ["clients", "processes", "documents", "financial", "notifications"]
            },
            "enterprise": {
                "max_users": 500,
                "max_processes": 10000,
                "modules": ["clients", "processes", "documents", "financial", "notifications", "analytics", "api"]
            }
        }
        return features.get(plan_type, features["free"])
    

    
    async def list_tenants(self, skip: int = 0, limit: int = 100, search: str = None, status: str = None):
        """Lista tenants com filtros"""
        query = self.db.query(Tenant)
        
        if search:
            query = query.filter(Tenant.name.ilike(f"%{search}%"))
        
        if status:
            if status == "active":
                query = query.filter(Tenant.is_active == True)
            elif status == "suspended":
                query = query.filter(Tenant.is_suspended == True)
        
        tenants = query.offset(skip).limit(limit).all()
        
        # Converter para dicionários para evitar problemas de serialização
        tenant_list = []
        for tenant in tenants:
            tenant_dict = {
                "id": str(tenant.id),
                "name": tenant.name,
                "slug": tenant.slug,
                "email": tenant.email,
                "phone": tenant.phone,
                "plan_type": tenant.plan_type,
                "plan_features": tenant.plan_features or {},
                "max_users": tenant.max_users,
                "max_processes": tenant.max_processes,
                "is_active": tenant.is_active,
                "is_suspended": tenant.is_suspended,
                "settings": tenant.settings or {},
                "branding": tenant.branding or {},
                "created_at": tenant.created_at
            }
            tenant_list.append(tenant_dict)
        
        return tenant_list
    
    async def get_tenant(self, tenant_id: str):
        """Obtém um tenant específico"""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        
        if not tenant:
            return None
        
        # Converter para dicionário
        tenant_dict = {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "email": tenant.email,
            "phone": tenant.phone,
            "plan_type": tenant.plan_type,
            "plan_features": tenant.plan_features or {},
            "max_users": tenant.max_users,
            "max_processes": tenant.max_processes,
            "is_active": tenant.is_active,
            "is_suspended": tenant.is_suspended,
            "settings": tenant.settings or {},
            "branding": tenant.branding or {},
            "created_at": tenant.created_at
        }
        
        return tenant_dict
    
    async def update_tenant(self, tenant_id: str, tenant_data: TenantUpdate):
        """Atualiza um tenant"""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return None
        
        update_data = tenant_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tenant, field, value)
        
        self.db.commit()
        self.db.refresh(tenant)
        
        # Converter para dicionário
        tenant_dict = {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "email": tenant.email,
            "phone": tenant.phone,
            "plan_type": tenant.plan_type,
            "plan_features": tenant.plan_features or {},
            "max_users": tenant.max_users,
            "max_processes": tenant.max_processes,
            "is_active": tenant.is_active,
            "is_suspended": tenant.is_suspended,
            "settings": tenant.settings or {},
            "branding": tenant.branding or {},
            "created_at": tenant.created_at
        }
        
        return tenant_dict
    
    async def deactivate_tenant(self, tenant_id: str):
        """Desativa um tenant"""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return False
        
        tenant.is_active = False
        self.db.commit()
        return True
    
    async def suspend_tenant(self, tenant_id: str, reason: str, admin_id: str):
        """Suspende um tenant"""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return False
        
        tenant.is_suspended = True
        self.db.commit()
        return True
    
    async def activate_tenant(self, tenant_id: str):
        """Reativa um tenant"""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return False
        
        tenant.is_suspended = False
        tenant.is_active = True
        self.db.commit()
        return True
    
    async def create_user(self, user_data: UserCreate):
        """Cria um novo usuário"""
        user = User(
            id=uuid.uuid4(),
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=generate_password_hash(user_data.password),
            oab_number=user_data.oab_number,
            oab_state=user_data.oab_state,
            position=user_data.position,
            department=user_data.department
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def list_users(self, skip: int = 0, limit: int = 100, search: str = None):
        """Lista todos os usuários"""
        query = self.db.query(User)
        
        if search:
            query = query.filter(User.name.ilike(f"%{search}%"))
        
        return query.offset(skip).limit(limit).all()
    
    async def add_user_to_tenant(self, tenant_id: str, user_data: TenantUserCreate):
        """Adiciona um usuário a uma empresa específica"""
        # Verificar se tenant existe
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return False
        
        # Verificar se usuário existe
        user = self.db.query(User).filter(User.id == user_data.user_id).first()
        if not user:
            return False
        
        # Verificar se já existe relação
        existing = self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_data.user_id
        ).first()
        
        if existing:
            return False
        
        # Criar relação
        tenant_user = TenantUser(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_data.user_id,
            role=user_data.role,
            permissions=user_data.permissions,
            is_active=True
        )
        
        self.db.add(tenant_user)
        self.db.commit()
        return True
    
    async def list_tenant_users(self, tenant_id: str, skip: int = 0, limit: int = 100):
        """Lista todos os usuários de uma empresa específica"""
        return self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id
        ).offset(skip).limit(limit).all()
    
    async def get_analytics_overview(self):
        """Obtém visão geral do sistema para analytics"""
        total_tenants = self.db.query(Tenant).count()
        active_tenants = self.db.query(Tenant).filter(Tenant.is_active == True).count()
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "total_users": total_users,
            "active_users": active_users,
            "tenant_activation_rate": (active_tenants / total_tenants * 100) if total_tenants > 0 else 0,
            "user_activation_rate": (active_users / total_users * 100) if total_users > 0 else 0
        }
    
    async def get_tenant_analytics(self, period: str = "30d"):
        """Obtém analytics das empresas"""
        # Implementação similar ao dashboard service
        from datetime import datetime, timedelta
        
        if period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        elif period == "1y":
            days = 365
        else:
            days = 30
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        new_tenants = self.db.query(Tenant).filter(Tenant.created_at >= start_date).count()
        activated_tenants = self.db.query(Tenant).filter(
            Tenant.is_active == True,
            Tenant.created_at >= start_date
        ).count()
        
        return {
            "period": period,
            "new_tenants": new_tenants,
            "activated_tenants": activated_tenants,
            "growth_rate": (new_tenants / days) * 30  # Projeção mensal
        }
    
    async def get_audit_logs(self, tenant_id: str = None, user_id: str = None, 
                           action: str = None, start_date: str = None, 
                           end_date: str = None, skip: int = 0, limit: int = 100):
        """Obtém logs de auditoria"""
        # TODO: Implementar sistema de auditoria real
        # Por enquanto retorna logs vazios
        return {
            "logs": [],
            "total": 0,
            "filters": {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "action": action,
                "start_date": start_date,
                "end_date": end_date
            },
            "message": "Sistema de auditoria não implementado"
        }
