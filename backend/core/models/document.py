from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class Document(Base):
    """Modelo para documentos do sistema"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações básicas
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Caminho no S3
    file_size = Column(Integer, nullable=False)  # Tamanho em bytes
    mime_type = Column(String(100), nullable=False)
    
    # Tipo e categoria
    document_type = Column(String(100), nullable=False)  # petição, contrato, procuração, etc.
    category = Column(String(100), nullable=True)  # Categoria do documento
    
    # Relacionamentos
    process_id = Column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Versionamento
    version = Column(Integer, default=1)
    parent_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    
    # Assinatura digital
    is_signed = Column(Boolean, default=False)
    signed_at = Column(DateTime, nullable=True)
    signed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    signature_data = Column(JSON, nullable=True)  # Dados da assinatura
    
    # Configurações
    is_public = Column(Boolean, default=False)  # Visível para clientes
    is_confidential = Column(Boolean, default=False)
    tags = Column(JSON, default=list)
    
    # Status
    status = Column(String(50), default="draft")  # draft, final, archived
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relacionamentos
    process = relationship("Process", back_populates="documents")
    client = relationship("Client", back_populates="documents")
    creator = relationship("User", foreign_keys=[created_by])
    signer = relationship("User", foreign_keys=[signed_by])
    parent_document = relationship("Document", remote_side=[id])
    versions = relationship("Document", back_populates="parent_document")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "title": self.title,
            "description": self.description,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "document_type": self.document_type,
            "category": self.category,
            "process_id": str(self.process_id) if self.process_id else None,
            "client_id": str(self.client_id) if self.client_id else None,
            "version": self.version,
            "is_signed": self.is_signed,
            "signed_at": self.signed_at.isoformat() if self.signed_at else None,
            "is_public": self.is_public,
            "is_confidential": self.is_confidential,
            "tags": self.tags,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class DocumentTemplate(Base):
    """Modelos de documentos reutilizáveis"""
    __tablename__ = "document_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Informações básicas
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String(100), nullable=False)  # contrato, petição, etc.
    
    # Arquivo template
    template_file_path = Column(String(500), nullable=False)
    template_variables = Column(JSON, default=list)  # Variáveis disponíveis
    
    # Configurações
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # Template público
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "description": self.description,
            "template_type": self.template_type,
            "template_variables": self.template_variables,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
