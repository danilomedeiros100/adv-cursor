from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form
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

# ==================== TIMELINE ENDPOINTS ====================

@router.get("/{process_id}/timeline")
async def get_process_timeline(
    process_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Obtém timeline de andamentos do processo"""
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
    
    try:
        timeline = await service.get_process_timeline(process_id)
        return timeline
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar timeline: {str(e)}"
        )

@router.post("/{process_id}/timeline")
async def add_timeline_entry(
    process_id: str,
    entry_data: dict,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "update"))
):
    """Adiciona novo andamento ao processo"""
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
    
    try:
        timeline_entry = await service.add_timeline_entry(process_id, entry_data, user_id)
        return timeline_entry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar andamento: {str(e)}"
        )

@router.put("/{process_id}/timeline/{entry_id}")
async def update_timeline_entry(
    process_id: str,
    entry_id: str,
    entry_data: dict,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "update"))
):
    """Atualiza andamento do processo"""
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
    
    try:
        timeline_entry = await service.update_timeline_entry(process_id, entry_id, entry_data, user_id)
        if not timeline_entry:
            raise HTTPException(status_code=404, detail="Andamento não encontrado")
        return timeline_entry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar andamento: {str(e)}"
        )

@router.delete("/{process_id}/timeline/{entry_id}")
async def delete_timeline_entry(
    process_id: str,
    entry_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "delete"))
):
    """Remove andamento do processo"""
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
    
    try:
        success = await service.delete_timeline_entry(process_id, entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Andamento não encontrado")
        return {"message": "Andamento removido com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover andamento: {str(e)}"
        )

# ==================== DEADLINES ENDPOINTS ====================

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
    
    try:
        deadlines = await service.get_process_deadlines(process_id)
        return deadlines
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar prazos: {str(e)}"
        )

@router.post("/{process_id}/deadlines")
async def add_deadline(
    process_id: str,
    deadline_data: dict,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "update"))
):
    """Adiciona novo prazo ao processo"""
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
    
    try:
        deadline = await service.add_deadline(process_id, deadline_data, user_id)
        return deadline
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar prazo: {str(e)}"
        )

@router.put("/{process_id}/deadlines/{deadline_id}/complete")
async def complete_deadline(
    process_id: str,
    deadline_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "update"))
):
    """Marca prazo como concluído"""
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
    
    try:
        success = await service.complete_deadline(process_id, deadline_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Prazo não encontrado")
        return {"message": "Prazo marcado como concluído"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao concluir prazo: {str(e)}"
        )

@router.delete("/{process_id}/deadlines/{deadline_id}")
async def delete_deadline(
    process_id: str,
    deadline_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "delete"))
):
    """Remove prazo do processo"""
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
    
    try:
        success = await service.delete_deadline(process_id, deadline_id)
        if not success:
            raise HTTPException(status_code=404, detail="Prazo não encontrado")
        return {"message": "Prazo removido com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover prazo: {str(e)}"
        )

# ==================== DOCUMENTS ENDPOINTS ====================

@router.get("/{process_id}/documents")
async def get_process_documents(
    process_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Obtém documentos do processo"""
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
    
    try:
        documents = await service.get_process_documents(process_id)
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar documentos: {str(e)}"
        )

@router.post("/{process_id}/documents")
async def upload_document(
    process_id: str,
    file: UploadFile,
    title: str = Form(...),
    description: str = Form(None),
    tags: str = Form("[]"),  # JSON string
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "update"))
):
    """Faz upload de documento para o processo"""
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
    
    try:
        import json
        tags_list = json.loads(tags) if tags else []
        
        document = await service.upload_document(
            process_id, 
            file, 
            title, 
            description, 
            tags_list, 
            user_id
        )
        return document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload: {str(e)}"
        )

@router.delete("/{process_id}/documents/{document_id}")
async def delete_document(
    process_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "delete"))
):
    """Remove documento do processo"""
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
    
    try:
        success = await service.delete_document(process_id, document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        return {"message": "Documento removido com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover documento: {str(e)}"
        )

# ==================== NOTES ENDPOINTS ====================

@router.get("/{process_id}/notes")
async def get_process_notes(
    process_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Obtém anotações do processo"""
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
    
    try:
        notes = await service.get_process_notes(process_id)
        return notes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar anotações: {str(e)}"
        )

@router.post("/{process_id}/notes")
async def add_process_note(
    process_id: str,
    note_data: dict,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "update"))
):
    """Adiciona anotação ao processo"""
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
    
    try:
        note = await service.add_process_note(process_id, note_data, user_id)
        return note
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar anotação: {str(e)}"
        )

@router.delete("/{process_id}/notes/{note_id}")
async def delete_process_note(
    process_id: str,
    note_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "delete"))
):
    """Remove anotação do processo"""
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
    
    try:
        success = await service.delete_process_note(process_id, note_id)
        if not success:
            raise HTTPException(status_code=404, detail="Anotação não encontrada")
        return {"message": "Anotação removida com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover anotação: {str(e)}"
        )

# Incluir rotas CNJ
from .cnj_routes import router as cnj_router
router.include_router(cnj_router)
