from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth.multi_tenant_auth import MultiTenantAuth
from core.auth.permission_system import require_permission
from apps.clients.schemas import (
    ClientCreate, ClientUpdate, ClientResponse, 
    ClientListResponse, ClientStats
)
from apps.clients.services import ClientService

router = APIRouter(prefix="/clients", tags=["Clientes"])

# Instância do sistema de autenticação
auth = MultiTenantAuth()

@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("clients", "create"))
):
    """Cria um novo cliente (isolado por empresa)"""
    tenant_id = current_user_data["tenant"].id
    service = ClientService(db)
    
    try:
        client = await service.create_client(client_data, str(tenant_id))
        return client.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar cliente: {str(e)}"
        )

@router.get("/", response_model=ClientListResponse)
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    person_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_vip: Optional[bool] = Query(None),
    order_by: str = Query("name", regex="^(name|created_at|person_type)$"),
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("clients", "read"))
):
    """Lista clientes da empresa (isolado automaticamente)"""
    tenant_id = current_user_data["tenant"].id
    service = ClientService(db)
    
    try:
        clients = await service.list_clients(
            str(tenant_id),
            skip=skip,
            limit=limit,
            search=search,
            person_type=person_type,
            is_active=is_active,
            is_vip=is_vip,
            order_by=order_by
        )
        
        # Calcular metadados
        total = await service.get_client_count(str(tenant_id), search, person_type, is_active, is_vip)
        total_pages = (total + limit - 1) // limit
        current_page = (skip // limit) + 1
        
        return ClientListResponse(
            clients=[client.to_dict() for client in clients],
            total=total,
            page=current_page,
            per_page=limit,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar clientes: {str(e)}"
        )

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("clients", "read"))
):
    """Obtém cliente específico (isolado por empresa)"""
    tenant_id = current_user_data["tenant"].id
    service = ClientService(db)
    
    client = await service.get_client(client_id, str(tenant_id))
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return client.to_dict()

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("clients", "update"))
):
    """Atualiza cliente (isolado por empresa)"""
    tenant_id = current_user_data["tenant"].id
    service = ClientService(db)
    
    try:
        client = await service.update_client(client_id, client_data, str(tenant_id))
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        return client.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar cliente: {str(e)}"
        )

@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("clients", "delete"))
):
    """Remove cliente (soft delete, isolado por empresa)"""
    tenant_id = current_user_data["tenant"].id
    service = ClientService(db)
    
    try:
        success = await service.delete_client(client_id, str(tenant_id))
        if not success:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        return {"message": "Cliente removido com sucesso"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar cliente: {str(e)}"
        )

@router.post("/{client_id}/activate")
async def activate_client(
    client_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("clients", "update"))
):
    """Reativa um cliente"""
    tenant_id = current_user_data["tenant"].id
    service = ClientService(db)
    
    success = await service.activate_client(client_id, str(tenant_id))
    if not success:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return {"message": "Cliente reativado com sucesso"}

# ==================== ESTATÍSTICAS ====================

@router.get("/stats/summary", response_model=ClientStats)
async def get_client_stats(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("clients", "read"))
):
    """Retorna estatísticas dos clientes"""
    tenant_id = current_user_data["tenant"].id
    service = ClientService(db)
    
    try:
        stats = await service.get_client_stats(str(tenant_id))
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )
