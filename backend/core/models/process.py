from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid
from sqlalchemy.orm import Session
from core.models.user_roles import UserSpecialty

class Process(Base):
    """Modelo para processos jurídicos"""
    __tablename__ = "processes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações básicas
    cnj_number = Column(String(50), nullable=True)  # Número CNJ
    court = Column(String(255), nullable=True)  # Tribunal
    jurisdiction = Column(String(255), nullable=True)  # Comarca
    subject = Column(Text, nullable=False)  # Assunto do processo
    status = Column(String(50), default="active")  # active, closed, suspended
    
    # Relacionamentos
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    
    # Especialidade do processo
    specialty_id = Column(UUID(as_uuid=True), ForeignKey("specialties.id"), nullable=True)
    
    # Informações adicionais
    priority = Column(String(50), default="normal")  # low, normal, high, urgent
    estimated_value = Column(Integer, nullable=True)  # Valor estimado em centavos
    notes = Column(Text, nullable=True)
    
    # Configurações
    is_confidential = Column(Boolean, default=False)
    requires_attention = Column(Boolean, default=False)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamentos
    client = relationship("Client", back_populates="processes")
    specialty = relationship("Specialty")
    lawyers = relationship("ProcessLawyer", back_populates="process")
    documents = relationship("Document", back_populates="process")
    # tasks = relationship("Task", back_populates="process")  # Temporariamente comentado
    financial_records = relationship("FinancialRecord", back_populates="process")

class ProcessLawyer(Base):
    """Relacionamento processo-advogado"""
    __tablename__ = "process_lawyers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Tipo de participação
    role = Column(String(50), default="lawyer")  # lawyer, assistant, coordinator
    is_primary = Column(Boolean, default=False)  # Advogado principal
    
    # Responsabilidades
    can_sign_documents = Column(Boolean, default=True)
    can_manage_process = Column(Boolean, default=True)
    can_view_financial = Column(Boolean, default=False)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    assigned_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamentos
    process = relationship("Process", back_populates="lawyers")
    lawyer = relationship("User")
    
    # __table_args__ = (
    #     UniqueConstraint('process_id', 'lawyer_id', name='unique_process_lawyer'),
    # )

class ProcessTimeline(Base):
    """Timeline de andamentos do processo"""
    __tablename__ = "process_timeline"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    
    # Informações do andamento
    date = Column(DateTime, nullable=False)
    type = Column(String(100), nullable=False)  # sentença, audiência, petição, etc.
    description = Column(Text, nullable=False)
    court_decision = Column(Text, nullable=True)
    
    # Classificação automática por IA
    ai_classification = Column(String(100), nullable=True)
    ai_confidence = Column(Integer, nullable=True)  # 0-100
    
    # Arquivos relacionados
    documents = Column(JSON, default=list)  # Lista de documentos relacionados
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamento
    process = relationship("Process")

class ProcessDeadline(Base):
    """Prazos críticos do processo"""
    __tablename__ = "process_deadlines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    
    # Informações do prazo
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    deadline_type = Column(String(50), nullable=False)  # legal, internal, client
    
    # Status
    status = Column(String(50), default="pending")  # pending, completed, overdue
    completed_at = Column(DateTime, nullable=True)
    completed_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Notificações
    notify_days_before = Column(Integer, default=3)  # Dias antes para notificar
    is_critical = Column(Boolean, default=False)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamento
    process = relationship("Process")

