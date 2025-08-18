from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth.permission_system import require_permission, require_module_access, get_current_user_permissions
from core.auth.multi_tenant_auth import get_current_user
from apps.processes.schemas import ProcessCreate, ProcessUpdate, ProcessResponse, ProcessLawyerCreate
from apps.processes.services import ProcessService
from core.models.user_roles import UserSpecialty, LegalSpecialty

router = APIRouter(prefix="/processes", tags=["Processos"])

@router.post("/", response_model=ProcessResponse)
async def create_process(
    process_data: ProcessCreate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "create"))
):
    """Cria um novo processo"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    
    # Verifica se especialidade é compatível com advogados (opcional)
    if process_data.specialty_id:
        for lawyer in process_data.lawyers:
            # Verifica se advogado tem a especialidade
            user_specialty = db.query(UserSpecialty).filter(
                UserSpecialty.user_id == lawyer["lawyer_id"],
                UserSpecialty.specialty_id == process_data.specialty_id
            ).first()
            
            if not user_specialty:
                # Por enquanto, apenas loga o aviso
                print(f"Aviso: Advogado {lawyer['lawyer_id']} não possui especialidade compatível")
    
    # Cria o processo
    service = ProcessService(db, tenant_id)
    process = await service.create_process(
        process_data.dict(exclude={"lawyers"}),
        process_data.lawyers,
        user_id
    )
    
    return process

@router.get("/", response_model=List[ProcessResponse])
async def list_processes(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    specialty_id: Optional[str] = None,
    priority: Optional[str] = None,
    client_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Lista processos com filtros"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    user_permissions = await get_current_user_permissions(current_user_data, db)
    
    service = ProcessService(db, tenant_id)
    
    # Se usuário não pode ver todos os processos, filtra apenas os seus
    if not user_permissions.get("can_view_all_processes", False):
        processes = await service.get_user_processes(user_id, "lawyer")
    else:
        processes = await service.list_processes(
            skip=skip,
            limit=limit,
            search=search,
            status=status,
            specialty_id=specialty_id,
            priority=priority,
            client_id=client_id
        )
    
    return processes

@router.get("/{process_id}", response_model=ProcessResponse)
async def get_process(
    process_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Obtém processo específico (verifica se usuário tem acesso)"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    user_permissions = await get_current_user_permissions(current_user_data, db)
    
    service = ProcessService(db, tenant_id)
    
    # Verifica se usuário tem acesso ao processo
    if not user_permissions.get("can_view_all_processes", False):
        user_processes = await service.get_user_processes(user_id, "lawyer")
        process_ids = [p.id for p in user_processes]
        
        if process_id not in process_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem acesso a este processo"
            )
    
    process = await service.get_process(process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    return process

@router.put("/{process_id}", response_model=ProcessResponse)
async def update_process(
    process_id: str,
    process_data: ProcessUpdate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "update"))
):
    """Atualiza um processo"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    user_permissions = await get_current_user_permissions(current_user_data, db)
    
    service = ProcessService(db, tenant_id)
    
    # Verifica se usuário tem acesso ao processo
    if not user_permissions.get("can_view_all_processes", False):
        user_processes = await service.get_user_processes(user_id, "lawyer")
        process_ids = [p.id for p in user_processes]
        
        if process_id not in process_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem acesso a este processo"
            )
    
    process = await service.update_process(process_id, process_data)
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    return process

@router.delete("/{process_id}")
async def delete_process(
    process_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "delete"))
):
    """Deleta um processo (soft delete)"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    user_permissions = await get_current_user_permissions(current_user_data, db)
    
    service = ProcessService(db, tenant_id)
    
    # Verifica se usuário tem acesso ao processo
    if not user_permissions.get("can_view_all_processes", False):
        user_processes = await service.get_user_processes(user_id, "lawyer")
        process_ids = [p.id for p in user_processes]
        
        if process_id not in process_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem acesso a este processo"
            )
    
    success = await service.delete_process(process_id)
    if not success:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    return {"message": "Processo deletado com sucesso"}

@router.get("/stats/summary")
async def get_process_stats(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Obtém estatísticas dos processos"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    user_permissions = await get_current_user_permissions(current_user_data, db)
    
    service = ProcessService(db, tenant_id)
    
    # Se usuário não pode ver todos os processos, filtra apenas os seus
    if not user_permissions.get("can_view_all_processes", False):
        processes = await service.get_user_processes(user_id, "lawyer")
    else:
        processes = await service.list_processes()
    
    total_processes = len(processes)
    active_processes = len([p for p in processes if p.status == "active"])
    closed_processes = len([p for p in processes if p.status == "closed"])
    urgent_processes = len([p for p in processes if p.priority == "urgent"])
    
    completion_rate = (closed_processes / total_processes * 100) if total_processes > 0 else 0
    
    return {
        "total_processes": total_processes,
        "active_processes": active_processes,
        "closed_processes": closed_processes,
        "urgent_processes": urgent_processes,
        "completion_rate": round(completion_rate, 2)
    }

@router.get("/{process_id}/timeline")
async def get_process_timeline(
    process_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Obtém timeline do processo"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    user_permissions = await get_current_user_permissions(current_user_data, db)
    
    service = ProcessService(db, tenant_id)
    
    # Verifica se usuário tem acesso ao processo
    if not user_permissions.get("can_view_all_processes", False):
        user_processes = await service.get_user_processes(user_id, "lawyer")
        process_ids = [p.id for p in user_processes]
        
        if process_id not in process_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem acesso a este processo"
            )
    
    timeline = await service.get_process_timeline(process_id)
    return timeline

@router.get("/{process_id}/deadlines")
async def get_process_deadlines(
    process_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Obtém prazos do processo"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    user_permissions = await get_current_user_permissions(current_user_data, db)
    
    service = ProcessService(db, tenant_id)
    
    # Verifica se usuário tem acesso ao processo
    if not user_permissions.get("can_view_all_processes", False):
        user_processes = await service.get_user_processes(user_id, "lawyer")
        process_ids = [p.id for p in user_processes]
        
        if process_id not in process_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem acesso a este processo"
            )
    
    deadlines = await service.get_process_deadlines(process_id)
    return deadlines

# Incluir rotas CNJ
from .cnj_routes import router as cnj_router
router.include_router(cnj_router)
