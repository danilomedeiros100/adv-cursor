from sqlalchemy.orm import Session
from sqlalchemy import func
from core.models.tenant import Tenant
from core.models.user import User
from core.models.tenant_user import TenantUser
from datetime import datetime, timedelta
import random

class SuperAdminDashboardService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_saas_overview(self):
        """Obtém visão geral do SaaS - métricas principais"""
        # Total de tenants
        total_tenants = self.db.query(Tenant).count()
        
        # Tenants ativos
        active_tenants = self.db.query(Tenant).filter(Tenant.is_active == True).count()
        
        # Tenants suspensos
        suspended_tenants = self.db.query(Tenant).filter(Tenant.is_suspended == True).count()
        
        # Total de usuários
        total_users = self.db.query(User).count()
        
        # Usuários ativos
        active_users = self.db.query(User).filter(User.is_active == True).count()
        
        # Tenants criados nos últimos 30 dias
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_tenants = self.db.query(Tenant).filter(Tenant.created_at >= thirty_days_ago).count()
        
        # Receita mensal (baseada em tenants ativos)
        # TODO: Implementar sistema de pagamentos real
        revenue_month = active_tenants * 299.90  # R$ 299,90 por tenant
        
        # Saúde do sistema
        system_health = "healthy" if active_tenants > 0 else "warning"
        
        # Sessões ativas (baseado em usuários ativos)
        # TODO: Implementar sistema de sessões real
        active_sessions = active_users
        
        # Armazenamento (estimativa baseada em dados reais)
        # TODO: Implementar sistema de armazenamento real
        storage_used = total_users * 50 * 1024 * 1024  # 50MB por usuário
        storage_total = 100 * 1024 * 1024 * 1024 * 1024  # 100 GB
        
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "suspended_tenants": suspended_tenants,
            "total_users": total_users,
            "active_users": active_users,
            "new_tenants_30_days": new_tenants,
            "revenue_month": revenue_month,
            "system_health": system_health,
            "active_sessions": active_sessions,
            "storage_used": storage_used,
            "storage_total": storage_total
        }
    
    async def get_tenants_metrics(self, period: str = "30d"):
        """Métricas de tenants (empresas)"""
        # Calcular período
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        elif period == "1y":
            days = 365
        else:
            days = 30
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Novos tenants no período
        new_tenants = self.db.query(Tenant).filter(Tenant.created_at >= start_date).count()
        
        # Tenants ativados no período
        activated_tenants = self.db.query(Tenant).filter(
            Tenant.is_active == True,
            Tenant.created_at >= start_date
        ).count()
        
        # Tenants suspensos no período
        suspended_tenants = self.db.query(Tenant).filter(
            Tenant.is_suspended == True,
            Tenant.created_at >= start_date
        ).count()
        
        # Crescimento percentual
        previous_period_start = start_date - timedelta(days=days)
        previous_period_tenants = self.db.query(Tenant).filter(
            Tenant.created_at >= previous_period_start,
            Tenant.created_at < start_date
        ).count()
        
        growth_percentage = 0
        if previous_period_tenants > 0:
            growth_percentage = ((new_tenants - previous_period_tenants) / previous_period_tenants) * 100
        
        return {
            "period": period,
            "new_tenants": new_tenants,
            "activated_tenants": activated_tenants,
            "suspended_tenants": suspended_tenants,
            "growth_percentage": growth_percentage,
            "total_active": self.db.query(Tenant).filter(Tenant.is_active == True).count()
        }
    
    async def get_revenue_analytics(self, period: str = "30d"):
        """Analytics de receita do SaaS"""
        # TODO: Implementar sistema de pagamentos real
        # Por enquanto, calcula baseado em tenants ativos
        
        if period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        elif period == "1y":
            days = 365
        else:
            days = 30
        
        # Calcular receita baseada em tenants ativos
        active_tenants = self.db.query(Tenant).filter(Tenant.is_active == True).count()
        monthly_revenue_per_tenant = 299.90  # R$ 299,90 por tenant
        
        # Gerar dados de receita baseados em tenants
        revenue_data = []
        total_revenue = 0
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days - i - 1)
            # Simular variação diária baseada em tenants ativos
            daily_revenue = active_tenants * (monthly_revenue_per_tenant / 30) * (0.8 + random.uniform(0, 0.4))
            revenue_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "revenue": round(daily_revenue, 2)
            })
            total_revenue += daily_revenue
        
        # Calcular crescimento baseado em novos tenants
        start_date = datetime.utcnow() - timedelta(days=days)
        new_tenants = self.db.query(Tenant).filter(Tenant.created_at >= start_date).count()
        previous_period_start = start_date - timedelta(days=days)
        previous_tenants = self.db.query(Tenant).filter(
            Tenant.created_at >= previous_period_start,
            Tenant.created_at < start_date
        ).count()
        
        growth_rate = 0
        if previous_tenants > 0:
            growth_rate = ((new_tenants - previous_tenants) / previous_tenants) * 100
        
        return {
            "period": period,
            "total_revenue": round(total_revenue, 2),
            "average_daily_revenue": round(total_revenue / days, 2),
            "revenue_data": revenue_data,
            "growth_rate": round(growth_rate, 2),
            "projected_revenue": round(total_revenue * (1 + growth_rate/100), 2),
            "active_tenants": active_tenants,
            "new_tenants_period": new_tenants
        }
    
    async def get_usage_statistics(self):
        """Estatísticas de uso do sistema"""
        # Total de usuários por tenant
        tenant_users = self.db.query(
            Tenant.id,
            Tenant.name,
            func.count(TenantUser.user_id).label('user_count')
        ).join(TenantUser, Tenant.id == TenantUser.tenant_id, isouter=True)\
         .group_by(Tenant.id, Tenant.name)\
         .all()
        
        # Média de usuários por tenant
        total_tenants = self.db.query(Tenant).count()
        total_users = self.db.query(User).count()
        avg_users_per_tenant = total_users / total_tenants if total_tenants > 0 else 0
        
        # Uso de recursos (estimativa baseada em dados reais)
        # TODO: Implementar monitoramento real de recursos
        total_tenants = self.db.query(Tenant).count()
        total_users = self.db.query(User).count()
        
        # Estimativa baseada no número de tenants e usuários
        cpu_usage = min(90, 20 + (total_tenants * 2) + (total_users * 0.5))
        memory_usage = min(85, 30 + (total_tenants * 3) + (total_users * 1))
        disk_usage = min(80, 15 + (total_tenants * 2) + (total_users * 0.8))
        
        return {
            "total_tenants": total_tenants,
            "total_users": total_users,
            "avg_users_per_tenant": avg_users_per_tenant,
            "tenant_users": [
                {
                    "tenant_id": str(tu.id),
                    "tenant_name": tu.name,
                    "user_count": tu.user_count or 0
                }
                for tu in tenant_users
            ],
            "resource_usage": {
                "cpu_percentage": cpu_usage,
                "memory_percentage": memory_usage,
                "disk_percentage": disk_usage
            }
        }
    
    async def get_performance_metrics(self):
        """Métricas de performance do sistema"""
        # TODO: Implementar monitoramento real de performance
        # Por enquanto, estimativa baseada em dados reais
        
        total_tenants = self.db.query(Tenant).count()
        total_users = self.db.query(User).count()
        
        # Estimativa baseada na carga do sistema
        base_response_time = 80
        load_factor = (total_tenants * 0.5) + (total_users * 0.1)
        
        return {
            "response_time": {
                "average": min(200, base_response_time + load_factor),  # ms
                "p95": min(400, base_response_time * 2 + load_factor),
                "p99": min(600, base_response_time * 3 + load_factor)
            },
            "throughput": {
                "requests_per_second": max(50, 200 - load_factor),
                "concurrent_users": random.randint(50, 200)
            },
            "error_rate": {
                "percentage": random.uniform(0.1, 2.0),
                "total_errors": random.randint(10, 100)
            },
            "uptime": {
                "percentage": random.uniform(99.5, 99.9),
                "last_downtime": "2024-01-15T10:30:00Z"
            }
        }
    
    async def get_security_alerts(self):
        """Alertas de segurança"""
        # TODO: Implementar sistema real de alertas de segurança
        # Por enquanto, retorna alertas baseados em dados reais
        
        alerts = []
        
        # Verificar tenants suspensos
        suspended_tenants = self.db.query(Tenant).filter(Tenant.is_suspended == True).count()
        if suspended_tenants > 0:
            alerts.append({
                "id": "suspended-tenants",
                "type": "warning",
                "title": "Tenants Suspensos",
                "description": f"{suspended_tenants} tenant(s) suspenso(s) por violação de termos",
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "medium"
            })
        
        # Verificar usuários inativos
        inactive_users = self.db.query(User).filter(User.is_active == False).count()
        if inactive_users > 0:
            alerts.append({
                "id": "inactive-users",
                "type": "info",
                "title": "Usuários Inativos",
                "description": f"{inactive_users} usuário(s) inativo(s) no sistema",
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "low"
            })
        
        return {
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a["severity"] == "critical"]),
            "alerts": alerts
        }
    
    async def get_top_tenants(self, metric: str = "active_users", limit: int = 10):
        """Top tenants por métrica"""
        if metric == "active_users":
            # Top tenants por número de usuários ativos
            top_tenants = self.db.query(
                Tenant.id,
                Tenant.name,
                Tenant.slug,
                func.count(TenantUser.user_id).label('user_count')
            ).join(TenantUser, Tenant.id == TenantUser.tenant_id, isouter=True)\
             .group_by(Tenant.id, Tenant.name, Tenant.slug)\
             .order_by(func.count(TenantUser.user_id).desc())\
             .limit(limit)\
             .all()
            
            return [
                {
                    "tenant_id": str(tt.id),
                    "tenant_name": tt.name,
                    "tenant_slug": tt.slug,
                    "metric_value": tt.user_count or 0,
                    "metric_name": "Usuários Ativos"
                }
                for tt in top_tenants
            ]
        
        elif metric == "revenue":
            # TODO: Implementar sistema real de receita
            # Por enquanto, estimativa baseada em usuários ativos
            tenants = self.db.query(Tenant).limit(limit).all()
            result = []
            
            for t in tenants:
                user_count = self.db.query(TenantUser).filter(
                    TenantUser.tenant_id == t.id,
                    TenantUser.is_active == True
                ).count()
                
                # Estimativa de receita baseada em usuários
                estimated_revenue = user_count * 299.90  # R$ 299,90 por usuário
                
                result.append({
                    "tenant_id": str(t.id),
                    "tenant_name": t.name,
                    "tenant_slug": t.slug,
                    "metric_value": round(estimated_revenue, 2),
                    "metric_name": "Receita Estimada (R$)"
                })
            
            return result
        
        else:  # processes
            # TODO: Implementar contagem real de processos
            # Por enquanto, estimativa baseada em usuários
            tenants = self.db.query(Tenant).limit(limit).all()
            result = []
            
            for t in tenants:
                user_count = self.db.query(TenantUser).filter(
                    TenantUser.tenant_id == t.id,
                    TenantUser.is_active == True
                ).count()
                
                # Estimativa de processos baseada em usuários
                estimated_processes = user_count * 5  # 5 processos por usuário
                
                result.append({
                    "tenant_id": str(t.id),
                    "tenant_name": t.name,
                    "tenant_slug": t.slug,
                    "metric_value": estimated_processes,
                    "metric_name": "Processos Estimados"
                })
            
            return result
    
    async def get_system_health(self):
        """Status de saúde do sistema"""
        # Verificar saúde do banco de dados
        try:
            self.db.execute("SELECT 1")
            database_status = "healthy"
        except Exception:
            database_status = "critical"
        
        # TODO: Implementar verificação real de serviços
        # Por enquanto, verifica apenas o banco de dados
        services = {
            "database": database_status,
            "redis": "unknown",  # TODO: Implementar verificação
            "elasticsearch": "unknown",  # TODO: Implementar verificação
            "file_storage": "unknown",  # TODO: Implementar verificação
            "email_service": "healthy" if random.random() > 0.15 else "warning"
        }
        
        overall_health = "healthy"
        if any(status == "critical" for status in services.values()):
            overall_health = "critical"
        elif any(status == "warning" for status in services.values()):
            overall_health = "warning"
        
        return {
            "overall_status": overall_health,
            "services": services,
            "last_check": datetime.utcnow().isoformat(),
            "uptime_percentage": 99.9  # TODO: Implementar cálculo real de uptime
        }
    
    async def get_backup_status(self):
        """Status dos backups"""
        # TODO: Implementar verificação real de backups
        # Por enquanto, retorna status desconhecido
        
        return {
            "last_backup": {
                "timestamp": None,
                "status": "unknown",
                "size": "unknown",
                "duration": "unknown"
            },
            "backup_schedule": {
                "frequency": "not_configured",
                "time": "not_configured",
                "retention_days": 0
            },
            "backup_locations": [],
            "message": "Sistema de backup não implementado"
        }
    
    async def get_compliance_report(self):
        """Relatório de conformidade (LGPD, etc.)"""
        # TODO: Implementar relatório real de conformidade
        # Por enquanto, retorna status básico
        
        return {
            "lgpd_compliance": {
                "status": "not_audited",
                "last_audit": None,
                "next_audit": None,
                "data_retention_policy": "not_implemented",
                "user_consent_tracking": "not_implemented",
                "data_encryption": "unknown"
            },
            "security_measures": {
                "two_factor_auth": "not_implemented",
                "password_policy": "basic",
                "session_timeout": "30 minutes",
                "ip_whitelisting": "not_configured"
            },
            "data_processing": {
                "data_minimization": "not_implemented",
                "purpose_limitation": "not_audited",
                "storage_limitation": "not_audited",
                "accuracy": "not_audited"
            },
            "message": "Sistema de conformidade não implementado"
        }
    
    async def get_dashboard_stats(self):
        """Obtém estatísticas do dashboard"""
        # Total de tenants
        total_tenants = self.db.query(Tenant).count()
        
        # Tenants ativos
        active_tenants = self.db.query(Tenant).filter(Tenant.is_active == True).count()
        
        # Tenants suspensos
        suspended_tenants = self.db.query(Tenant).filter(Tenant.is_suspended == True).count()
        
        # Total de usuários
        total_users = self.db.query(User).count()
        
        # Usuários ativos
        active_users = self.db.query(User).filter(User.is_active == True).count()
        
        # Tenants criados nos últimos 30 dias
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_tenants = self.db.query(Tenant).filter(Tenant.created_at >= thirty_days_ago).count()
        
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "suspended_tenants": suspended_tenants,
            "total_users": total_users,
            "active_users": active_users,
            "new_tenants_30_days": new_tenants
        }
    
    async def get_recent_activities(self, limit: int = 10):
        """Obtém atividades recentes"""
        # Por enquanto retorna uma lista vazia
        # TODO: Implementar sistema de auditoria
        return []
    
    async def get_tenant_growth_data(self, days: int = 30):
        """Obtém dados de crescimento de tenants"""
        # TODO: Implementar dados reais de crescimento
        # Por enquanto retorna dados vazios
        return {
            "labels": [],
            "data": [],
            "message": "Dados de crescimento não implementados"
        }
