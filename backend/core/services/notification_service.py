from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from core.models.notification import ProcessNotification, NotificationPreference
from core.models.process import Process, ProcessDeadline, ProcessTimeline
from core.models.user import User
import uuid
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Serviço inteligente de notificações para advogados"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== NOTIFICAÇÕES DE PRAZOS ====================
    
    async def create_deadline_notification(self, deadline: ProcessDeadline, user_id: str) -> ProcessNotification:
        """Cria notificação de prazo"""
        days_until_deadline = (deadline.due_date - datetime.now()).days
        
        if days_until_deadline <= 0:
            priority = "critical"
            title = f"⚠️ PRAZO VENCIDO: {deadline.title}"
            message = f"O prazo '{deadline.title}' do processo venceu hoje!"
        elif days_until_deadline == 1:
            priority = "high"
            title = f"🚨 PRAZO AMANHÃ: {deadline.title}"
            message = f"O prazo '{deadline.title}' vence amanhã!"
        elif days_until_deadline <= 3:
            priority = "high"
            title = f"⏰ PRAZO PRÓXIMO: {deadline.title}"
            message = f"O prazo '{deadline.title}' vence em {days_until_deadline} dias"
        else:
            priority = "normal"
            title = f"📅 PRAZO: {deadline.title}"
            message = f"Lembrete: prazo '{deadline.title}' vence em {days_until_deadline} dias"
        
        notification = ProcessNotification(
            id=uuid.uuid4(),
            tenant_id=deadline.process.tenant_id,
            process_id=deadline.process_id,
            user_id=user_id,
            notification_type="deadline",
            priority=priority,
            title=title,
            message=message,
            notification_data={
                "deadline_id": str(deadline.id),
                "due_date": deadline.due_date.isoformat(),
                "days_until": days_until_deadline,
                "deadline_type": deadline.deadline_type
            }
        )
        
        self.db.add(notification)
        self.db.commit()
        return notification
    
    # ==================== NOTIFICAÇÕES DE ANDAMENTOS ====================
    
    async def create_court_update_notification(self, timeline_entry: ProcessTimeline, user_id: str) -> ProcessNotification:
        """Cria notificação de atualização do tribunal"""
        
        # Classificar tipo de andamento
        if "sentença" in timeline_entry.type.lower() or "julgamento" in timeline_entry.type.lower():
            notification_type = "sentença"
            priority = "high"
            emoji = "⚖️"
            title = f"⚖️ SENTENÇA: {timeline_entry.process.subject}"
        elif "audiência" in timeline_entry.type.lower():
            notification_type = "audiência"
            priority = "high"
            emoji = "🏛️"
            title = f"🏛️ AUDIÊNCIA: {timeline_entry.process.subject}"
        elif "prazo" in timeline_entry.type.lower():
            notification_type = "prazo"
            priority = "normal"
            emoji = "⏰"
            title = f"⏰ PRAZO: {timeline_entry.process.subject}"
        else:
            notification_type = "andamento"
            priority = "normal"
            emoji = "📋"
            title = f"📋 ANDAMENTO: {timeline_entry.process.subject}"
        
        message = f"{emoji} {timeline_entry.description[:100]}..."
        
        notification = ProcessNotification(
            id=uuid.uuid4(),
            tenant_id=timeline_entry.process.tenant_id,
            process_id=timeline_entry.process_id,
            user_id=user_id,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            notification_data={
                "timeline_id": str(timeline_entry.id),
                "andamento_type": timeline_entry.type,
                "court_decision": timeline_entry.court_decision
            }
        )
        
        self.db.add(notification)
        self.db.commit()
        return notification
    
    # ==================== NOTIFICAÇÕES DE PROCESSOS URGENTES ====================
    
    async def create_urgent_process_notification(self, process: Process, user_id: str) -> ProcessNotification:
        """Cria notificação de processo urgente"""
        
        notification = ProcessNotification(
            id=uuid.uuid4(),
            tenant_id=process.tenant_id,
            process_id=process.id,
            user_id=user_id,
            notification_type="urgente",
            priority="critical",
            title=f"🚨 PROCESSO URGENTE: {process.subject}",
            message=f"O processo {process.cnj_number} foi marcado como urgente e requer atenção imediata!",
            notification_data={
                "process_number": process.cnj_number,
                "priority": process.priority,
                "requires_attention": process.requires_attention
            }
        )
        
        self.db.add(notification)
        self.db.commit()
        return notification
    
    # ==================== NOTIFICAÇÕES DE RESUMO ====================
    
    async def create_daily_summary_notification(self, user_id: str, tenant_id: str) -> ProcessNotification:
        """Cria notificação de resumo diário"""
        
        # Buscar estatísticas do dia
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Prazos vencendo hoje
        deadlines_today = self.db.query(ProcessDeadline).join(Process).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessDeadline.due_date >= today,
                ProcessDeadline.due_date < tomorrow,
                ProcessDeadline.status == "pending"
            )
        ).count()
        
        # Novos andamentos
        new_updates = self.db.query(ProcessTimeline).join(Process).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessTimeline.created_at >= today,
                ProcessTimeline.created_at < tomorrow
            )
        ).count()
        
        # Processos urgentes
        urgent_processes = self.db.query(Process).filter(
            and_(
                Process.tenant_id == tenant_id,
                Process.requires_attention == True,
                Process.status == "active"
            )
        ).count()
        
        title = f"📊 RESUMO DIÁRIO - {today.strftime('%d/%m/%Y')}"
        message = f"📅 {deadlines_today} prazos vencendo hoje | 📋 {new_updates} novos andamentos | 🚨 {urgent_processes} processos urgentes"
        
        notification = ProcessNotification(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            process_id=None,
            user_id=user_id,
            notification_type="resumo",
            priority="normal",
            title=title,
            message=message,
            notification_data={
                "deadlines_today": deadlines_today,
                "new_updates": new_updates,
                "urgent_processes": urgent_processes,
                "date": today.isoformat()
            }
        )
        
        self.db.add(notification)
        self.db.commit()
        return notification
    
    # ==================== GESTÃO DE NOTIFICAÇÕES ====================
    
    async def get_user_notifications(
        self, 
        user_id: str, 
        tenant_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[ProcessNotification]:
        """Busca notificações do usuário"""
        
        query = self.db.query(ProcessNotification).filter(
            and_(
                ProcessNotification.user_id == user_id,
                ProcessNotification.tenant_id == tenant_id,
                ProcessNotification.is_archived == False
            )
        )
        
        if unread_only:
            query = query.filter(ProcessNotification.is_read == False)
        
        return query.order_by(desc(ProcessNotification.created_at)).limit(limit).all()
    
    async def mark_notification_as_read(self, notification_id: str, user_id: str) -> bool:
        """Marca notificação como lida"""
        
        notification = self.db.query(ProcessNotification).filter(
            and_(
                ProcessNotification.id == notification_id,
                ProcessNotification.user_id == user_id
            )
        ).first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.now()
            self.db.commit()
            return True
        
        return False
    
    async def mark_all_notifications_as_read(self, user_id: str, tenant_id: str) -> int:
        """Marca todas as notificações como lidas"""
        
        result = self.db.query(ProcessNotification).filter(
            and_(
                ProcessNotification.user_id == user_id,
                ProcessNotification.tenant_id == tenant_id,
                ProcessNotification.is_read == False
            )
        ).update({
            "is_read": True,
            "read_at": datetime.now()
        })
        
        self.db.commit()
        return result
    
    async def archive_notification(self, notification_id: str, user_id: str) -> bool:
        """Arquiva notificação"""
        
        notification = self.db.query(ProcessNotification).filter(
            and_(
                ProcessNotification.id == notification_id,
                ProcessNotification.user_id == user_id
            )
        ).first()
        
        if notification:
            notification.is_archived = True
            notification.archived_at = datetime.now()
            self.db.commit()
            return True
        
        return False
    
    # ==================== PREFERÊNCIAS DE NOTIFICAÇÃO ====================
    
    async def get_user_preferences(self, user_id: str, tenant_id: str) -> Optional[NotificationPreference]:
        """Busca preferências de notificação do usuário"""
        
        return self.db.query(NotificationPreference).filter(
            and_(
                NotificationPreference.user_id == user_id,
                NotificationPreference.tenant_id == tenant_id
            )
        ).first()
    
    async def create_or_update_preferences(
        self, 
        user_id: str, 
        tenant_id: str, 
        preferences_data: Dict[str, Any]
    ) -> NotificationPreference:
        """Cria ou atualiza preferências de notificação"""
        
        preferences = await self.get_user_preferences(user_id, tenant_id)
        
        if not preferences:
            preferences = NotificationPreference(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                user_id=user_id
            )
            self.db.add(preferences)
        
        # Atualizar campos
        for field, value in preferences_data.items():
            if hasattr(preferences, field):
                setattr(preferences, field, value)
        
        self.db.commit()
        return preferences
    
    # ==================== NOTIFICAÇÕES AUTOMÁTICAS ====================
    
    async def check_and_create_deadline_notifications(self, tenant_id: str) -> List[ProcessNotification]:
        """Verifica e cria notificações de prazos automaticamente"""
        
        notifications_created = []
        today = datetime.now().date()
        
        # Buscar prazos próximos
        upcoming_deadlines = self.db.query(ProcessDeadline).join(Process).filter(
            and_(
                Process.tenant_id == tenant_id,
                ProcessDeadline.status == "pending",
                ProcessDeadline.due_date >= today,
                ProcessDeadline.due_date <= today + timedelta(days=7)
            )
        ).all()
        
        for deadline in upcoming_deadlines:
            # Buscar advogados responsáveis pelo processo
            lawyers = self.db.query(User).join(Process.lawyers).filter(
                Process.id == deadline.process_id
            ).all()
            
            for lawyer in lawyers:
                # Verificar se já existe notificação recente
                existing_notification = self.db.query(ProcessNotification).filter(
                    and_(
                        ProcessNotification.user_id == lawyer.id,
                        ProcessNotification.process_id == deadline.process_id,
                        ProcessNotification.notification_type == "deadline",
                        ProcessNotification.notification_data.contains({"deadline_id": str(deadline.id)}),
                        ProcessNotification.created_at >= today
                    )
                ).first()
                
                if not existing_notification:
                    # Verificar preferências do usuário
                    preferences = await self.get_user_preferences(lawyer.id, tenant_id)
                    
                    if not preferences or preferences.deadline_notifications:
                        notification = await self.create_deadline_notification(deadline, lawyer.id)
                        notifications_created.append(notification)
        
        return notifications_created
    
    async def create_court_update_notifications_for_process(
        self, 
        process_id: str, 
        timeline_entry: ProcessTimeline
    ) -> List[ProcessNotification]:
        """Cria notificações de atualização do tribunal para todos os advogados do processo"""
        
        notifications_created = []
        
        # Buscar advogados responsáveis pelo processo
        lawyers = self.db.query(User).join(Process.lawyers).filter(
            Process.id == process_id
        ).all()
        
        for lawyer in lawyers:
            # Verificar preferências do usuário
            preferences = await self.get_user_preferences(lawyer.id, timeline_entry.process.tenant_id)
            
            if not preferences or preferences.court_updates:
                notification = await self.create_court_update_notification(timeline_entry, lawyer.id)
                notifications_created.append(notification)
        
        return notifications_created
