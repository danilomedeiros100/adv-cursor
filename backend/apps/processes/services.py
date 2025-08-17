from sqlalchemy.orm import Session
from core.models.process import Process
from apps.processes.schemas import ProcessCreate, ProcessUpdate
import uuid

class ProcessService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_process(self, process_data: ProcessCreate, tenant_id: str):
        """Cria um novo processo"""
        process = Process(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            title=process_data.title,
            description=process_data.description,
            process_number=process_data.process_number,
            court=process_data.court,
            specialty_id=process_data.specialty_id,
            client_id=process_data.client_id,
            status=process_data.status,
            priority=process_data.priority,
            estimated_value=process_data.estimated_value,
            start_date=process_data.start_date,
            expected_end_date=process_data.expected_end_date
        )
        self.db.add(process)
        self.db.commit()
        self.db.refresh(process)
        return process
    
    async def get_process(self, process_id: str, tenant_id: str):
        """Obtém um processo específico"""
        return self.db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == tenant_id
        ).first()
    
    async def list_processes(self, tenant_id: str, skip: int = 0, limit: int = 100, search: str = None):
        """Lista processos com filtros"""
        query = self.db.query(Process).filter(Process.tenant_id == tenant_id)
        
        if search:
            query = query.filter(Process.title.ilike(f"%{search}%"))
        
        return query.offset(skip).limit(limit).all()
    
    async def update_process(self, process_id: str, process_data: ProcessUpdate, tenant_id: str):
        """Atualiza um processo"""
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == tenant_id
        ).first()
        
        if not process:
            return None
        
        update_data = process_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(process, field, value)
        
        self.db.commit()
        self.db.refresh(process)
        return process
    
    async def delete_process(self, process_id: str, tenant_id: str):
        """Deleta um processo (soft delete)"""
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == tenant_id
        ).first()
        
        if not process:
            return False
        
        process.is_active = False
        self.db.commit()
        return True
