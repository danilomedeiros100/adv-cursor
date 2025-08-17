from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional
from core.models.specialty import Specialty
from apps.specialties.schemas import SpecialtyCreate, SpecialtyUpdate

class SpecialtyService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_specialty(self, specialty_data: SpecialtyCreate, tenant_id: str) -> Specialty:
        """Cria uma nova especialidade para o tenant"""
        # Verificar se já existe uma especialidade com o mesmo nome no tenant
        existing = self.db.query(Specialty).filter(
            and_(
                Specialty.tenant_id == tenant_id,
                Specialty.name.ilike(specialty_data.name)
            )
        ).first()
        
        if existing:
            raise ValueError(f"Já existe uma especialidade com o nome '{specialty_data.name}'")
        
        # Criar nova especialidade
        specialty = Specialty(
            tenant_id=tenant_id,
            name=specialty_data.name,
            description=specialty_data.description,
            code=specialty_data.code,
            color=specialty_data.color,
            icon=specialty_data.icon,
            display_order=specialty_data.display_order or "0",
            requires_oab=specialty_data.requires_oab or False,
            min_experience_years=specialty_data.min_experience_years
        )
        
        self.db.add(specialty)
        self.db.commit()
        self.db.refresh(specialty)
        
        return specialty
    
    async def get_specialty(self, specialty_id: str, tenant_id: str) -> Optional[Specialty]:
        """Busca uma especialidade específica do tenant"""
        return self.db.query(Specialty).filter(
            and_(
                Specialty.id == specialty_id,
                Specialty.tenant_id == tenant_id
            )
        ).first()
    
    async def list_specialties(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        requires_oab: Optional[bool] = None,
        order_by: str = "display_order"
    ) -> List[Specialty]:
        """Lista especialidades do tenant com filtros"""
        query = self.db.query(Specialty).filter(Specialty.tenant_id == tenant_id)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    Specialty.name.ilike(f"%{search}%"),
                    Specialty.description.ilike(f"%{search}%"),
                    Specialty.code.ilike(f"%{search}%")
                )
            )
        
        if is_active is not None:
            query = query.filter(Specialty.is_active == is_active)
        
        if requires_oab is not None:
            query = query.filter(Specialty.requires_oab == requires_oab)
        
        # Aplicar ordenação
        if order_by == "name":
            query = query.order_by(asc(Specialty.name))
        elif order_by == "created_at":
            query = query.order_by(desc(Specialty.created_at))
        else:  # display_order (padrão)
            query = query.order_by(asc(Specialty.display_order))
        
        return query.offset(skip).limit(limit).all()
    
    async def update_specialty(
        self,
        specialty_id: str,
        specialty_data: SpecialtyUpdate,
        tenant_id: str
    ) -> Optional[Specialty]:
        """Atualiza uma especialidade"""
        specialty = await self.get_specialty(specialty_id, tenant_id)
        if not specialty:
            return None
        
        # Verificar se o novo nome já existe (se estiver sendo alterado)
        if specialty_data.name and specialty_data.name != specialty.name:
            existing = self.db.query(Specialty).filter(
                and_(
                    Specialty.tenant_id == tenant_id,
                    Specialty.name.ilike(specialty_data.name),
                    Specialty.id != specialty_id
                )
            ).first()
            
            if existing:
                raise ValueError(f"Já existe uma especialidade com o nome '{specialty_data.name}'")
        
        # Atualizar campos
        update_data = specialty_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(specialty, field, value)
        
        self.db.commit()
        self.db.refresh(specialty)
        
        return specialty
    
    async def delete_specialty(self, specialty_id: str, tenant_id: str) -> bool:
        """Remove uma especialidade (soft delete)"""
        specialty = await self.get_specialty(specialty_id, tenant_id)
        if not specialty:
            return False
        
        # Verificar se há processos vinculados (consulta direta na tabela de processos)
        # TODO: Implementar verificação quando a tabela de processos estiver disponível
        # from core.models.process import Process
        # linked_processes = self.db.query(Process).filter(Process.specialty_id == specialty_id).first()
        # if linked_processes:
        #     raise ValueError("Não é possível excluir uma especialidade que possui processos vinculados")
        
        # Soft delete - marcar como inativo
        specialty.is_active = False
        
        self.db.commit()
        return True
    
    async def activate_specialty(self, specialty_id: str, tenant_id: str) -> bool:
        """Reativa uma especialidade"""
        specialty = await self.get_specialty(specialty_id, tenant_id)
        if not specialty:
            return False
        
        specialty.is_active = True
        self.db.commit()
        return True
    
    async def get_specialty_stats(self, tenant_id: str) -> dict:
        """Retorna estatísticas das especialidades do tenant"""
        total = self.db.query(Specialty).filter(Specialty.tenant_id == tenant_id).count()
        active = self.db.query(Specialty).filter(
            and_(
                Specialty.tenant_id == tenant_id,
                Specialty.is_active == True
            )
        ).count()
        inactive = total - active
        
        with_oab = self.db.query(Specialty).filter(
            and_(
                Specialty.tenant_id == tenant_id,
                Specialty.requires_oab == True,
                Specialty.is_active == True  # Apenas ativas
            )
        ).count()
        
        with_experience = self.db.query(Specialty).filter(
            and_(
                Specialty.tenant_id == tenant_id,
                Specialty.min_experience_years.isnot(None),
                Specialty.is_active == True  # Apenas ativas
            )
        ).count()
        
        return {
            "total_specialties": total,
            "active_specialties": active,
            "inactive_specialties": inactive,
            "specialties_with_oab_requirement": with_oab,
            "specialties_with_experience_requirement": with_experience
        }
