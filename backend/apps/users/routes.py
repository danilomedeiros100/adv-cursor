from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth.multi_tenant_auth import MultiTenantAuth, require_permission
from apps.users.schemas import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, 
    TenantUserCreate, TenantUserUpdate, TenantUserResponse,
    UserPasswordUpdate, UserFilters
)
from apps.users.services import UserService
from apps.users.schemas import UserRole

router = APIRouter(prefix="/users", tags=["Usuários"])

# Instância do sistema de autenticação
auth = MultiTenantAuth()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Cria um novo usuário (isolado por empresa)"""
    # Verifica permissão
    if not current_user_data["permissions"].get("users.create", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar usuários"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    try:
        user = await service.create_user(user_data, str(tenant_id))
        return user.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {str(e)}"
        )

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    has_oab: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Lista usuários da empresa (isolado automaticamente)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.read", False) or permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para visualizar usuários"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    try:
        users = await service.list_users(
            str(tenant_id),
            skip=skip,
            limit=limit,
            search=search,
            role=role,
            department=department,
            is_active=is_active,
            has_oab=has_oab
        )
        
        return [user.to_dict() for user in users]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar usuários: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Obtém usuário específico (isolado por empresa)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.read", False) or permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para visualizar usuários"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    user = await service.get_user(user_id, str(tenant_id))
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return user.to_dict()

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Atualiza usuário (isolado por empresa)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.update", False) or permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar usuários"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    try:
        user = await service.update_user(user_id, user_data, str(tenant_id))
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        return user.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar usuário: {str(e)}"
        )

@router.put("/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: UserRole,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Atualiza role do usuário"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para gerenciar usuários"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    try:
        user = await service.update_user_role(user_id, str(tenant_id), role.value)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        return {"message": "Role atualizado com sucesso", "user": user.to_dict()}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar role: {str(e)}"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Remove usuário (soft delete, isolado por empresa)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.delete", False) or permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para deletar usuários"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    success = await service.delete_user(user_id, str(tenant_id))
    if not success:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {"message": "Usuário removido com sucesso"}

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Reativa um usuário"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para gerenciar usuários"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    success = await service.activate_user(user_id, str(tenant_id))
    if not success:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {"message": "Usuário reativado com sucesso"}

@router.post("/{user_id}/change-password")
async def change_password(
    user_id: str,
    password_data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Altera senha do usuário"""
    # Verifica se é o próprio usuário ou tem permissão de gerenciamento
    current_user_id = str(current_user_data["user"].id)
    permissions = current_user_data["permissions"]
    
    if user_id != current_user_id and not permissions.get("users.manage", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para alterar senha de outros usuários"
        )
    
    service = UserService(db)
    
    try:
        success = await service.change_password(
            user_id, 
            password_data.current_password, 
            password_data.new_password
        )
        if not success:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        return {"message": "Senha alterada com sucesso"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar senha: {str(e)}"
        )

@router.get("/stats/summary")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Obtém estatísticas dos usuários"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.read", False) or permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para visualizar estatísticas"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    try:
        stats = await service.get_user_stats(str(tenant_id))
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

@router.get("/departments/list")
async def get_departments(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Obtém lista de departamentos"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.read", False) or permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para visualizar departamentos"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    try:
        departments = await service.get_departments(str(tenant_id))
        return {"departments": departments}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter departamentos: {str(e)}"
        )

# ==================== ESPECIALIDADES DOS USUÁRIOS ====================

@router.post("/{user_id}/specialties")
async def add_user_specialty(
    user_id: str,
    specialty_data: dict,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Adiciona especialidade a um usuário"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.update", False) or permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para gerenciar especialidades"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    try:
        result = await service.add_user_specialty(
            user_id, 
            specialty_data["specialty_id"],
            specialty_data.get("expertise_level", "intermediate"),
            specialty_data.get("years_experience"),
            str(tenant_id)
        )
        if not result:
            raise HTTPException(status_code=404, detail="Usuário ou especialidade não encontrado")
        
        return {"message": "Especialidade adicionada com sucesso"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar especialidade: {str(e)}"
        )

@router.get("/{user_id}/specialties")
async def get_user_specialties(
    user_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Lista especialidades de um usuário"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.read", False) or permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para visualizar especialidades"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    try:
        specialties = await service.get_user_specialties(user_id, str(tenant_id))
        return {"specialties": specialties}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter especialidades: {str(e)}"
        )

@router.delete("/{user_id}/specialties/{specialty_id}")
async def remove_user_specialty(
    user_id: str,
    specialty_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Remove especialidade de um usuário"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("users.update", False) or permissions.get("users.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para gerenciar especialidades"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = UserService(db)
    
    try:
        success = await service.remove_user_specialty(user_id, specialty_id, str(tenant_id))
        if not success:
            raise HTTPException(status_code=404, detail="Usuário ou especialidade não encontrado")
        
        return {"message": "Especialidade removida com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover especialidade: {str(e)}"
        )

# Endpoints de teste
@router.get("/test")
async def test_users_endpoint(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Endpoint de teste para users"""
    try:
        return {
            "message": "Endpoint de users funcionando!",
            "user": current_user_data["user"].name,
            "tenant": current_user_data["tenant"].name,
            "permissions": current_user_data["permissions"]
        }
    except Exception as e:
        return {
            "message": "Erro no endpoint de users",
            "error": str(e)
        }
