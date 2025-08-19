from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from core.models.process import Process, ProcessLawyer, ProcessSpecialty
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
        
        # Adiciona as especialidades ao processo
        specialty_ids = process_data.get("specialty_ids", [])
        if specialty_ids:
            for specialty_id in specialty_ids:
                process_specialty = ProcessSpecialty(
                    id=uuid.uuid4(),
                    process_id=process.id,
                    specialty_id=specialty_id,
                    created_by=created_by
                )
                self.db.add(process_specialty)
        
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
        """Obtém timeline de andamentos do processo"""
        from core.models.process import ProcessTimeline
        
        timeline_entries = self.db.query(ProcessTimeline).filter(
            ProcessTimeline.process_id == process_id
        ).order_by(ProcessTimeline.date.desc()).all()
        
        return [entry.to_dict() for entry in timeline_entries]
    
    async def add_timeline_entry(self, process_id: str, entry_data: dict, user_id: str) -> dict:
        """Adiciona novo andamento ao processo"""
        from core.models.process import ProcessTimeline
        from datetime import datetime
        
        timeline_entry = ProcessTimeline(
            id=uuid.uuid4(),
            process_id=process_id,
            date=datetime.fromisoformat(entry_data.get("occurred_at", datetime.now().isoformat())),
            type=entry_data.get("type", "other"),
            description=entry_data.get("description", ""),
            court_decision=entry_data.get("court_decision"),
            documents=entry_data.get("documents", []),
            created_by=user_id
        )
        
        self.db.add(timeline_entry)
        self.db.commit()
        self.db.refresh(timeline_entry)
        
        return timeline_entry.to_dict()
    
    async def update_timeline_entry(self, process_id: str, entry_id: str, entry_data: dict, user_id: str) -> Optional[dict]:
        """Atualiza andamento do processo"""
        from core.models.process import ProcessTimeline
        from datetime import datetime
        
        timeline_entry = self.db.query(ProcessTimeline).filter(
            ProcessTimeline.id == entry_id,
            ProcessTimeline.process_id == process_id
        ).first()
        
        if not timeline_entry:
            return None
        
        # Atualizar campos
        if "occurred_at" in entry_data:
            timeline_entry.date = datetime.fromisoformat(entry_data["occurred_at"])
        if "type" in entry_data:
            timeline_entry.type = entry_data["type"]
        if "description" in entry_data:
            timeline_entry.description = entry_data["description"]
        if "court_decision" in entry_data:
            timeline_entry.court_decision = entry_data["court_decision"]
        if "documents" in entry_data:
            timeline_entry.documents = entry_data["documents"]
        
        self.db.commit()
        self.db.refresh(timeline_entry)
        
        return timeline_entry.to_dict()
    
    async def delete_timeline_entry(self, process_id: str, entry_id: str) -> bool:
        """Remove andamento do processo"""
        from core.models.process import ProcessTimeline
        
        timeline_entry = self.db.query(ProcessTimeline).filter(
            ProcessTimeline.id == entry_id,
            ProcessTimeline.process_id == process_id
        ).first()
        
        if not timeline_entry:
            return False
        
        self.db.delete(timeline_entry)
        self.db.commit()
        
        return True

    async def get_process_deadlines(self, process_id: str) -> List[dict]:
        """Obtém prazos do processo"""
        from core.models.process import ProcessDeadline
        from datetime import datetime
        
        deadlines = self.db.query(ProcessDeadline).filter(
            ProcessDeadline.process_id == process_id
        ).order_by(ProcessDeadline.due_date.asc()).all()
        
        # Calcular status baseado na data
        now = datetime.now()
        for deadline in deadlines:
            if deadline.status == "pending":
                if deadline.due_date < now:
                    deadline.status = "overdue"
        
        return [deadline.to_dict() for deadline in deadlines]
    
    async def add_deadline(self, process_id: str, deadline_data: dict, user_id: str) -> dict:
        """Adiciona novo prazo ao processo"""
        from core.models.process import ProcessDeadline
        from datetime import datetime
        
        deadline = ProcessDeadline(
            id=uuid.uuid4(),
            process_id=process_id,
            title=deadline_data.get("title", ""),
            description=deadline_data.get("description"),
            due_date=datetime.fromisoformat(deadline_data.get("due_date", datetime.now().isoformat())),
            deadline_type=deadline_data.get("deadline_type", "internal"),
            notify_days_before=deadline_data.get("notify_days_before", 3),
            is_critical=deadline_data.get("is_critical", False),
            status="pending",
            created_by=user_id
        )
        
        self.db.add(deadline)
        self.db.commit()
        self.db.refresh(deadline)
        
        return deadline.to_dict()
    
    async def complete_deadline(self, process_id: str, deadline_id: str, user_id: str) -> bool:
        """Marca prazo como concluído"""
        from core.models.process import ProcessDeadline
        from datetime import datetime
        
        deadline = self.db.query(ProcessDeadline).filter(
            ProcessDeadline.id == deadline_id,
            ProcessDeadline.process_id == process_id
        ).first()
        
        if not deadline:
            return False
        
        deadline.status = "completed"
        deadline.completed_at = datetime.now()
        deadline.completed_by = user_id
        
        self.db.commit()
        
        return True
    
    async def delete_deadline(self, process_id: str, deadline_id: str) -> bool:
        """Remove prazo do processo"""
        from core.models.process import ProcessDeadline
        
        deadline = self.db.query(ProcessDeadline).filter(
            ProcessDeadline.id == deadline_id,
            ProcessDeadline.process_id == process_id
        ).first()
        
        if not deadline:
            return False
        
        self.db.delete(deadline)
        self.db.commit()
        
        return True

    async def get_process_documents(self, process_id: str) -> List[dict]:
        """Obtém documentos do processo"""
        from core.models.document import Document
        
        documents = self.db.query(Document).filter(
            Document.process_id == process_id
        ).order_by(Document.created_at.desc()).all()
        
        return [doc.to_dict() for doc in documents]
    
    async def upload_document(self, process_id: str, file, title: str, description: str, tags: List[str], user_id: str) -> dict:
        """Faz upload de documento para o processo"""
        from core.models.document import Document
        import os
        import shutil
        from datetime import datetime
        
        # Criar diretório se não existir
        upload_dir = f"uploads/processes/{process_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Salvar arquivo
        file_extension = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, file_name)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Criar documento no banco
        document = Document(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            process_id=process_id,
            title=title,
            description=description,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            mime_type=file.content_type,
            tags=tags,
            created_by=user_id
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return document.to_dict()
    
    async def delete_document(self, process_id: str, document_id: str) -> bool:
        """Remove documento do processo"""
        from core.models.document import Document
        import os
        
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.process_id == process_id
        ).first()
        
        if not document:
            return False
        
        # Remover arquivo físico
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        self.db.delete(document)
        self.db.commit()
        
        return True

    async def get_process_notes(self, process_id: str) -> List[dict]:
        """Obtém anotações do processo"""
        from core.models.process import ProcessNote
        
        notes = self.db.query(ProcessNote).filter(
            ProcessNote.process_id == process_id
        ).order_by(ProcessNote.created_at.desc()).all()
        
        return [note.to_dict() for note in notes]
    
    async def add_process_note(self, process_id: str, note_data: dict, user_id: str) -> dict:
        """Adiciona anotação ao processo"""
        from core.models.process import ProcessNote
        
        note = ProcessNote(
            id=uuid.uuid4(),
            process_id=process_id,
            content=note_data.get("content", ""),
            mentions=note_data.get("mentions", []),
            created_by=user_id
        )
        
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        
        return note.to_dict()
    
    async def delete_process_note(self, process_id: str, note_id: str) -> bool:
        """Remove anotação do processo"""
        from core.models.process import ProcessNote
        
        note = self.db.query(ProcessNote).filter(
            ProcessNote.id == note_id,
            ProcessNote.process_id == process_id
        ).first()
        
        if not note:
            return False
        
        self.db.delete(note)
        self.db.commit()
        
        return True

    async def _format_process_response(self, process: Process) -> ProcessResponse:
        """Formata a resposta do processo com relacionamentos"""
        # Busca o cliente
        client = self.db.query(Client).filter(Client.id == process.client_id).first()
        client_data = {
            "id": client.id,
            "name": client.name,
            "email": client.email
        } if client else None
        
        # Busca a especialidade (mantido para compatibilidade)
        specialty = None
        if process.specialty_id:
            specialty = self.db.query(Specialty).filter(Specialty.id == process.specialty_id).first()
        specialty_data = {
            "id": specialty.id,
            "name": specialty.name,
            "description": specialty.description
        } if specialty else None
        
        # Busca as especialidades (novo relacionamento)
        process_specialties = self.db.query(ProcessSpecialty).filter(ProcessSpecialty.process_id == process.id).all()
        specialties_data = []
        for process_specialty in process_specialties:
            specialty_obj = self.db.query(Specialty).filter(Specialty.id == process_specialty.specialty_id).first()
            if specialty_obj:
                specialties_data.append({
                    "id": str(specialty_obj.id),
                    "name": specialty_obj.name,
                    "description": specialty_obj.description,
                    "code": specialty_obj.code
                })
        
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
            specialties=specialties_data,
            lawyers=lawyers_data
        )
