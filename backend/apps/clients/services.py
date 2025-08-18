from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional
from core.models.client import Client
from apps.clients.schemas import ClientCreate, ClientUpdate
import uuid

class ClientService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_client(self, client_data: ClientCreate, tenant_id: str) -> Client:
        """Cria um novo cliente"""
        # Verificar se já existe um cliente com o mesmo email no tenant
        if client_data.email:
            existing = self.db.query(Client).filter(
                and_(
                    Client.tenant_id == tenant_id,
                    Client.email.ilike(client_data.email)
                )
            ).first()
            
            if existing:
                raise ValueError(f"Já existe um cliente com o email '{client_data.email}'")
        
        # Verificar se já existe um cliente com o mesmo CPF/CNPJ no tenant
        if client_data.cpf_cnpj:
            existing = self.db.query(Client).filter(
                and_(
                    Client.tenant_id == tenant_id,
                    Client.cpf_cnpj == client_data.cpf_cnpj
                )
            ).first()
            
            if existing:
                raise ValueError(f"Já existe um cliente com o CPF/CNPJ '{client_data.cpf_cnpj}'")
        
        # Criar novo cliente
        client = Client(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=client_data.name,
            email=client_data.email,
            phone=client_data.phone,
            cpf_cnpj=client_data.cpf_cnpj,
            person_type=client_data.person_type,
            address=client_data.address,
            birth_date=client_data.birth_date,
            occupation=client_data.occupation,
            company_name=client_data.company_name,
            company_role=client_data.company_role,
            is_vip=client_data.is_vip,
            notes=client_data.notes,
            is_active=True
        )
        
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        
        return client
    
    async def get_client(self, client_id: str, tenant_id: str) -> Optional[Client]:
        """Obtém um cliente específico"""
        return self.db.query(Client).filter(
            and_(
                Client.id == client_id,
                Client.tenant_id == tenant_id
            )
        ).first()
    
    async def list_clients(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        person_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_vip: Optional[bool] = None,
        order_by: str = "name"
    ) -> List[Client]:
        """Lista clientes com filtros"""
        query = self.db.query(Client).filter(Client.tenant_id == tenant_id)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    Client.name.ilike(f"%{search}%"),
                    Client.email.ilike(f"%{search}%"),
                    Client.cpf_cnpj.ilike(f"%{search}%"),
                    Client.company_name.ilike(f"%{search}%")
                )
            )
        
        if person_type:
            query = query.filter(Client.person_type == person_type)
        
        if is_active is not None:
            query = query.filter(Client.is_active == is_active)
        
        if is_vip is not None:
            query = query.filter(Client.is_vip == is_vip)
        
        # Aplicar ordenação
        if order_by == "name":
            query = query.order_by(asc(Client.name))
        elif order_by == "created_at":
            query = query.order_by(desc(Client.created_at))
        elif order_by == "person_type":
            query = query.order_by(asc(Client.person_type))
        else:
            query = query.order_by(asc(Client.name))
        
        return query.offset(skip).limit(limit).all()
    
    async def update_client(
        self,
        client_id: str,
        client_data: ClientUpdate,
        tenant_id: str
    ) -> Optional[Client]:
        """Atualiza um cliente"""
        client = await self.get_client(client_id, tenant_id)
        if not client:
            return None
        
        # Verificar duplicatas se email foi alterado
        if client_data.email and client_data.email != client.email:
            existing = self.db.query(Client).filter(
                and_(
                    Client.tenant_id == tenant_id,
                    Client.email.ilike(client_data.email),
                    Client.id != client_id
                )
            ).first()
            
            if existing:
                raise ValueError(f"Já existe um cliente com o email '{client_data.email}'")
        
        # Verificar duplicatas se CPF/CNPJ foi alterado
        if client_data.cpf_cnpj and client_data.cpf_cnpj != client.cpf_cnpj:
            existing = self.db.query(Client).filter(
                and_(
                    Client.tenant_id == tenant_id,
                    Client.cpf_cnpj == client_data.cpf_cnpj,
                    Client.id != client_id
                )
            ).first()
            
            if existing:
                raise ValueError(f"Já existe um cliente com o CPF/CNPJ '{client_data.cpf_cnpj}'")
        
        # Atualizar campos
        update_data = client_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        self.db.commit()
        self.db.refresh(client)
        
        return client
    
    async def delete_client(self, client_id: str, tenant_id: str) -> bool:
        """Remove um cliente (soft delete)"""
        client = await self.get_client(client_id, tenant_id)
        if not client:
            return False
        
        # Verificar relacionamentos se necessário
        # if client.processes:
        #     raise ValueError("Não é possível excluir um cliente que possui processos vinculados")
        
        # Soft delete
        client.is_active = False
        self.db.commit()
        return True
    
    async def activate_client(self, client_id: str, tenant_id: str) -> bool:
        """Reativa um cliente"""
        client = await self.get_client(client_id, tenant_id)
        if not client:
            return False
        
        client.is_active = True
        self.db.commit()
        return True
    
    async def get_client_count(self, tenant_id: str, search: str = None, person_type: str = None, 
                              is_active: bool = None, is_vip: bool = None) -> int:
        """Retorna o total de clientes com filtros aplicados"""
        query = self.db.query(Client).filter(Client.tenant_id == tenant_id)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    Client.name.ilike(f"%{search}%"),
                    Client.email.ilike(f"%{search}%"),
                    Client.cpf_cnpj.ilike(f"%{search}%"),
                    Client.company_name.ilike(f"%{search}%")
                )
            )
        
        if person_type:
            query = query.filter(Client.person_type == person_type)
        
        if is_active is not None:
            query = query.filter(Client.is_active == is_active)
        
        if is_vip is not None:
            query = query.filter(Client.is_vip == is_vip)
        
        return query.count()

    async def get_client_stats(self, tenant_id: str) -> dict:
        """Retorna estatísticas dos clientes"""
        total = self.db.query(Client).filter(Client.tenant_id == tenant_id).count()
        active = self.db.query(Client).filter(
            and_(
                Client.tenant_id == tenant_id,
                Client.is_active == True
            )
        ).count()
        inactive = total - active
        
        # Contagem por tipo de pessoa
        pf_count = self.db.query(Client).filter(
            and_(
                Client.tenant_id == tenant_id,
                Client.person_type == "PF",
                Client.is_active == True
            )
        ).count()
        
        pj_count = self.db.query(Client).filter(
            and_(
                Client.tenant_id == tenant_id,
                Client.person_type == "PJ",
                Client.is_active == True
            )
        ).count()
        
        # Contagem VIP
        vip_count = self.db.query(Client).filter(
            and_(
                Client.tenant_id == tenant_id,
                Client.is_vip == True,
                Client.is_active == True
            )
        ).count()
        
        return {
            "total_clients": total,
            "active_clients": active,
            "inactive_clients": inactive,
            "pf_clients": pf_count,
            "pj_clients": pj_count,
            "vip_clients": vip_count
        }