# Serviço para gerenciar processos
class ProcessService:
    """Serviço para gerenciar processos com isolamento por tenant"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def create_process(self, process_data: dict, lawyers: list, created_by: str):
        """Cria um novo processo com advogados"""
        try:
            # Cria o processo
            import uuid
            # Converte IDs para UUID se necessário
            process_data_clean = {}
            for key, value in process_data.items():
                if key in ['client_id', 'specialty_id'] and value and isinstance(value, str):
                    process_data_clean[key] = uuid.UUID(value)
                else:
                    process_data_clean[key] = value
            
            process = Process(
                tenant_id=uuid.UUID(self.tenant_id) if isinstance(self.tenant_id, str) else self.tenant_id,
                **process_data_clean,
                created_by=uuid.UUID(created_by) if created_by and isinstance(created_by, str) else created_by
            )
            self.db.add(process)
            self.db.flush()  # Para obter o ID
            
            # Adiciona os advogados
            for lawyer_data in lawyers:
                process_lawyer = ProcessLawyer(
                    process_id=process.id,
                    lawyer_id=uuid.UUID(lawyer_data["lawyer_id"]) if isinstance(lawyer_data["lawyer_id"], str) else lawyer_data["lawyer_id"],
                    role=lawyer_data.get("role", "lawyer"),
                    is_primary=lawyer_data.get("is_primary", False),
                    can_sign_documents=lawyer_data.get("can_sign_documents", True),
                    can_manage_process=lawyer_data.get("can_manage_process", True),
                    can_view_financial=lawyer_data.get("can_view_financial", False),
                    assigned_by=uuid.UUID(created_by) if created_by and isinstance(created_by, str) else created_by
                )
                self.db.add(process_lawyer)
            
            self.db.commit()
            self.db.refresh(process)
            return process
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao criar processo: {e}")
            raise e
    
    async def get_user_processes(self, user_id: str, user_role: str):
        """Obtém processos do usuário baseado no role"""
        query = self.db.query(Process).filter(Process.tenant_id == self.tenant_id)
        
        # Se não é admin, filtra apenas processos do usuário
        if user_role != "admin":
            query = query.join(ProcessLawyer).filter(ProcessLawyer.lawyer_id == user_id)
        
        processes = query.all()
        
        # Carrega relacionamentos
        for process in processes:
            await self._load_process_relationships(process)
        
        return processes

    async def get_all_processes(self, skip: int = 0, limit: int = 100, search: str = None, status: str = None, specialty_id: str = None):
        """Obtém todos os processos com filtros"""
        try:
            query = self.db.query(Process).filter(Process.tenant_id == self.tenant_id)
            
            if search:
                query = query.filter(Process.subject.ilike(f"%{search}%"))
            if status:
                query = query.filter(Process.status == status)
            if specialty_id:
                query = query.filter(Process.specialty_id == specialty_id)
            
            processes = query.offset(skip).limit(limit).all()
            
            # Carrega relacionamentos
            for process in processes:
                try:
                    await self._load_process_relationships(process)
                except Exception as e:
                    print(f"Erro ao carregar relacionamentos do processo {process.id}: {e}")
                    # Define valores padrão em caso de erro
                    process.client = None
                    process.specialty = None
                    process.lawyers = []
            
            return processes
        except Exception as e:
            print(f"Erro ao buscar processos: {e}")
            return []

    async def _load_process_relationships(self, process: Process):
        """Carrega relacionamentos de um processo"""
        try:
            # Carrega cliente
            if process.client_id:
                from core.models.client import Client
                process.client = self.db.query(Client).filter(Client.id == process.client_id).first()
            
            # Carrega especialidade (da tabela legal_specialties)
            if process.specialty_id:
                from sqlalchemy import text
                result = self.db.execute(text("SELECT * FROM legal_specialties WHERE id = :specialty_id"), 
                                       {"specialty_id": process.specialty_id})
                specialty_data = result.fetchone()
                if specialty_data:
                    process.specialty = {
                        "id": str(specialty_data.id),
                        "name": specialty_data.name,
                        "code": specialty_data.code,
                        "description": specialty_data.description,
                        "is_active": specialty_data.is_active,
                        "requires_oab": specialty_data.requires_oab
                    }
            
            # Carrega advogados
            process.lawyers = self.db.query(ProcessLawyer).filter(ProcessLawyer.process_id == process.id).all()
        except Exception as e:
            print(f"Erro ao carregar relacionamentos do processo: {e}")
            # Define valores padrão em caso de erro
            process.client = None
            process.specialty = None
            process.lawyers = []
        for lawyer in process.lawyers:
            from core.models.user import User
            lawyer.lawyer = self.db.query(User).filter(User.id == lawyer.lawyer_id).first()
    
    async def get_process(self, process_id: str):
        """Obtém um processo específico"""
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == self.tenant_id
        ).first()
        
        if process:
            await self._load_process_relationships(process)
        
        return process

    async def get_process_lawyers(self, process_id: str):
        """Obtém advogados de um processo"""
        return self.db.query(ProcessLawyer).filter(
            ProcessLawyer.process_id == process_id
        ).all()
    
    async def update_process(self, process_id: str, process_data: dict):
        """Atualiza um processo"""
        process = self.db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == self.tenant_id
        ).first()
        
        if not process:
            return None
        
        # Atualiza apenas os campos fornecidos
        for field, value in process_data.items():
            if hasattr(process, field) and value is not None:
                setattr(process, field, value)
        
        self.db.commit()
        self.db.refresh(process)
        
        # Carrega relacionamentos
        await self._load_process_relationships(process)
        
        return process

    async def add_lawyer_to_process(self, process_id: str, lawyer_id: str, role: str = "lawyer", assigned_by: str = None):
        """Adiciona advogado ao processo"""
        # Verifica se advogado tem especialidade compatível
        process = self.db.query(Process).filter(Process.id == process_id).first()
        if process.specialty_id:
            user_specialty = self.db.query(UserSpecialty).filter(
                UserSpecialty.user_id == lawyer_id,
                UserSpecialty.specialty_id == process.specialty_id
            ).first()
            
            if not user_specialty:
                raise ValueError("Advogado não possui especialidade compatível com o processo")
        
        process_lawyer = ProcessLawyer(
            process_id=process_id,
            lawyer_id=lawyer_id,
            role=role,
            assigned_by=assigned_by
        )
        self.db.add(process_lawyer)
        self.db.commit()
        return process_lawyer
