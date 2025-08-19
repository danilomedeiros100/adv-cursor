from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from core.models.process import Process, ProcessDeadline, ProcessTimeline, ProcessLawyer
from core.models.client import Client
from core.models.user import User
from core.models.notification import ProcessNotification
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    """Serviço de dashboard inteligente para advogados"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== DASHBOARD GERAL ====================
    
    async def get_lawyer_dashboard(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Retorna dashboard completo para o advogado"""
        
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Processos urgentes
        urgent_processes = await self._get_urgent_processes(user_id, tenant_id)
        
        # Prazos críticos
        critical_deadlines = await self._get_critical_deadlines(user_id, tenant_id)
        
        # Atualizações recentes
        recent_updates = await self._get_recent_updates(user_id, tenant_id)
        
        # Estatísticas gerais
        stats = await self._get_process_stats(user_id, tenant_id)
        
        # Notificações não lidas
        unread_notifications = await self._get_unread_notifications(user_id, tenant_id)
        
        # Próximas audiências
        upcoming_hearings = await self._get_upcoming_hearings(user_id, tenant_id)
        
        return {
            "urgent_processes": urgent_processes,
            "critical_deadlines": critical_deadlines,
            "recent_updates": recent_updates,
            "stats": stats,
            "unread_notifications": unread_notifications,
            "upcoming_hearings": upcoming_hearings,
            "last_updated": datetime.now().isoformat()
        }
    
    # ==================== PROCESSOS URGENTES ====================
    
    async def _get_urgent_processes(self, user_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Busca processos urgentes do advogado"""
        
        urgent_processes = self.db.query(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id,
                Process.status == "active",
                or_(
                    Process.requires_attention == True,
                    Process.priority.in_(["high", "urgent"])
                )
            )
        ).order_by(desc(Process.updated_at)).limit(10).all()
        
        return [self._format_process_summary(process) for process in urgent_processes]
    
    # ==================== PRAZOS CRÍTICOS ====================
    
    async def _get_critical_deadlines(self, user_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Busca prazos críticos do advogado"""
        
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        
        critical_deadlines = self.db.query(ProcessDeadline).join(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id,
                ProcessDeadline.status == "pending",
                ProcessDeadline.due_date >= today,
                ProcessDeadline.due_date <= next_week
            )
        ).order_by(ProcessDeadline.due_date).limit(10).all()
        
        return [self._format_deadline_summary(deadline) for deadline in critical_deadlines]
    
    # ==================== ATUALIZAÇÕES RECENTES ====================
    
    async def _get_recent_updates(self, user_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Busca atualizações recentes dos processos do advogado"""
        
        week_ago = datetime.now() - timedelta(days=7)
        
        recent_updates = self.db.query(ProcessTimeline).join(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id,
                ProcessTimeline.created_at >= week_ago
            )
        ).order_by(desc(ProcessTimeline.created_at)).limit(15).all()
        
        return [self._format_timeline_summary(update) for update in recent_updates]
    
    # ==================== ESTATÍSTICAS ====================
    
    async def _get_process_stats(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Calcula estatísticas dos processos do advogado"""
        
        # Total de processos ativos
        total_active = self.db.query(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id,
                Process.status == "active"
            )
        ).count()
        
        # Processos urgentes
        urgent_count = self.db.query(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id,
                Process.requires_attention == True,
                Process.status == "active"
            )
        ).count()
        
        # Prazos vencendo hoje
        today = datetime.now().date()
        deadlines_today = self.db.query(ProcessDeadline).join(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id,
                ProcessDeadline.due_date == today,
                ProcessDeadline.status == "pending"
            )
        ).count()
        
        # Prazos vencendo esta semana
        next_week = today + timedelta(days=7)
        deadlines_week = self.db.query(ProcessDeadline).join(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id,
                ProcessDeadline.due_date >= today,
                ProcessDeadline.due_date <= next_week,
                ProcessDeadline.status == "pending"
            )
        ).count()
        
        # Novos andamentos esta semana
        week_ago = datetime.now() - timedelta(days=7)
        new_updates = self.db.query(ProcessTimeline).join(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id,
                ProcessTimeline.created_at >= week_ago
            )
        ).count()
        
        return {
            "total_active_processes": total_active,
            "urgent_processes": urgent_count,
            "deadlines_today": deadlines_today,
            "deadlines_this_week": deadlines_week,
            "new_updates_this_week": new_updates,
            "completion_rate": self._calculate_completion_rate(user_id, tenant_id)
        }
    
    # ==================== NOTIFICAÇÕES ====================
    
    async def _get_unread_notifications(self, user_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Busca notificações não lidas"""
        
        unread_notifications = self.db.query(ProcessNotification).filter(
            and_(
                ProcessNotification.user_id == user_id,
                ProcessNotification.tenant_id == tenant_id,
                ProcessNotification.is_read == False,
                ProcessNotification.is_archived == False
            )
        ).order_by(desc(ProcessNotification.created_at)).limit(10).all()
        
        return [notification.to_dict() for notification in unread_notifications]
    
    # ==================== AUDIÊNCIAS ====================
    
    async def _get_upcoming_hearings(self, user_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Busca próximas audiências"""
        
        today = datetime.now()
        next_month = today + timedelta(days=30)
        
        upcoming_hearings = self.db.query(ProcessTimeline).join(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id,
                ProcessTimeline.type.ilike("%audiência%"),
                ProcessTimeline.date >= today,
                ProcessTimeline.date <= next_month
            )
        ).order_by(ProcessTimeline.date).limit(5).all()
        
        return [self._format_hearing_summary(hearing) for hearing in upcoming_hearings]
    
    # ==================== FUNÇÕES AUXILIARES ====================
    
    def _format_process_summary(self, process: Process) -> Dict[str, Any]:
        """Formata resumo do processo"""
        return {
            "id": str(process.id),
            "cnj_number": process.cnj_number,
            "subject": process.subject,
            "priority": process.priority,
            "requires_attention": process.requires_attention,
            "status": process.status,
            "client_name": process.client.name if process.client else None,
            "last_updated": process.updated_at.isoformat() if process.updated_at else None,
            "deadlines_count": self._count_process_deadlines(process.id),
            "recent_updates_count": self._count_recent_updates(process.id)
        }
    
    def _format_deadline_summary(self, deadline: ProcessDeadline) -> Dict[str, Any]:
        """Formata resumo do prazo"""
        days_until = (deadline.due_date - datetime.now().date()).days
        
        return {
            "id": str(deadline.id),
            "title": deadline.title,
            "description": deadline.description,
            "due_date": deadline.due_date.isoformat(),
            "days_until": days_until,
            "is_critical": days_until <= 1,
            "deadline_type": deadline.deadline_type,
            "process_id": str(deadline.process_id),
            "process_subject": deadline.process.subject,
            "process_cnj": deadline.process.cnj_number
        }
    
    def _format_timeline_summary(self, timeline: ProcessTimeline) -> Dict[str, Any]:
        """Formata resumo do andamento"""
        return {
            "id": str(timeline.id),
            "date": timeline.date.isoformat(),
            "type": timeline.type,
            "description": timeline.description[:100] + "..." if len(timeline.description) > 100 else timeline.description,
            "ai_classification": timeline.ai_classification,
            "process_id": str(timeline.process_id),
            "process_subject": timeline.process.subject,
            "process_cnj": timeline.process.cnj_number
        }
    
    def _format_hearing_summary(self, hearing: ProcessTimeline) -> Dict[str, Any]:
        """Formata resumo da audiência"""
        return {
            "id": str(hearing.id),
            "date": hearing.date.isoformat(),
            "description": hearing.description,
            "process_id": str(hearing.process_id),
            "process_subject": hearing.process.subject,
            "process_cnj": hearing.process.cnj_number,
            "court": hearing.process.court,
            "jurisdiction": hearing.process.jurisdiction
        }
    
    def _count_process_deadlines(self, process_id: str) -> int:
        """Conta prazos pendentes do processo"""
        return self.db.query(ProcessDeadline).filter(
            and_(
                ProcessDeadline.process_id == process_id,
                ProcessDeadline.status == "pending"
            )
        ).count()
    
    def _count_recent_updates(self, process_id: str) -> int:
        """Conta atualizações recentes do processo"""
        week_ago = datetime.now() - timedelta(days=7)
        return self.db.query(ProcessTimeline).filter(
            and_(
                ProcessTimeline.process_id == process_id,
                ProcessTimeline.created_at >= week_ago
            )
        ).count()
    
    def _calculate_completion_rate(self, user_id: str, tenant_id: str) -> float:
        """Calcula taxa de conclusão de prazos"""
        
        # Total de prazos completados
        completed_deadlines = self.db.query(ProcessDeadline).join(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id,
                ProcessDeadline.status == "completed"
            )
        ).count()
        
        # Total de prazos
        total_deadlines = self.db.query(ProcessDeadline).join(Process).join(ProcessLawyer).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessLawyer.lawyer_id == user_id
            )
        ).count()
        
        if total_deadlines == 0:
            return 100.0
        
        return round((completed_deadlines / total_deadlines) * 100, 1)
    
    # ==================== DASHBOARD MOBILE ====================
    
    async def get_mobile_dashboard(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Retorna dashboard otimizado para mobile"""
        
        # Dados essenciais para mobile
        urgent_processes = await self._get_urgent_processes(user_id, tenant_id)
        critical_deadlines = await self._get_critical_deadlines(user_id, tenant_id)
        unread_count = len(await self._get_unread_notifications(user_id, tenant_id))
        
        # Estatísticas simplificadas
        stats = await self._get_process_stats(user_id, tenant_id)
        
        return {
            "urgent_processes_count": len(urgent_processes),
            "critical_deadlines_count": len(critical_deadlines),
            "unread_notifications_count": unread_count,
            "stats": {
                "active_processes": stats["total_active_processes"],
                "deadlines_today": stats["deadlines_today"],
                "completion_rate": stats["completion_rate"]
            },
            "quick_actions": [
                {"id": "view_urgent", "title": "Ver Urgentes", "icon": "alert"},
                {"id": "view_deadlines", "title": "Ver Prazos", "icon": "clock"},
                {"id": "add_process", "title": "Novo Processo", "icon": "plus"},
                {"id": "search", "title": "Buscar", "icon": "search"}
            ]
        }
