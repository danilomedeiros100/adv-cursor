from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from core.database import get_db
from core.auth.superadmin_auth import get_current_superadmin
from apps.superadmin.dashboard.services import SuperAdminDashboardService

router = APIRouter(prefix="/super-admin/dashboard", tags=["Super Admin Dashboard"])

@router.get("/overview")
async def get_saas_overview(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_superadmin)
):
    """Visão geral do SaaS - métricas principais"""
    service = SuperAdminDashboardService(db)
    return await service.get_saas_overview()

@router.get("/tenants/metrics")
async def get_tenants_metrics(
    period: str = "30d",  # 7d, 30d, 90d, 1y
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_superadmin)
):
    """Métricas de tenants (empresas)"""
    service = SuperAdminDashboardService(db)
    return await service.get_tenants_metrics(period)

@router.get("/revenue/analytics")
async def get_revenue_analytics(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_superadmin)
):
    """Analytics de receita do SaaS"""
    service = SuperAdminDashboardService(db)
    return await service.get_revenue_analytics(period)

@router.get("/usage/statistics")
async def get_usage_statistics(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_superadmin)
):
    """Estatísticas de uso do sistema"""
    service = SuperAdminDashboardService(db)
    return await service.get_usage_statistics()

@router.get("/performance/metrics")
async def get_performance_metrics(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_superadmin)
):
    """Métricas de performance do sistema"""
    service = SuperAdminDashboardService(db)
    return await service.get_performance_metrics()

@router.get("/security/alerts")
async def get_security_alerts(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_superadmin)
):
    """Alertas de segurança"""
    service = SuperAdminDashboardService(db)
    return await service.get_security_alerts()

@router.get("/top-tenants")
async def get_top_tenants(
    metric: str = "active_users",  # active_users, processes, revenue
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_superadmin)
):
    """Top tenants por métrica"""
    service = SuperAdminDashboardService(db)
    return await service.get_top_tenants(metric, limit)

@router.get("/system/health")
async def get_system_health(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_superadmin)
):
    """Status de saúde do sistema"""
    service = SuperAdminDashboardService(db)
    return await service.get_system_health()

@router.get("/backup/status")
async def get_backup_status(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_superadmin)
):
    """Status dos backups"""
    service = SuperAdminDashboardService(db)
    return await service.get_backup_status()

@router.get("/compliance/report")
async def get_compliance_report(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_superadmin)
):
    """Relatório de conformidade (LGPD, etc.)"""
    service = SuperAdminDashboardService(db)
    return await service.get_compliance_report()
