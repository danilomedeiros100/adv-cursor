from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from core.models.user import User
from core.models.tenant_user import TenantUser
from apps.users.schemas import UserCreate, UserUpdate, TenantUserCreate, TenantUserUpdate
from core.models.user_roles import DEFAULT_ROLE_PERMISSIONS
import uuid
from typing import List, Optional, Dict, Any

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user_data: UserCreate, tenant_id: str) -> User:
        """Cria um novo usuário e associa ao tenant"""
        # Verificar se email já existe
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email já está em uso")
        
        # Criar usuário
        user = User(
            id=uuid.uuid4(),
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            birth_date=user_data.birth_date,
            cpf=user_data.cpf,
            oab_number=user_data.oab_number,
            oab_state=user_data.oab_state,
            position=user_data.position,
            department=user_data.department,
            is_active=user_data.is_active,
            preferences=user_data.preferences or {},
            timezone=user_data.timezone,
            language=user_data.language
        )
        
        # Definir senha
        user.set_password(user_data.password)
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Associar ao tenant
        await self._create_tenant_user(user.id, tenant_id, user_data.role)
        
        return user
    
    async def _create_tenant_user(self, user_id: str, tenant_id: str, role: str) -> TenantUser:
        """Cria associação entre usuário e tenant"""
        # Obter permissões padrão para o role
        default_permissions = DEFAULT_ROLE_PERMISSIONS.get(role, {})
        
        tenant_user = TenantUser(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            permissions=default_permissions,
            is_active=True
        )
        
        self.db.add(tenant_user)
        self.db.commit()
        self.db.refresh(tenant_user)
        
        return tenant_user
    
    async def get_user(self, user_id: str, tenant_id: str) -> Optional[User]:
        """Obtém um usuário específico do tenant"""
        user = self.db.query(User).join(TenantUser).filter(
            and_(
                User.id == user_id,
                TenantUser.tenant_id == tenant_id,
                TenantUser.is_active == True
            )
        ).first()
        
        if user:
            # Adicionar informações do tenant
            tenant_user = self.db.query(TenantUser).filter(
                and_(
                    TenantUser.user_id == user_id,
                    TenantUser.tenant_id == tenant_id
                )
            ).first()
            
            if tenant_user:
                user.role = tenant_user.role
                user.tenant_permissions = tenant_user.permissions
        
        return user
    
    async def list_users(
        self, 
        tenant_id: str, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        has_oab: Optional[bool] = None
    ) -> List[User]:
        """Lista usuários do tenant com filtros"""
        query = self.db.query(User).join(TenantUser).filter(
            and_(
                TenantUser.tenant_id == tenant_id,
                TenantUser.is_active == True
            )
        )
        
        # Aplicar filtros
        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.cpf.ilike(f"%{search}%"),
                User.oab_number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if role:
            query = query.filter(TenantUser.role == role)
        
        if department:
            query = query.filter(User.department == department)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if has_oab is not None:
            if has_oab:
                query = query.filter(User.oab_number.isnot(None))
            else:
                query = query.filter(User.oab_number.is_(None))
        
        users = query.offset(skip).limit(limit).all()
        
        # Adicionar informações do tenant para cada usuário
        for user in users:
            tenant_user = self.db.query(TenantUser).filter(
                and_(
                    TenantUser.user_id == user.id,
                    TenantUser.tenant_id == tenant_id
                )
            ).first()
            
            if tenant_user:
                user.role = tenant_user.role
                user.tenant_permissions = tenant_user.permissions
        
        return users
    
    async def update_user(self, user_id: str, user_data: UserUpdate, tenant_id: str) -> Optional[User]:
        """Atualiza um usuário"""
        user = await self.get_user(user_id, tenant_id)
        if not user:
            return None
        
        # Verificar se email já existe (se foi alterado)
        if user_data.email and user_data.email != user.email:
            existing_user = self.db.query(User).filter(
                and_(
                    User.email == user_data.email,
                    User.id != user_id
                )
            ).first()
            if existing_user:
                raise ValueError("Email já está em uso")
        
        # Atualizar campos
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        # Adicionar informações do tenant
        tenant_user = self.db.query(TenantUser).filter(
            and_(
                TenantUser.user_id == user_id,
                TenantUser.tenant_id == tenant_id
            )
        ).first()
        
        if tenant_user:
            user.role = tenant_user.role
            user.tenant_permissions = tenant_user.permissions
        
        return user
    
    async def update_user_role(self, user_id: str, tenant_id: str, role: str) -> Optional[User]:
        """Atualiza o role do usuário no tenant"""
        tenant_user = self.db.query(TenantUser).filter(
            and_(
                TenantUser.user_id == user_id,
                TenantUser.tenant_id == tenant_id
            )
        ).first()
        
        if not tenant_user:
            return None
        
        # Atualizar role e permissões
        tenant_user.role = role
        tenant_user.permissions = DEFAULT_ROLE_PERMISSIONS.get(role, {})
        
        self.db.commit()
        self.db.refresh(tenant_user)
        
        return await self.get_user(user_id, tenant_id)
    
    async def delete_user(self, user_id: str, tenant_id: str) -> bool:
        """Remove usuário do tenant (soft delete)"""
        tenant_user = self.db.query(TenantUser).filter(
            and_(
                TenantUser.user_id == user_id,
                TenantUser.tenant_id == tenant_id
            )
        ).first()
        
        if not tenant_user:
            return False
        
        # Soft delete - marcar como inativo
        tenant_user.is_active = False
        
        self.db.commit()
        return True
    
    async def activate_user(self, user_id: str, tenant_id: str) -> bool:
        """Reativa um usuário no tenant"""
        tenant_user = self.db.query(TenantUser).filter(
            and_(
                TenantUser.user_id == user_id,
                TenantUser.tenant_id == tenant_id
            )
        ).first()
        
        if not tenant_user:
            return False
        
        tenant_user.is_active = True
        
        self.db.commit()
        return True
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Altera senha do usuário"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Verificar senha atual
        if not user.verify_password(current_password):
            raise ValueError("Senha atual incorreta")
        
        # Definir nova senha
        user.set_password(new_password)
        
        self.db.commit()
        return True
    
    async def get_user_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Obtém estatísticas dos usuários do tenant"""
        total_users = self.db.query(TenantUser).filter(
            and_(
                TenantUser.tenant_id == tenant_id,
                TenantUser.is_active == True
            )
        ).count()
        
        active_users = self.db.query(TenantUser).join(User).filter(
            and_(
                TenantUser.tenant_id == tenant_id,
                TenantUser.is_active == True,
                User.is_active == True
            )
        ).count()
        
        # Contar por role
        role_counts = {}
        for role in ["admin", "lawyer", "assistant", "secretary", "receptionist", "user"]:
            count = self.db.query(TenantUser).filter(
                and_(
                    TenantUser.tenant_id == tenant_id,
                    TenantUser.role == role,
                    TenantUser.is_active == True
                )
            ).count()
            role_counts[role] = count
        
        # Contar advogados com OAB
        lawyers_with_oab = self.db.query(TenantUser).join(User).filter(
            and_(
                TenantUser.tenant_id == tenant_id,
                TenantUser.role == "lawyer",
                TenantUser.is_active == True,
                User.oab_number.isnot(None)
            )
        ).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "role_counts": role_counts,
            "lawyers_with_oab": lawyers_with_oab
        }
    
    async def get_departments(self, tenant_id: str) -> List[str]:
        """Obtém lista de departamentos do tenant"""
        departments = self.db.query(User.department).join(TenantUser).filter(
            and_(
                TenantUser.tenant_id == tenant_id,
                TenantUser.is_active == True,
                User.department.isnot(None)
            )
        ).distinct().all()
        
        return [dept[0] for dept in departments if dept[0]]

    # ==================== ESPECIALIDADES DOS USUÁRIOS ====================
    
    async def add_user_specialty(
        self, 
        user_id: str, 
        specialty_id: str, 
        expertise_level: str = "intermediate",
        years_experience: int = None,
        tenant_id: str = None
    ) -> bool:
        """Adiciona especialidade a um usuário"""
        from core.models.user_roles import UserSpecialty
        from core.models.specialty import Specialty
        
        # Verificar se o usuário existe e pertence ao tenant
        if tenant_id:
            tenant_user = self.db.query(TenantUser).filter(
                and_(
                    TenantUser.user_id == user_id,
                    TenantUser.tenant_id == tenant_id,
                    TenantUser.is_active == True
                )
            ).first()
            if not tenant_user:
                return False
        
        # Verificar se a especialidade existe
        specialty = self.db.query(Specialty).filter(Specialty.id == specialty_id).first()
        if not specialty:
            return False
        
        # Verificar se já existe a associação
        existing = self.db.query(UserSpecialty).filter(
            and_(
                UserSpecialty.user_id == user_id,
                UserSpecialty.specialty_id == specialty_id
            )
        ).first()
        
        if existing:
            raise ValueError("Usuário já possui esta especialidade")
        
        # Criar nova associação
        user_specialty = UserSpecialty(
            user_id=user_id,
            specialty_id=specialty_id,
            expertise_level=expertise_level,
            years_experience=years_experience
        )
        
        self.db.add(user_specialty)
        self.db.commit()
        return True
    
    async def get_user_specialties(self, user_id: str, tenant_id: str = None) -> List[Dict]:
        """Lista especialidades de um usuário"""
        from core.models.user_roles import UserSpecialty
        from core.models.specialty import Specialty
        
        # Verificar se o usuário pertence ao tenant
        if tenant_id:
            tenant_user = self.db.query(TenantUser).filter(
                and_(
                    TenantUser.user_id == user_id,
                    TenantUser.tenant_id == tenant_id,
                    TenantUser.is_active == True
                )
            ).first()
            if not tenant_user:
                return []
        
        # Buscar especialidades do usuário
        user_specialties = self.db.query(UserSpecialty).join(Specialty).filter(
            UserSpecialty.user_id == user_id
        ).all()
        
        return [
            {
                "id": str(us.id),
                "specialty_id": str(us.specialty_id),
                "specialty_name": us.specialty.name,
                "expertise_level": us.expertise_level,
                "years_experience": us.years_experience,
                "certifications": us.certifications,
                "created_at": us.created_at.isoformat()
            }
            for us in user_specialties
        ]
    
    async def remove_user_specialty(self, user_id: str, specialty_id: str, tenant_id: str = None) -> bool:
        """Remove especialidade de um usuário"""
        from core.models.user_roles import UserSpecialty
        
        # Verificar se o usuário pertence ao tenant
        if tenant_id:
            tenant_user = self.db.query(TenantUser).filter(
                and_(
                    TenantUser.user_id == user_id,
                    TenantUser.tenant_id == tenant_id,
                    TenantUser.is_active == True
                )
            ).first()
            if not tenant_user:
                return False
        
        # Buscar e remover a associação
        user_specialty = self.db.query(UserSpecialty).filter(
            and_(
                UserSpecialty.user_id == user_id,
                UserSpecialty.specialty_id == specialty_id
            )
        ).first()
        
        if not user_specialty:
            return False
        
        self.db.delete(user_specialty)
        self.db.commit()
        return True
    
    async def get_user_count(
        self, 
        tenant_id: str, 
        search: Optional[str] = None,
        role: Optional[str] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        has_oab: Optional[bool] = None
    ) -> int:
        """Conta usuários do tenant com filtros"""
        query = self.db.query(User).join(TenantUser).filter(
            and_(
                TenantUser.tenant_id == tenant_id,
                TenantUser.is_active == True
            )
        )
        
        # Aplicar filtros
        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.cpf.ilike(f"%{search}%"),
                User.oab_number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if role:
            query = query.filter(TenantUser.role == role)
        
        if department:
            query = query.filter(User.department == department)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if has_oab is not None:
            if has_oab:
                query = query.filter(User.oab_number.isnot(None))
            else:
                query = query.filter(User.oab_number.is_(None))
        
        return query.count()