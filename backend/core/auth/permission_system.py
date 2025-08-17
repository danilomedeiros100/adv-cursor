from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from core.database import get_db
from core.models.user_roles import Role, UserRole, DEFAULT_ROLE_PERMISSIONS
from core.models.tenant_user import TenantUser
from core.auth.multi_tenant_auth import get_current_user

class PermissionSystem:
    """Sistema de permissões personalizadas por usuário"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_permissions(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Obtém permissões completas do usuário (role + personalizadas)"""
        # Busca role do usuário no tenant
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.user_id == user_id,
            TenantUser.tenant_id == tenant_id,
            TenantUser.is_active == True
        ).first()
        
        if not tenant_user:
            return {}
        
        # Busca role base
        role = self.db.query(Role).filter(Role.id == tenant_user.role).first()
        if not role:
            return {}
        
        # Busca permissões personalizadas
        user_role = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role.id
        ).first()
        
        # Combina permissões padrão com personalizadas
        base_permissions = DEFAULT_ROLE_PERMISSIONS.get(role.name, {})
        custom_permissions = user_role.custom_permissions if user_role else {}
        
        # Merge das permissões (custom sobrescreve base)
        final_permissions = self._merge_permissions(base_permissions, custom_permissions)
        
        # Adiciona configurações específicas do usuário
        if user_role:
            final_permissions.update({
                "can_manage_users": user_role.can_manage_users if user_role.can_manage_users is not None else base_permissions.get("can_manage_users", False),
                "can_manage_financial": user_role.can_manage_financial if user_role.can_manage_financial is not None else base_permissions.get("can_manage_financial", False),
                "can_view_all_processes": user_role.can_view_all_processes if user_role.can_view_all_processes is not None else base_permissions.get("can_view_all_processes", False),
                "can_manage_specialties": user_role.can_manage_specialties if user_role.can_manage_specialties is not None else base_permissions.get("can_manage_specialties", False),
                "allowed_modules": user_role.allowed_modules if user_role.allowed_modules else base_permissions.get("modules", [])
            })
        
        return final_permissions
    
    def _merge_permissions(self, base: Dict, custom: Dict) -> Dict:
        """Merge de permissões base com personalizadas"""
        result = base.copy()
        
        for module, permissions in custom.items():
            if module in result:
                if isinstance(permissions, dict) and isinstance(result[module], dict):
                    result[module].update(permissions)
                else:
                    result[module] = permissions
            else:
                result[module] = permissions
        
        return result
    
    def has_permission(self, user_permissions: Dict, module: str, action: str) -> bool:
        """Verifica se usuário tem permissão específica"""
        if "*" in user_permissions.get("modules", []):
            return True
        
        if module not in user_permissions.get("modules", []):
            return False
        
        module_permissions = user_permissions.get("permissions", {}).get(module, {})
        return module_permissions.get(action, False)
    
    def can_access_module(self, user_permissions: Dict, module: str) -> bool:
        """Verifica se usuário pode acessar módulo"""
        allowed_modules = user_permissions.get("modules", [])
        return "*" in allowed_modules or module in allowed_modules
    
    def get_user_modules(self, user_permissions: Dict) -> List[str]:
        """Retorna lista de módulos que usuário pode acessar"""
        modules = user_permissions.get("modules", [])
        if "*" in modules:
            return ["clients", "processes", "documents", "financial", "reports", "users", "specialties", "settings", "tasks", "communications"]
        return modules

# Decorators para verificação de permissões
def require_permission(module: str, action: str):
    """Decorator para verificar permissão específica"""
    def permission_checker(current_user_data: Dict = Depends(get_current_user)):
        db = next(get_db())
        permission_system = PermissionSystem(db)
        
        user_permissions = permission_system.get_user_permissions(
            current_user_data["user"].id,
            current_user_data["tenant"].id
        )
        
        if not permission_system.has_permission(user_permissions, module, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sem permissão para {action} em {module}"
            )
        
        return current_user_data
    return permission_checker

def require_module_access(module: str):
    """Decorator para verificar acesso ao módulo"""
    def module_checker(current_user_data: Dict = Depends(get_current_user)):
        db = next(get_db())
        permission_system = PermissionSystem(db)
        
        user_permissions = permission_system.get_user_permissions(
            current_user_data["user"].id,
            current_user_data["tenant"].id
        )
        
        if not permission_system.can_access_module(user_permissions, module):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sem acesso ao módulo {module}"
            )
        
        return current_user_data
    return module_checker

def require_admin_access():
    """Decorator para verificar se é admin"""
    def admin_checker(current_user_data: Dict = Depends(get_current_user)):
        db = next(get_db())
        permission_system = PermissionSystem(db)
        
        user_permissions = permission_system.get_user_permissions(
            current_user_data["user"].id,
            current_user_data["tenant"].id
        )
        
        if not user_permissions.get("can_manage_users", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso de administrador necessário"
            )
        
        return current_user_data
    return admin_checker

def require_financial_access():
    """Decorator para verificar acesso financeiro"""
    def financial_checker(current_user_data: Dict = Depends(get_current_user)):
        db = next(get_db())
        permission_system = PermissionSystem(db)
        
        user_permissions = permission_system.get_user_permissions(
            current_user_data["user"].id,
            current_user_data["tenant"].id
        )
        
        if not user_permissions.get("can_manage_financial", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso financeiro necessário"
            )
        
        return current_user_data
    return financial_checker

# Função utilitária para obter permissões do usuário atual
async def get_current_user_permissions(
    current_user_data: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Obtém permissões do usuário atual"""
    permission_system = PermissionSystem(db)
    return permission_system.get_user_permissions(
        current_user_data["user"].id,
        current_user_data["tenant"].id
    )

# Exemplo de uso em rotas
"""
@router.get("/clients")
async def list_clients(
    current_user_data: Dict = Depends(require_permission("clients", "read"))
):
    # Usuário tem permissão de leitura em clientes
    pass

@router.post("/processes")
async def create_process(
    current_user_data: Dict = Depends(require_permission("processes", "create"))
):
    # Usuário tem permissão de criação em processos
    pass

@router.get("/financial/reports")
async def get_financial_reports(
    current_user_data: Dict = Depends(require_financial_access())
):
    # Usuário tem acesso financeiro
    pass
"""
