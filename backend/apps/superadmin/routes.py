from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.models.tenant import Tenant
from core.models.tenant_user import TenantUser
from core.models.user import User
from core.auth.superadmin_auth import require_super_admin
from apps.superadmin.schemas import (
    TenantCreate, TenantUpdate, TenantResponse,
    UserCreate, UserResponse, TenantUserCreate, TenantSuspendRequest
)
from apps.superadmin.services import SuperAdminService
import uuid

router = APIRouter(tags=["Super Admin"])

# ==================== GESTÃO DE EMPRESAS (TENANTS) ====================

@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Cria uma nova empresa/tenant"""
    service = SuperAdminService(db)
    return await service.create_tenant(tenant_data)

@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Lista todas as empresas com filtros"""
    service = SuperAdminService(db)
    return await service.list_tenants(skip=skip, limit=limit, search=search, status=status)

@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Obtém detalhes de uma empresa específica"""
    service = SuperAdminService(db)
    tenant = await service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return tenant

@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Atualiza dados de uma empresa"""
    service = SuperAdminService(db)
    tenant = await service.update_tenant(tenant_id, tenant_data)
    if not tenant:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return tenant

@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Desativa uma empresa (soft delete)"""
    service = SuperAdminService(db)
    success = await service.deactivate_tenant(tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return {"message": "Empresa desativada com sucesso"}

@router.post("/tenants/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: str,
    suspend_data: TenantSuspendRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Suspende uma empresa"""
    service = SuperAdminService(db)
    success = await service.suspend_tenant(tenant_id, suspend_data.reason, current_user["superadmin_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return {"message": "Empresa suspensa com sucesso"}

@router.post("/tenants/{tenant_id}/activate")
async def activate_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Reativa uma empresa suspensa"""
    service = SuperAdminService(db)
    success = await service.activate_tenant(tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return {"message": "Empresa reativada com sucesso"}

# ==================== GESTÃO DE USUÁRIOS ====================

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Cria um novo usuário"""
    service = SuperAdminService(db)
    return await service.create_user(user_data)

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Lista todos os usuários"""
    service = SuperAdminService(db)
    return await service.list_users(skip=skip, limit=limit, search=search)

@router.post("/tenants/{tenant_id}/users")
async def add_user_to_tenant(
    tenant_id: str,
    user_data: TenantUserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Adiciona um usuário a uma empresa específica"""
    service = SuperAdminService(db)
    result = await service.add_user_to_tenant(tenant_id, user_data)
    if not result:
        raise HTTPException(status_code=404, detail="Empresa ou usuário não encontrado")
    return {"message": "Usuário adicionado à empresa com sucesso"}

@router.get("/tenants/{tenant_id}/users")
async def list_tenant_users(
    tenant_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Lista todos os usuários de uma empresa específica"""
    service = SuperAdminService(db)
    return await service.list_tenant_users(tenant_id, skip=skip, limit=limit)

# ==================== RELATÓRIOS E ANALYTICS ====================

@router.get("/analytics/overview")
async def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Obtém visão geral do sistema"""
    service = SuperAdminService(db)
    return await service.get_analytics_overview()

@router.get("/analytics/tenants")
async def get_tenant_analytics(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Obtém analytics das empresas"""
    service = SuperAdminService(db)
    return await service.get_tenant_analytics(period)

@router.get("/logs/audit")
async def get_audit_logs(
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """Obtém logs de auditoria"""
    service = SuperAdminService(db)
    return await service.get_audit_logs(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
