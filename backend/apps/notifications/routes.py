from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth.multi_tenant_auth import MultiTenantAuth
from apps.notifications.schemas import (
    NotificationResponse, NotificationListResponse, NotificationPreferenceResponse,
    NotificationPreferenceUpdate, NotificationStats, MarkNotificationReadRequest,
    ArchiveNotificationRequest
)
from core.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Instância do sistema de autenticação
auth = MultiTenantAuth()

# ==================== NOTIFICAÇÕES ====================

@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = Query(False, description="Apenas não lidas"),
    page: int = Query(1, ge=1, description="Página"),
    per_page: int = Query(20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Lista notificações do usuário"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("notifications.read", False) or permissions.get("notifications.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para visualizar notificações"
        )
    
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    
    service = NotificationService(db)
    
    try:
        # Buscar notificações
        notifications = await service.get_user_notifications(
            str(user_id), 
            str(tenant_id), 
            unread_only=unread_only,
            limit=per_page
        )
        
        # Calcular estatísticas
        all_notifications = await service.get_user_notifications(str(user_id), str(tenant_id))
        unread_notifications = await service.get_user_notifications(str(user_id), str(tenant_id), unread_only=True)
        
        # Calcular paginação
        total = len(all_notifications)
        total_pages = (total + per_page - 1) // per_page
        
        return NotificationListResponse(
            notifications=[NotificationResponse(**notification.to_dict()) for notification in notifications],
            total=total,
            unread_count=len(unread_notifications),
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar notificações: {str(e)}"
        )

@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Retorna contagem de notificações não lidas"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    
    service = NotificationService(db)
    
    try:
        unread_notifications = await service.get_user_notifications(
            str(user_id), 
            str(tenant_id), 
            unread_only=True
        )
        
        return {"unread_count": len(unread_notifications)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar contagem: {str(e)}"
        )

@router.post("/mark-read")
async def mark_notification_as_read(
    request: MarkNotificationReadRequest,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Marca notificação como lida"""
    user_id = current_user_data["user"].id
    
    service = NotificationService(db)
    
    try:
        success = await service.mark_notification_as_read(request.notification_id, str(user_id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificação não encontrada"
            )
        
        return {"message": "Notificação marcada como lida"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao marcar notificação: {str(e)}"
        )

@router.post("/mark-all-read")
async def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Marca todas as notificações como lidas"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    
    service = NotificationService(db)
    
    try:
        count = await service.mark_all_notifications_as_read(str(user_id), str(tenant_id))
        
        return {"message": f"{count} notificações marcadas como lidas"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao marcar notificações: {str(e)}"
        )

@router.post("/archive")
async def archive_notification(
    request: ArchiveNotificationRequest,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Arquiva notificação"""
    user_id = current_user_data["user"].id
    
    service = NotificationService(db)
    
    try:
        success = await service.archive_notification(request.notification_id, str(user_id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificação não encontrada"
            )
        
        return {"message": "Notificação arquivada"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao arquivar notificação: {str(e)}"
        )

# ==================== PREFERÊNCIAS ====================

@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Busca preferências de notificação do usuário"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    
    service = NotificationService(db)
    
    try:
        preferences = await service.get_user_preferences(str(user_id), str(tenant_id))
        
        if not preferences:
            # Criar preferências padrão
            preferences = await service.create_or_update_preferences(
                str(user_id), 
                str(tenant_id), 
                {}
            )
        
        return NotificationPreferenceResponse(**preferences.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar preferências: {str(e)}"
        )

@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_notification_preferences(
    preferences_data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Atualiza preferências de notificação"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    
    service = NotificationService(db)
    
    try:
        # Filtrar apenas campos não nulos
        update_data = {k: v for k, v in preferences_data.dict().items() if v is not None}
        
        preferences = await service.create_or_update_preferences(
            str(user_id), 
            str(tenant_id), 
            update_data
        )
        
        return NotificationPreferenceResponse(**preferences.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar preferências: {str(e)}"
        )

# ==================== ESTATÍSTICAS ====================

@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Retorna estatísticas de notificações"""
    tenant_id = current_user_data["tenant"].id
    user_id = current_user_data["user"].id
    
    service = NotificationService(db)
    
    try:
        # Buscar todas as notificações
        all_notifications = await service.get_user_notifications(str(user_id), str(tenant_id))
        unread_notifications = await service.get_user_notifications(str(user_id), str(tenant_id), unread_only=True)
        
        # Calcular estatísticas por tipo
        by_type = {}
        by_priority = {}
        
        for notification in all_notifications:
            # Por tipo
            notification_type = notification.notification_type
            by_type[notification_type] = by_type.get(notification_type, 0) + 1
            
            # Por prioridade
            priority = notification.priority
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        # Calcular notificações de hoje e desta semana
        from datetime import datetime, timedelta
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        notifications_today = len([
            n for n in all_notifications 
            if n.created_at.date() == today
        ])
        
        notifications_this_week = len([
            n for n in all_notifications 
            if n.created_at.date() >= week_ago
        ])
        
        return NotificationStats(
            total_notifications=len(all_notifications),
            unread_notifications=len(unread_notifications),
            notifications_today=notifications_today,
            notifications_this_week=notifications_this_week,
            by_type=by_type,
            by_priority=by_priority
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )
