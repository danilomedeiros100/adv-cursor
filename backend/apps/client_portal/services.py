from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from core.models.process import Process, ProcessTimeline, ProcessDeadline
from core.models.client import Client
from core.models.specialty import Specialty
from core.models.user import User
from typing import List, Optional, Dict, Any
from datetime import datetime

class ClientPortalService:
    def __init__(self, db: Session, client_id: str):
        self.db = db
        self.client_id = client_id
    
    async def get_client_processes(self, skip: int = 0, limit: int = 50, status: str = None) -> List[dict]:
        """Lista processos do cliente"""
        query = self.db.query(Process).filter(Process.client_id == self.client_id)
        
        if status:
            query = query.filter(Process.status == status)
        
        processes = query.offset(skip).limit(limit).all()
        
        processes_data = []
        for process in processes:
            processes_data.append({
                "id": str(process.id),
                "subject": process.subject,
                "cnj_number": process.cnj_number,
                "court": process.court,
                "jurisdiction": process.jurisdiction,
                "status": process.status,
                "priority": process.priority,
                "created_at": process.created_at.isoformat() if process.created_at else None,
                "updated_at": process.updated_at.isoformat() if process.updated_at else None
            })
        
        return processes_data
    
    async def get_client_process(self, process_id: str) -> Optional[dict]:
        """Obtém detalhes de um processo específico do cliente"""
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.client_id == self.client_id
        ).first()
        
        if not process:
            return None
        
        return {
            "id": str(process.id),
            "subject": process.subject,
            "cnj_number": process.cnj_number,
            "court": process.court,
            "jurisdiction": process.jurisdiction,
            "status": process.status,
            "priority": process.priority,
            "estimated_value": process.estimated_value,
            "notes": process.notes,
            "created_at": process.created_at.isoformat() if process.created_at else None,
            "updated_at": process.updated_at.isoformat() if process.updated_at else None
        }
    
    async def get_process_timeline(self, process_id: str) -> List[dict]:
        """Obtém timeline do processo (versão simplificada para cliente)"""
        # Verifica se o processo pertence ao cliente
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.client_id == self.client_id
        ).first()
        
        if not process:
            return []
        
        # Busca os itens da timeline
        timeline_items = self.db.query(ProcessTimeline).filter(
            ProcessTimeline.process_id == process_id
        ).order_by(ProcessTimeline.date.desc()).all()
        
        timeline_data = []
        for item in timeline_items:
            timeline_data.append({
                "id": str(item.id),
                "date": item.date.isoformat() if item.date else None,
                "type": item.type,
                "description": item.description,
                "court_decision": item.court_decision,
                "created_at": item.created_at.isoformat() if item.created_at else None
            })
        
        return timeline_data
    
    async def get_process_documents(self, process_id: str, skip: int = 0, limit: int = 50) -> List[dict]:
        """Lista documentos do processo (apenas documentos compartilhados)"""
        # Verifica se o processo pertence ao cliente
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.client_id == self.client_id
        ).first()
        
        if not process:
            return []
        
        # Por enquanto, retorna lista vazia (implementar quando tivermos documentos)
        return []
    
    async def get_document_download_url(self, document_id: str) -> Optional[str]:
        """Obtém URL de download do documento"""
        # Por enquanto, retorna None (implementar quando tivermos documentos)
        return None
    
    async def get_messages(self, skip: int = 0, limit: int = 50) -> List[dict]:
        """Lista mensagens trocadas com a empresa"""
        # Por enquanto, retorna lista vazia (implementar quando tivermos mensagens)
        return []
    
    async def send_message(self, message_data: dict) -> dict:
        """Envia mensagem para a empresa"""
        # Por enquanto, retorna mensagem de sucesso (implementar quando tivermos mensagens)
        return {
            "id": "temp-id",
            "subject": message_data.get("subject", ""),
            "message": message_data.get("message", ""),
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def get_dashboard_summary(self) -> dict:
        """Dashboard resumido do cliente"""
        # Conta processos do cliente
        total_processes = self.db.query(Process).filter(Process.client_id == self.client_id).count()
        active_processes = self.db.query(Process).filter(
            Process.client_id == self.client_id,
            Process.status == "active"
        ).count()
        
        return {
            "total_processes": total_processes,
            "active_processes": active_processes,
            "recent_activities": []
        }
    
    async def get_client_profile(self) -> dict:
        """Obtém perfil do cliente"""
        client = self.db.query(Client).filter(Client.id == self.client_id).first()
        
        if not client:
            return {}
        
        return {
            "id": str(client.id),
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "address": client.address,
            "created_at": client.created_at.isoformat() if client.created_at else None
        }
    
    async def update_client_profile(self, profile_data: dict) -> dict:
        """Atualiza perfil do cliente"""
        client = self.db.query(Client).filter(Client.id == self.client_id).first()
        
        if not client:
            return {}
        
        # Atualiza apenas os campos fornecidos
        for field, value in profile_data.items():
            if hasattr(client, field):
                setattr(client, field, value)
        
        client.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(client)
        
        return await self.get_client_profile()
    
    async def request_data_export(self) -> dict:
        """Solicita exportação de dados pessoais (LGPD)"""
        # Por enquanto, retorna sucesso (implementar quando tivermos LGPD)
        return {
            "request_id": "temp-export-id",
            "status": "pending",
            "estimated_completion": "7 days"
        }
    
    async def request_data_deletion(self) -> dict:
        """Solicita exclusão de dados pessoais (LGPD)"""
        # Por enquanto, retorna sucesso (implementar quando tivermos LGPD)
        return {
            "request_id": "temp-deletion-id",
            "status": "pending",
            "estimated_completion": "30 days"
        }
