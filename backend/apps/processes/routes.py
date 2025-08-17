from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth.permission_system import require_permission, require_module_access, get_current_user_permissions
from core.auth.multi_tenant_auth import get_current_user
from apps.processes.schemas import ProcessCreate, ProcessUpdate, ProcessResponse, ProcessLawyerCreate
from apps.processes.services import ProcessService
from core.models.process import ProcessService as ProcessModelService
from core.models.user_roles import UserSpecialty, LegalSpecialty

router = APIRouter(prefix="/processes", tags=["Processos"])

@router.post("/", response_model=ProcessResponse)
async def create_process(
    process_data: ProcessCreate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "create"))
):
    """Cria um novo processo (verifica especialidades dos advogados)"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    
    # Verifica se especialidade é compatível com advogados
    if process_data.specialty_id:
        for lawyer in process_data.lawyers:
            # Verifica se advogado tem a especialidade
            user_specialty = db.query(UserSpecialty).filter(
                UserSpecialty.user_id == lawyer.lawyer_id,
                UserSpecialty.specialty_id == process_data.specialty_id
            ).first()
            
            if not user_specialty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Advogado {lawyer.lawyer_id} não possui especialidade compatível"
                )
    
    # Cria o processo
    service = ProcessModelService(db, tenant_id)
    process = await service.create_process(
        process_data.dict(exclude={"lawyers"}),
        [lawyer.dict() for lawyer in process_data.lawyers],
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
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Lista processos (filtra por permissões do usuário)"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    user_permissions = await get_current_user_permissions(current_user_data, db)
    
    service = ProcessModelService(db, tenant_id)
    
    # Se não é admin, filtra apenas processos do usuário
    if not user_permissions.get("can_view_all_processes", False):
        processes = await service.get_user_processes(user_id, "lawyer")
    else:
        # Admin vê todos os processos
        processes = await service.get_all_processes(skip, limit, search, status, specialty_id)
    
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
    
    service = ProcessModelService(db, tenant_id)
    
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
    """Atualiza processo (verifica permissões)"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    user_permissions = await get_current_user_permissions(current_user_data, db)
    
    service = ProcessModelService(db, tenant_id)
    
    # Verifica se usuário tem acesso ao processo
    if not user_permissions.get("can_view_all_processes", False):
        user_processes = await service.get_user_processes(user_id, "lawyer")
        process_ids = [p.id for p in user_processes]
        
        if process_id not in process_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem acesso a este processo"
            )
    
    process = await service.update_process(process_id, process_data.dict())
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    return process

@router.post("/{process_id}/lawyers")
async def add_lawyer_to_process(
    process_id: str,
    lawyer_data: ProcessLawyerCreate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "update"))
):
    """Adiciona advogado ao processo (verifica especialidade)"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    
    service = ProcessModelService(db, tenant_id)
    
    # Verifica se advogado tem especialidade compatível
    process = await service.get_process(process_id)
    if process.specialty_id:
        user_specialty = db.query(UserSpecialty).filter(
            UserSpecialty.user_id == lawyer_data.lawyer_id,
            UserSpecialty.specialty_id == process.specialty_id
        ).first()
        
        if not user_specialty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Advogado não possui especialidade compatível com o processo"
            )
    
    result = await service.add_lawyer_to_process(
        process_id,
        lawyer_data.lawyer_id,
        lawyer_data.role,
        user_id
    )
    
    return {"message": "Advogado adicionado com sucesso", "process_lawyer_id": result.id}

@router.get("/{process_id}/lawyers")
async def get_process_lawyers(
    process_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Lista advogados do processo"""
    tenant_id = current_user_data["tenant"].id
    service = ProcessModelService(db, tenant_id)
    
    lawyers = await service.get_process_lawyers(process_id)
    return lawyers

