from sqlalchemy.orm import Session
from sqlalchemy import func
from core.models.client import Client
from core.models.process import Process
from core.models.financial import FinancialRecord
from datetime import datetime, timedelta

class CompanyDashboardService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_company_overview(self, user_id: str):
        """Obtém visão geral da empresa"""
        # Por enquanto retorna dados básicos
        return {
            "total_clients": 0,
            "active_clients": 0,
            "total_processes": 0,
            "active_processes": 0,
            "monthly_revenue": 0.0,
            "new_clients_month": 0,
            "recent_activities": [],
            "upcoming_deadlines": []
        }
    
    async def get_dashboard_stats(self, tenant_id: str):
        """Obtém estatísticas do dashboard da empresa"""
        # Total de clientes
        total_clients = self.db.query(Client).filter(Client.tenant_id == tenant_id).count()
        
        # Clientes ativos
        active_clients = self.db.query(Client).filter(
            Client.tenant_id == tenant_id,
            Client.is_active == True
        ).count()
        
        # Total de processos
        total_processes = self.db.query(Process).filter(Process.tenant_id == tenant_id).count()
        
        # Processos ativos
        active_processes = self.db.query(Process).filter(
            Process.tenant_id == tenant_id,
            Process.status.in_(["active", "pending"])
        ).count()
        
        # Receita do mês
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = self.db.query(func.sum(FinancialRecord.amount)).filter(
            FinancialRecord.tenant_id == tenant_id,
            FinancialRecord.record_type == "income",
            FinancialRecord.paid_date >= current_month
        ).scalar() or 0
        
        # Novos clientes no mês
        new_clients_month = self.db.query(Client).filter(
            Client.tenant_id == tenant_id,
            Client.created_at >= current_month
        ).count()
        
        return {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "total_processes": total_processes,
            "active_processes": active_processes,
            "monthly_revenue": float(monthly_revenue),
            "new_clients_month": new_clients_month
        }
    
    async def get_recent_activities(self, tenant_id: str, limit: int = 10):
        """Obtém atividades recentes"""
        # Por enquanto retorna uma lista vazia
        # TODO: Implementar sistema de auditoria
        return []
    
    async def get_revenue_chart_data(self, tenant_id: str, days: int = 30):
        """Obtém dados de receita para gráfico"""
        # TODO: Implementar sistema real de receita
        # Por enquanto retorna dados vazios
        return {
            "labels": [],
            "data": [],
            "message": "Sistema de receita não implementado"
        }
    
    # Métodos adicionais para as rotas
    async def get_processes_metrics(self, period: str, user_id: str):
        """Métricas de processos"""
        return {
            "total": 0,
            "active": 0,
            "pending": 0,
            "completed": 0,
            "growth_rate": 0.0
        }
    
    async def get_financial_overview(self, period: str, user_id: str):
        """Visão financeira"""
        return {
            "total_revenue": 0.0,
            "total_expenses": 0.0,
            "net_profit": 0.0,
            "pending_payments": 0.0
        }
    
    async def get_team_performance(self, period: str, user_id: str):
        """Performance da equipe"""
        return {
            "total_members": 0,
            "active_members": 0,
            "avg_performance": 0.0
        }
    
    async def get_deadlines_alerts(self, user_id: str):
        """Alertas de prazos"""
        return []
    
    async def get_clients_analytics(self, period: str, user_id: str):
        """Analytics de clientes"""
        return {
            "total": 0,
            "new_this_month": 0,
            "growth_rate": 0.0
        }
    
    async def get_documents_statistics(self, period: str, user_id: str):
        """Estatísticas de documentos"""
        return {
            "total": 0,
            "this_month": 0,
            "pending_review": 0
        }
    
    async def get_tasks_overview(self, user_id: str):
        """Visão geral de tarefas"""
        return {
            "total": 0,
            "pending": 0,
            "completed": 0
        }
    
    async def get_specialties_performance(self, period: str, user_id: str):
        """Performance por especialidade"""
        return []
    
    async def get_upcoming_events(self, days: int, user_id: str):
        """Eventos próximos"""
        return []
    
    async def get_quick_report(self, report_type: str, period: str, user_id: str):
        """Relatórios rápidos"""
        return {
            "type": report_type,
            "period": period,
            "data": []
        }
    
    async def get_notifications_summary(self, user_id: str):
        """Resumo de notificações"""
        return {
            "unread": 0,
            "total": 0,
            "recent": []
        }
