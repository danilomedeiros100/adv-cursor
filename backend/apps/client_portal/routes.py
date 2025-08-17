from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth.client_auth import get_current_client
from apps.client_portal.schemas import (
    ClientProcessResponse, ClientDocumentResponse, 
    ClientMessageCreate, ClientMessageResponse
)
from apps.client_portal.services import ClientPortalService

router = APIRouter(prefix="/client-portal", tags=["Portal do Cliente"])

@router.get("/processes", response_model=List[ClientProcessResponse])
async def get_client_processes(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Lista processos do cliente (acesso externo)"""
    service = ClientPortalService(db, current_client["client_id"])
    return await service.get_client_processes(skip=skip, limit=limit, status=status)

@router.get("/processes/{process_id}", response_model=ClientProcessResponse)
async def get_client_process(
    process_id: str,
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Obtém detalhes de um processo específico"""
    service = ClientPortalService(db, current_client["client_id"])
    process = await service.get_client_process(process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return process

@router.get("/processes/{process_id}/timeline")
async def get_process_timeline(
    process_id: str,
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Obtém timeline do processo (versão simplificada para cliente)"""
    service = ClientPortalService(db, current_client["client_id"])
    timeline = await service.get_process_timeline(process_id)
    return timeline

@router.get("/processes/{process_id}/documents", response_model=List[ClientDocumentResponse])
async def get_process_documents(
    process_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Lista documentos do processo (apenas documentos compartilhados)"""
    service = ClientPortalService(db, current_client["client_id"])
    return await service.get_process_documents(process_id, skip=skip, limit=limit)

@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Download de documento (com verificação de acesso)"""
    service = ClientPortalService(db, current_client["client_id"])
    document_url = await service.get_document_download_url(document_id)
    if not document_url:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return {"download_url": document_url}

@router.get("/messages")
async def get_messages(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Lista mensagens trocadas com a empresa"""
    service = ClientPortalService(db, current_client["client_id"])
    return await service.get_messages(skip=skip, limit=limit)

@router.post("/messages", response_model=ClientMessageResponse)
async def send_message(
    message_data: ClientMessageCreate,
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Envia mensagem para a empresa"""
    service = ClientPortalService(db, current_client["client_id"])
    return await service.send_message(message_data)

@router.get("/dashboard/summary")
async def get_client_dashboard(
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Dashboard resumido do cliente"""
    service = ClientPortalService(db, current_client["client_id"])
    return await service.get_dashboard_summary()

@router.get("/profile")
async def get_client_profile(
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Obtém perfil do cliente"""
    service = ClientPortalService(db, current_client["client_id"])
    return await service.get_client_profile()

@router.put("/profile")
async def update_client_profile(
    profile_data: dict,
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Atualiza perfil do cliente"""
    service = ClientPortalService(db, current_client["client_id"])
    return await service.update_client_profile(profile_data)

@router.post("/lgpd/export-request")
async def request_data_export(
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Solicita exportação de dados pessoais (LGPD)"""
    service = ClientPortalService(db, current_client["client_id"])
    return await service.request_data_export()

@router.post("/lgpd/forget-request")
async def request_data_deletion(
    db: Session = Depends(get_db),
    current_client: dict = Depends(get_current_client)
):
    """Solicita exclusão de dados pessoais (LGPD)"""
    service = ClientPortalService(db, current_client["client_id"])
    return await service.request_data_deletion()
