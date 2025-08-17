import asyncio
import json
import gzip
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import get_db
from core.models.tenant import Tenant
import boto3
import os

class BackupService:
    """Sistema de backup automático por tenant"""
    
    def __init__(self, db: Session):
        self.db = db
        self.s3_client = boto3.client('s3')
        self.backup_bucket = os.getenv('BACKUP_BUCKET', 'saas-juridico-backups')
        self.retention_days = 90
    
    async def create_tenant_backup(self, tenant_id: str, backup_type: str = "daily") -> Dict[str, Any]:
        """Cria backup completo de um tenant específico"""
        try:
            # Busca dados do tenant
            tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                raise ValueError(f"Tenant {tenant_id} não encontrado")
            
            # Gera timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_id = f"{tenant.slug}_{backup_type}_{timestamp}"
            
            # Coleta dados do tenant
            backup_data = await self._collect_tenant_data(tenant_id)
            
            # Comprime dados
            compressed_data = gzip.compress(json.dumps(backup_data, default=str).encode('utf-8'))
            
            # Upload para S3
            s3_key = f"tenants/{tenant.slug}/{backup_type}/{backup_id}.json.gz"
            self.s3_client.put_object(
                Bucket=self.backup_bucket,
                Key=s3_key,
                Body=compressed_data,
                Metadata={
                    'tenant_id': str(tenant_id),
                    'backup_type': backup_type,
                    'created_at': timestamp,
                    'data_size': str(len(compressed_data))
                }
            )
            
            # Registra backup no banco
            await self._register_backup(tenant_id, backup_id, s3_key, backup_type, len(compressed_data))
            
            return {
                "backup_id": backup_id,
                "tenant_id": str(tenant_id),
                "backup_type": backup_type,
                "s3_key": s3_key,
                "size_bytes": len(compressed_data),
                "created_at": timestamp
            }
            
        except Exception as e:
            raise Exception(f"Erro ao criar backup: {str(e)}")
    
    async def _collect_tenant_data(self, tenant_id: str) -> Dict[str, Any]:
        """Coleta todos os dados de um tenant"""
        backup_data = {
            "tenant_info": {},
            "users": [],
            "clients": [],
            "processes": [],
            "documents": [],
            "financial_records": [],
            "specialties": [],
            "audit_logs": []
        }
        
        # Dados do tenant
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        backup_data["tenant_info"] = {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "plan_type": tenant.plan_type,
            "settings": tenant.settings,
            "branding": tenant.branding
        }
        
        # Usuários do tenant
        from core.models.tenant import TenantUser
        tenant_users = self.db.query(TenantUser).filter(TenantUser.tenant_id == tenant_id).all()
        backup_data["users"] = [
            {
                "id": str(tu.id),
                "user_id": str(tu.user_id),
                "role": tu.role,
                "permissions": tu.permissions,
                "department": tu.department,
                "position": tu.position
            }
            for tu in tenant_users
        ]
        
        # Clientes
        from core.models.client import Client
        clients = self.db.query(Client).filter(Client.tenant_id == tenant_id).all()
        backup_data["clients"] = [
            {
                "id": str(c.id),
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "address": c.address,
                "created_at": c.created_at.isoformat()
            }
            for c in clients
        ]
        
        # Processos
        from core.models.process import Process, ProcessLawyer
        processes = self.db.query(Process).filter(Process.tenant_id == tenant_id).all()
        backup_data["processes"] = []
        
        for process in processes:
            process_data = {
                "id": str(process.id),
                "cnj_number": process.cnj_number,
                "subject": process.subject,
                "status": process.status,
                "client_id": str(process.client_id),
                "specialty_id": str(process.specialty_id) if process.specialty_id else None,
                "priority": process.priority,
                "created_at": process.created_at.isoformat()
            }
            
            # Advogados do processo
            lawyers = self.db.query(ProcessLawyer).filter(ProcessLawyer.process_id == process.id).all()
            process_data["lawyers"] = [
                {
                    "lawyer_id": str(pl.lawyer_id),
                    "role": pl.role,
                    "is_primary": pl.is_primary
                }
                for pl in lawyers
            ]
            
            backup_data["processes"].append(process_data)
        
        return backup_data
    
    async def _register_backup(self, tenant_id: str, backup_id: str, s3_key: str, backup_type: str, size_bytes: int):
        """Registra backup no banco de dados"""
        from core.models.backup import BackupRecord
        
        backup_record = BackupRecord(
            tenant_id=tenant_id,
            backup_id=backup_id,
            s3_key=s3_key,
            backup_type=backup_type,
            size_bytes=size_bytes,
            status="completed"
        )
        
        self.db.add(backup_record)
        self.db.commit()
    
    async def restore_tenant_backup(self, tenant_id: str, backup_id: str) -> Dict[str, Any]:
        """Restaura backup de um tenant"""
        try:
            # Busca backup no S3
            backup_record = self.db.query(BackupRecord).filter(
                BackupRecord.tenant_id == tenant_id,
                BackupRecord.backup_id == backup_id
            ).first()
            
            if not backup_record:
                raise ValueError(f"Backup {backup_id} não encontrado")
            
            # Download do S3
            response = self.s3_client.get_object(
                Bucket=self.backup_bucket,
                Key=backup_record.s3_key
            )
            
            compressed_data = response['Body'].read()
            backup_data = json.loads(gzip.decompress(compressed_data).decode('utf-8'))
            
            # Restaura dados
            await self._restore_tenant_data(backup_data)
            
            return {
                "backup_id": backup_id,
                "tenant_id": str(tenant_id),
                "status": "restored",
                "restored_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Erro ao restaurar backup: {str(e)}")
    
    async def cleanup_old_backups(self):
        """Remove backups antigos (mais de 90 dias)"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        old_backups = self.db.query(BackupRecord).filter(
            BackupRecord.created_at < cutoff_date
        ).all()
        
        for backup in old_backups:
            try:
                # Remove do S3
                self.s3_client.delete_object(
                    Bucket=self.backup_bucket,
                    Key=backup.s3_key
                )
                
                # Remove do banco
                self.db.delete(backup)
                
            except Exception as e:
                print(f"Erro ao remover backup {backup.backup_id}: {str(e)}")
        
        self.db.commit()
    
    async def schedule_backups(self):
        """Agenda backups automáticos"""
        # Backup diário para todos os tenants ativos
        tenants = self.db.query(Tenant).filter(Tenant.is_active == True).all()
        
        for tenant in tenants:
            try:
                await self.create_tenant_backup(tenant.id, "daily")
                print(f"Backup diário criado para tenant {tenant.slug}")
            except Exception as e:
                print(f"Erro no backup diário do tenant {tenant.slug}: {str(e)}")
        
        # Backup semanal (domingo)
        if datetime.utcnow().weekday() == 6:  # Domingo
            for tenant in tenants:
                try:
                    await self.create_tenant_backup(tenant.id, "weekly")
                    print(f"Backup semanal criado para tenant {tenant.slug}")
                except Exception as e:
                    print(f"Erro no backup semanal do tenant {tenant.slug}: {str(e)}")

# Modelo para registrar backups
class BackupRecord(Base):
    """Registro de backups realizados"""
    __tablename__ = "backup_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    backup_id = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False)
    backup_type = Column(String(50), nullable=False)  # daily, weekly, manual
    size_bytes = Column(Integer, nullable=False)
    status = Column(String(50), default="completed")  # completed, failed, restoring
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'backup_id', name='unique_tenant_backup'),
    )
