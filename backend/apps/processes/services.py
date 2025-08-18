from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from core.models.process import Process, ProcessLawyer
from core.models.client import Client
from core.models.specialty import Specialty
from core.models.user import User
from apps.processes.schemas import ProcessCreate, ProcessUpdate, ProcessResponse
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProcessService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def create_process(self, process_data: dict, lawyers_data: List[Dict[str, Any]], created_by: str) -> ProcessResponse:
        """Cria um novo processo"""
        # Cria o processo
        process = Process(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            subject=process_data["subject"],
            cnj_number=process_data.get("cnj_number"),
            court=process_data.get("court"),
            jurisdiction=process_data.get("jurisdiction"),
            client_id=process_data["client_id"],
            specialty_id=process_data.get("specialty_id"),
            priority=process_data.get("priority", "normal"),
            estimated_value=process_data.get("estimated_value"),
            notes=process_data.get("notes"),
            is_confidential=process_data.get("is_confidential", False),
            requires_attention=process_data.get("requires_attention", False),
            status="active",
            created_by=created_by
        )
        
        self.db.add(process)
        self.db.flush()  # Para obter o ID do processo
        
        # Adiciona os advogados ao processo
        for lawyer_data in lawyers_data:
            process_lawyer = ProcessLawyer(
                id=uuid.uuid4(),
                process_id=process.id,
                lawyer_id=lawyer_data["lawyer_id"],
                role=lawyer_data.get("role", "lawyer"),
                is_primary=lawyer_data.get("is_primary", False),
                can_sign_documents=lawyer_data.get("can_sign_documents", True),
                can_manage_process=lawyer_data.get("can_manage_process", True),
                can_view_financial=lawyer_data.get("can_view_financial", False),
                assigned_by=created_by
            )
            self.db.add(process_lawyer)
        
        self.db.commit()
        self.db.refresh(process)
        
        return await self._format_process_response(process)
    
    async def get_process(self, process_id: str) -> Optional[ProcessResponse]:
        """Obtém um processo específico"""
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == self.tenant_id
        ).first()
        
        if not process:
            return None
        
        return await self._format_process_response(process)
    
    async def list_processes(self, skip: int = 0, limit: int = 100, search: str = None, 
                           status: str = None, specialty_id: str = None, 
                           priority: str = None, client_id: str = None) -> List[ProcessResponse]:
        """Lista processos com filtros"""
        query = self.db.query(Process).filter(Process.tenant_id == self.tenant_id)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    Process.subject.ilike(f"%{search}%"),
                    Process.cnj_number.ilike(f"%{search}%"),
                    Process.court.ilike(f"%{search}%")
                )
            )
        
        if status:
            query = query.filter(Process.status == status)
        
        if specialty_id:
            query = query.filter(Process.specialty_id == specialty_id)
        
        if priority:
            query = query.filter(Process.priority == priority)
        
        if client_id:
            query = query.filter(Process.client_id == client_id)
        
        processes = query.offset(skip).limit(limit).all()
        
        return [await self._format_process_response(process) for process in processes]
    
    async def update_process(self, process_id: str, process_data: ProcessUpdate) -> Optional[ProcessResponse]:
        """Atualiza um processo"""
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == self.tenant_id
        ).first()
        
        if not process:
            return None
        
        # Atualiza apenas os campos fornecidos
        update_data = process_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(process, field, value)
        
        process.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(process)
        
        return await self._format_process_response(process)
    
    async def delete_process(self, process_id: str) -> bool:
        """Deleta um processo (soft delete)"""
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == self.tenant_id
        ).first()
        
        if not process:
            return False
        
        process.status = "closed"
        process.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    async def get_user_processes(self, user_id: str, role: str = "lawyer") -> List[ProcessResponse]:
        """Obtém processos de um usuário específico"""
        query = self.db.query(Process).join(ProcessLawyer).filter(
            Process.tenant_id == self.tenant_id,
            ProcessLawyer.lawyer_id == user_id
        )
        
        processes = query.all()
        return [await self._format_process_response(process) for process in processes]
    
    async def get_process_timeline(self, process_id: str) -> List[dict]:
        """Obtém timeline do processo"""
        from core.models.process import ProcessTimeline
        
        # Verifica se o processo existe e pertence ao tenant
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == self.tenant_id
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
                "process_id": str(item.process_id),
                "date": item.date.isoformat() if item.date else None,
                "type": item.type,
                "description": item.description,
                "court_decision": item.court_decision,
                "ai_classification": item.ai_classification,
                "ai_confidence": item.ai_confidence,
                "documents": item.documents or [],
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "created_by": str(item.created_by) if item.created_by else None
            })
        
        return timeline_data
    
    async def get_process_deadlines(self, process_id: str) -> List[dict]:
        """Obtém prazos do processo"""
        from core.models.process import ProcessDeadline
        
        # Verifica se o processo existe e pertence ao tenant
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == self.tenant_id
        ).first()
        
        if not process:
            return []
        
        # Busca os prazos
        deadlines = self.db.query(ProcessDeadline).filter(
            ProcessDeadline.process_id == process_id
        ).order_by(ProcessDeadline.due_date.asc()).all()
        
        deadlines_data = []
        for deadline in deadlines:
            deadlines_data.append({
                "id": str(deadline.id),
                "process_id": str(deadline.process_id),
                "title": deadline.title,
                "description": deadline.description,
                "due_date": deadline.due_date.isoformat() if deadline.due_date else None,
                "deadline_type": deadline.deadline_type,
                "status": deadline.status,
                "completed_at": deadline.completed_at.isoformat() if deadline.completed_at else None,
                "completed_by": str(deadline.completed_by) if deadline.completed_by else None,
                "notify_days_before": deadline.notify_days_before,
                "is_critical": deadline.is_critical,
                "created_at": deadline.created_at.isoformat() if deadline.created_at else None,
                "updated_at": deadline.updated_at.isoformat() if deadline.updated_at else None,
                "created_by": str(deadline.created_by) if deadline.created_by else None
            })
        
        return deadlines_data

    async def _format_process_response(self, process: Process) -> ProcessResponse:
        """Formata a resposta do processo com relacionamentos"""
        # Busca o cliente
        client = self.db.query(Client).filter(Client.id == process.client_id).first()
        client_data = {
            "id": client.id,
            "name": client.name,
            "email": client.email
        } if client else None
        
        # Busca a especialidade
        specialty = None
        if process.specialty_id:
            specialty = self.db.query(Specialty).filter(Specialty.id == process.specialty_id).first()
        specialty_data = {
            "id": specialty.id,
            "name": specialty.name,
            "description": specialty.description
        } if specialty else None
        
        # Busca os advogados
        lawyers = self.db.query(ProcessLawyer).filter(ProcessLawyer.process_id == process.id).all()
        lawyers_data = []
        for lawyer in lawyers:
            user = self.db.query(User).filter(User.id == lawyer.lawyer_id).first()
            lawyers_data.append({
                "id": str(lawyer.id),
                "process_id": str(lawyer.process_id),
                "lawyer_id": str(lawyer.lawyer_id),
                "role": lawyer.role,
                "is_primary": lawyer.is_primary,
                "can_sign_documents": lawyer.can_sign_documents,
                "can_manage_process": lawyer.can_manage_process,
                "can_view_financial": lawyer.can_view_financial,
                "created_at": lawyer.created_at.isoformat() if lawyer.created_at else None,
                "updated_at": lawyer.updated_at.isoformat() if lawyer.updated_at else None,
                "assigned_by": str(lawyer.assigned_by) if lawyer.assigned_by else None,
                "lawyer": {
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email
                } if user else None
            })
        
        return ProcessResponse(
            id=str(process.id),
            tenant_id=str(process.tenant_id),
            subject=process.subject,
            cnj_number=process.cnj_number,
            court=process.court,
            jurisdiction=process.jurisdiction,
            client_id=str(process.client_id),
            specialty_id=str(process.specialty_id) if process.specialty_id else None,
            priority=process.priority,
            estimated_value=process.estimated_value,
            notes=process.notes,
            is_confidential=process.is_confidential,
            requires_attention=process.requires_attention,
            status=process.status,
            created_at=process.created_at,
            updated_at=process.updated_at,
            created_by=str(process.created_by) if process.created_by else None,
            client=client_data,
            specialty=specialty_data,
            lawyers=lawyers_data
        )