@router.get("/specialties/compatible-lawyers")
async def get_compatible_lawyers(
    specialty_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "create"))
):
    """Lista advogados compatíveis com uma especialidade"""
    tenant_id = current_user_data["tenant"].id
    
    # Busca advogados com a especialidade
    user_specialties = db.query(UserSpecialty).filter(
        UserSpecialty.specialty_id == specialty_id
    ).all()
    
    # Busca informações dos usuários
    from core.models.user import User
    from core.models.tenant import TenantUser
    
    lawyer_ids = [us.user_id for us in user_specialties]
    lawyers = db.query(User, TenantUser).join(TenantUser).filter(
        User.id.in_(lawyer_ids),
        TenantUser.tenant_id == tenant_id,
        TenantUser.is_active == True
    ).all()
    
    return [
        {
            "user_id": lawyer.User.id,
            "name": lawyer.User.name,
            "email": lawyer.User.email,
            "role": lawyer.TenantUser.role,
            "expertise_level": next(us.expertise_level for us in user_specialties if us.user_id == lawyer.User.id)
        }
        for lawyer in lawyers
    ]

@router.get("/specialties/available")
async def get_available_specialties(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_module_access("processes"))
):
    """Lista especialidades disponíveis na empresa"""
    tenant_id = current_user_data["tenant"].id
    
    specialties = db.query(LegalSpecialty).filter(
        LegalSpecialty.tenant_id == tenant_id,
        LegalSpecialty.is_active == True
    ).all()
    
    return specialties

# ==================== TIMELINE E PRAZOS ====================

@router.get("/{process_id}/timeline")
async def get_process_timeline(
    process_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Obtém timeline do processo"""
    tenant_id = current_user_data["tenant"].id
    service = ProcessModelService(db, tenant_id)
    
    # Verifica acesso ao processo
    user_permissions = await get_current_user_permissions(current_user_data, db)
    if not user_permissions.get("can_view_all_processes", False):
        user_processes = await service.get_user_processes(current_user_data["user"].id, "lawyer")
        process_ids = [p.id for p in user_processes]
        
        if process_id not in process_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem acesso a este processo"
            )
    
    from core.models.process import ProcessTimeline
    timeline = db.query(ProcessTimeline).filter(
        ProcessTimeline.process_id == process_id
    ).order_by(ProcessTimeline.date.desc()).all()
    
    return timeline

@router.get("/{process_id}/deadlines")
async def get_process_deadlines(
    process_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Obtém prazos do processo"""
    tenant_id = current_user_data["tenant"].id
    service = ProcessModelService(db, tenant_id)
    
    # Verifica acesso ao processo
    user_permissions = await get_current_user_permissions(current_user_data, db)
    if not user_permissions.get("can_view_all_processes", False):
        user_processes = await service.get_user_processes(current_user_data["user"].id, "lawyer")
        process_ids = [p.id for p in user_processes]
        
        if process_id not in process_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem acesso a este processo"
            )
    
    from core.models.process import ProcessDeadline
    deadlines = db.query(ProcessDeadline).filter(
        ProcessDeadline.process_id == process_id
    ).order_by(ProcessDeadline.due_date).all()
    
    return deadlines

# ==================== RELATÓRIOS ====================

@router.get("/reports/summary")
async def get_processes_summary(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("reports", "read"))
):
    """Relatório resumo de processos"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    user_permissions = await get_current_user_permissions(current_user_data, db)
    
    service = ProcessModelService(db, tenant_id)
    
    # Filtra por permissões
    if not user_permissions.get("can_view_all_processes", False):
        processes = await service.get_user_processes(user_id, "lawyer")
    else:
        processes = await service.get_all_processes()
    
    # Estatísticas
    total_processes = len(processes)
    active_processes = len([p for p in processes if p.status == "active"])
    closed_processes = len([p for p in processes if p.status == "closed"])
    urgent_processes = len([p for p in processes if p.priority == "urgent"])
    
    return {
        "total_processes": total_processes,
        "active_processes": active_processes,
        "closed_processes": closed_processes,
        "urgent_processes": urgent_processes,
        "completion_rate": (closed_processes / total_processes * 100) if total_processes > 0 else 0
    }
