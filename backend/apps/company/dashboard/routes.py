from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from core.database import get_db
from apps.company.dashboard.services import CompanyDashboardService
from apps.auth.routes import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Company Dashboard"])

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste simples"""
    return {"message": "Dashboard funcionando!", "status": "ok"}

@router.get("/test-no-deps")
async def test_no_deps_endpoint():
    """Endpoint de teste sem dependências"""
    return {"message": "Endpoint sem dependências funcionando!", "status": "ok"}

@router.get("/test-auth-basic")
async def test_auth_basic_endpoint(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste com autenticação básica"""
    return {"message": "Autenticação básica funcionando!"}

@router.get("/test-auth-simple")
async def test_auth_simple_endpoint(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste com autenticação simples"""
    try:
        return {
            "message": "Autenticação funcionando!",
            "user_id": str(current_user["user"].id),
            "user_name": current_user["user"].name
        }
    except Exception as e:
        return {
            "message": "Erro no endpoint",
            "error": str(e),
            "current_user": str(current_user)
        }

@router.get("/test-auth")
async def test_auth_endpoint(current_user: dict = Depends(get_current_user)):
    """Endpoint de teste com autenticação"""
    return {
        "message": "Autenticação funcionando!",
        "user": current_user["user"].name,
        "tenant": current_user["tenant"].name if current_user["tenant"] else None
    }

@router.get("/overview")
async def get_company_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Visão geral da empresa - métricas principais"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_company_overview(user_id)

@router.get("/processes/metrics")
async def get_processes_metrics(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Métricas de processos da empresa"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_processes_metrics(period, user_id)

@router.get("/financial/overview")
async def get_financial_overview(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Visão financeira da empresa"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_financial_overview(period, user_id)

@router.get("/team/performance")
async def get_team_performance(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Performance da equipe"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_team_performance(period, user_id)

@router.get("/deadlines/alerts")
async def get_deadlines_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Alertas de prazos críticos"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_deadlines_alerts(user_id)

@router.get("/clients/analytics")
async def get_clients_analytics(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Analytics de clientes"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_clients_analytics(period, user_id)

@router.get("/documents/statistics")
async def get_documents_statistics(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Estatísticas de documentos"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_documents_statistics(period, user_id)

@router.get("/tasks/overview")
async def get_tasks_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Visão geral de tarefas"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_tasks_overview(user_id)

@router.get("/specialties/performance")
async def get_specialties_performance(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Performance por especialidade"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_specialties_performance(period, user_id)

@router.get("/recent-activities")
async def get_recent_activities(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Atividades recentes da empresa"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_recent_activities(tenant_id, limit)

@router.get("/upcoming-events")
async def get_upcoming_events(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Eventos próximos"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_upcoming_events(days, user_id)

@router.get("/reports/quick")
async def get_quick_reports(
    report_type: str,  # processes, financial, clients, team
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Relatórios rápidos"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_quick_report(report_type, period, user_id)

@router.get("/notifications/summary")
async def get_notifications_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Resumo de notificações"""
    tenant_id = current_user["tenant"].id if current_user["tenant"] else None
    user_id = current_user["user"].id
    service = CompanyDashboardService(db)
    return await service.get_notifications_summary(user_id)
