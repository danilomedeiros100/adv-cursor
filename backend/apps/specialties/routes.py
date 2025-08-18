from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth.multi_tenant_auth import MultiTenantAuth
from core.auth.permission_system import require_permission
from apps.specialties.schemas import (
    SpecialtyCreate, SpecialtyUpdate, SpecialtyResponse, 
    SpecialtyListResponse, SpecialtyStats
)
from apps.specialties.services import SpecialtyService

router = APIRouter(prefix="/specialties", tags=["specialties"])

# Instância do sistema de autenticação
auth = MultiTenantAuth()

@router.post("/", response_model=SpecialtyResponse)
async def create_specialty(
    specialty_data: SpecialtyCreate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("specialties", "create"))
):
    """Cria uma nova especialidade para a empresa"""
    tenant_id = current_user_data["tenant"].id
    service = SpecialtyService(db)
    
    try:
        specialty = await service.create_specialty(specialty_data, str(tenant_id))
        return specialty.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar especialidade: {str(e)}"
        )

@router.get("/", response_model=List[SpecialtyResponse])
async def list_specialties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    requires_oab: Optional[bool] = Query(None),
    order_by: str = Query("display_order", regex="^(display_order|name|created_at)$"),
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("specialties", "read"))
):
    """Lista especialidades da empresa (isolado automaticamente)"""
    tenant_id = current_user_data["tenant"].id
    service = SpecialtyService(db)
    
    try:
        specialties = await service.list_specialties(
            str(tenant_id),
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            requires_oab=requires_oab,
            order_by=order_by
        )
        
        return [specialty.to_dict() for specialty in specialties]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar especialidades: {str(e)}"
        )

@router.get("/{specialty_id}", response_model=SpecialtyResponse)
async def get_specialty(
    specialty_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("specialties", "read"))
):
    """Obtém uma especialidade específica"""
    tenant_id = current_user_data["tenant"].id
    service = SpecialtyService(db)
    
    specialty = await service.get_specialty(specialty_id, str(tenant_id))
    if not specialty:
        raise HTTPException(status_code=404, detail="Especialidade não encontrada")
    
    return specialty.to_dict()

@router.put("/{specialty_id}", response_model=SpecialtyResponse)
async def update_specialty(
    specialty_id: str,
    specialty_data: SpecialtyUpdate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("specialties", "update"))
):
    """Atualiza uma especialidade"""
    tenant_id = current_user_data["tenant"].id
    service = SpecialtyService(db)
    
    try:
        specialty = await service.update_specialty(specialty_id, specialty_data, str(tenant_id))
        if not specialty:
            raise HTTPException(status_code=404, detail="Especialidade não encontrada")
        
        return specialty.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar especialidade: {str(e)}"
        )

@router.delete("/{specialty_id}")
async def delete_specialty(
    specialty_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("specialties", "delete"))
):
    """Remove uma especialidade (soft delete)"""
    tenant_id = current_user_data["tenant"].id
    service = SpecialtyService(db)
    
    try:
        success = await service.delete_specialty(specialty_id, str(tenant_id))
        if not success:
            raise HTTPException(status_code=404, detail="Especialidade não encontrada")
        
        return {"message": "Especialidade removida com sucesso"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover especialidade: {str(e)}"
        )

@router.post("/{specialty_id}/activate")
async def activate_specialty(
    specialty_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("specialties", "update"))
):
    """Reativa uma especialidade"""
    tenant_id = current_user_data["tenant"].id
    service = SpecialtyService(db)
    
    success = await service.activate_specialty(specialty_id, str(tenant_id))
    if not success:
        raise HTTPException(status_code=404, detail="Especialidade não encontrada")
    
    return {"message": "Especialidade reativada com sucesso"}

@router.get("/stats/summary", response_model=SpecialtyStats)
async def get_specialty_stats(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("specialties", "read"))
):
    """Retorna estatísticas das especialidades"""
    tenant_id = current_user_data["tenant"].id
    service = SpecialtyService(db)
    
    try:
        stats = await service.get_specialty_stats(str(tenant_id))
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )
