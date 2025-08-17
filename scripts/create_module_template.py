#!/usr/bin/env python3
"""
Script para criar novos módulos seguindo o padrão definido em PADRAO_MODULOS.md

Uso:
    python scripts/create_module_template.py --module-name "products" --module-title "Produtos"
"""

import os
import argparse
import re
from pathlib import Path

def to_camel_case(snake_str):
    """Converte snake_case para CamelCase"""
    components = snake_str.split('_')
    return ''.join(word.capitalize() for word in components)

def to_pascal_case(snake_str):
    """Converte snake_case para PascalCase"""
    return to_camel_case(snake_str)

def create_module_structure(module_name: str, module_title: str):
    """Cria a estrutura completa de um novo módulo"""
    
    # Converter nomes
    module_name_snake = module_name.lower().replace(' ', '_')
    module_name_camel = to_camel_case(module_name_snake)
    module_name_pascal = to_pascal_case(module_name_snake)
    
    print(f"🚀 Criando módulo: {module_title}")
    print(f"📁 Nome do módulo: {module_name_snake}")
    print(f"🔤 CamelCase: {module_name_camel}")
    print(f"🔤 PascalCase: {module_name_pascal}")
    
    # Estrutura de diretórios
    backend_dir = Path("backend/apps") / module_name_snake
    frontend_types_dir = Path("saas-juridico-frontend/src/types")
    frontend_hooks_dir = Path("saas-juridico-frontend/src/hooks")
    frontend_pages_dir = Path("saas-juridico-frontend/src/app/company") / module_name_snake
    
    # Criar diretórios
    backend_dir.mkdir(parents=True, exist_ok=True)
    frontend_pages_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== BACKEND ====================
    
    # 1. __init__.py
    init_content = f'''"""
{module_title} - Módulo de gestão de {module_name_snake}
"""

from .routes import router
from .schemas import *
from .services import *

__all__ = ["router"]
'''
    
    with open(backend_dir / "__init__.py", "w", encoding="utf-8") as f:
        f.write(init_content)
    
    # 2. schemas.py
    schemas_content = f'''from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class {module_name_pascal}Create(BaseModel):
    """Schema para criação de {module_name_snake}"""
    name: str
    description: Optional[str] = None
    is_active: bool = True
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Nome é obrigatório")
        if len(v) > 255:
            raise ValueError("Nome deve ter no máximo 255 caracteres")
        return v.strip()

class {module_name_pascal}Update(BaseModel):
    """Schema para atualização de {module_name_snake}"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Nome não pode estar vazio")
            if len(v) > 255:
                raise ValueError("Nome deve ter no máximo 255 caracteres")
            return v.strip()
        return v

class {module_name_pascal}Response(BaseModel):
    """Schema para resposta de {module_name_snake}"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

class {module_name_pascal}ListResponse(BaseModel):
    """Schema para resposta de lista de {module_name_snake}s"""
    {module_name_snake}s: List[{module_name_pascal}Response]
    total: int
    page: int
    per_page: int
    total_pages: int

class {module_name_pascal}Stats(BaseModel):
    """Schema para estatísticas de {module_name_snake}s"""
    total_{module_name_snake}s: int
    active_{module_name_snake}s: int
    inactive_{module_name_snake}s: int
'''
    
    with open(backend_dir / "schemas.py", "w", encoding="utf-8") as f:
        f.write(schemas_content)
    
    # 3. services.py
    services_content = f'''from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from core.models.{module_name_snake} import {module_name_pascal}
from apps.{module_name_snake}.schemas import {module_name_pascal}Create, {module_name_pascal}Update
import uuid

class {module_name_pascal}Service:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_{module_name_snake}(self, {module_name_snake}_data: {module_name_pascal}Create, tenant_id: str) -> {module_name_pascal}:
        """Cria um novo {module_name_snake} para o tenant"""
        # Verificar duplicatas se necessário
        existing = self.db.query({module_name_pascal}).filter(
            and_(
                {module_name_pascal}.tenant_id == tenant_id,
                {module_name_pascal}.name.ilike({module_name_snake}_data.name)
            )
        ).first()
        
        if existing:
            raise ValueError(f"Já existe um {module_name_snake} com o nome '{{module_name_snake}_data.name}}'")
        
        # Criar novo {module_name_snake}
        {module_name_snake} = {module_name_pascal}(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name={module_name_snake}_data.name,
            description={module_name_snake}_data.description,
            is_active={module_name_snake}_data.is_active
        )
        
        self.db.add({module_name_snake})
        self.db.commit()
        self.db.refresh({module_name_snake})
        
        return {module_name_snake}
    
    async def get_{module_name_snake}(self, {module_name_snake}_id: str, tenant_id: str) -> Optional[{module_name_pascal}]:
        """Busca um {module_name_snake} específico do tenant"""
        return self.db.query({module_name_pascal}).filter(
            and_(
                {module_name_pascal}.id == {module_name_snake}_id,
                {module_name_pascal}.tenant_id == tenant_id
            )
        ).first()
    
    async def list_{module_name_snake}s(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        order_by: str = "name"
    ) -> List[{module_name_pascal}]:
        """Lista {module_name_snake}s do tenant com filtros"""
        query = self.db.query({module_name_pascal}).filter({module_name_pascal}.tenant_id == tenant_id)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    {module_name_pascal}.name.ilike(f"%{{search}}%"),
                    {module_name_pascal}.description.ilike(f"%{{search}}%")
                )
            )
        
        if is_active is not None:
            query = query.filter({module_name_pascal}.is_active == is_active)
        
        # Aplicar ordenação
        if order_by == "name":
            query = query.order_by(asc({module_name_pascal}.name))
        elif order_by == "created_at":
            query = query.order_by(desc({module_name_pascal}.created_at))
        else:
            query = query.order_by(asc({module_name_pascal}.name))
        
        return query.offset(skip).limit(limit).all()
    
    async def update_{module_name_snake}(
        self,
        {module_name_snake}_id: str,
        {module_name_snake}_data: {module_name_pascal}Update,
        tenant_id: str
    ) -> Optional[{module_name_pascal}]:
        """Atualiza um {module_name_snake}"""
        {module_name_snake} = await self.get_{module_name_snake}({module_name_snake}_id, tenant_id)
        if not {module_name_snake}:
            return None
        
        # Verificar duplicatas se nome foi alterado
        if {module_name_snake}_data.name and {module_name_snake}_data.name != {module_name_snake}.name:
            existing = self.db.query({module_name_pascal}).filter(
                and_(
                    {module_name_pascal}.tenant_id == tenant_id,
                    {module_name_pascal}.name.ilike({module_name_snake}_data.name),
                    {module_name_pascal}.id != {module_name_snake}_id
                )
            ).first()
            
            if existing:
                raise ValueError(f"Já existe um {module_name_snake} com o nome '{{module_name_snake}_data.name}}'")
        
        # Atualizar campos
        update_data = {module_name_snake}_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr({module_name_snake}, field, value)
        
        self.db.commit()
        self.db.refresh({module_name_snake})
        
        return {module_name_snake}
    
    async def delete_{module_name_snake}(self, {module_name_snake}_id: str, tenant_id: str) -> bool:
        """Remove um {module_name_snake} (soft delete)"""
        {module_name_snake} = await self.get_{module_name_snake}({module_name_snake}_id, tenant_id)
        if not {module_name_snake}:
            return False
        
        # Soft delete
        {module_name_snake}.is_active = False
        self.db.commit()
        return True
    
    async def activate_{module_name_snake}(self, {module_name_snake}_id: str, tenant_id: str) -> bool:
        """Reativa um {module_name_snake}"""
        {module_name_snake} = await self.get_{module_name_snake}({module_name_snake}_id, tenant_id)
        if not {module_name_snake}:
            return False
        
        {module_name_snake}.is_active = True
        self.db.commit()
        return True
    
    async def get_{module_name_snake}_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Retorna estatísticas dos {module_name_snake}s do tenant"""
        total = self.db.query({module_name_pascal}).filter({module_name_pascal}.tenant_id == tenant_id).count()
        active = self.db.query({module_name_pascal}).filter(
            and_(
                {module_name_pascal}.tenant_id == tenant_id,
                {module_name_pascal}.is_active == True
            )
        ).count()
        inactive = total - active
        
        return {{
            "total_{module_name_snake}s": total,
            "active_{module_name_snake}s": active,
            "inactive_{module_name_snake}s": inactive
        }}
'''
    
    with open(backend_dir / "services.py", "w", encoding="utf-8") as f:
        f.write(services_content)
    
    # 4. routes.py
    routes_content = f'''from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth.multi_tenant_auth import MultiTenantAuth
from apps.{module_name_snake}.schemas import (
    {module_name_pascal}Create, {module_name_pascal}Update, {module_name_pascal}Response,
    {module_name_pascal}ListResponse, {module_name_pascal}Stats
)
from apps.{module_name_snake}.services import {module_name_pascal}Service

router = APIRouter(prefix="/{module_name_snake}s", tags=["{module_title}"])

# Instância do sistema de autenticação
auth = MultiTenantAuth()

# ==================== CRUD BÁSICO ====================

@router.post("/", response_model={module_name_pascal}Response)
async def create_{module_name_snake}(
    {module_name_snake}_data: {module_name_pascal}Create,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Cria um novo {module_name_snake} (isolado por empresa)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name_snake}s.create", False) or permissions.get("{module_name_snake}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para criar {module_name_snake}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {module_name_pascal}Service(db)
    
    try:
        {module_name_snake} = await service.create_{module_name_snake}({module_name_snake}_data, str(tenant_id))
        return {module_name_snake}.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar {module_name_snake}: {{str(e)}}"
        )

@router.get("/", response_model=List[{module_name_pascal}Response])
async def list_{module_name_snake}s(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    order_by: str = Query("name", regex="^(name|created_at)$"),
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Lista {module_name_snake}s da empresa (isolado automaticamente)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name_snake}s.read", False) or permissions.get("{module_name_snake}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para visualizar {module_name_snake}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {module_name_pascal}Service(db)
    
    try:
        {module_name_snake}s = await service.list_{module_name_snake}s(
            str(tenant_id),
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            order_by=order_by
        )
        
        return [{module_name_snake}.to_dict() for {module_name_snake} in {module_name_snake}s]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar {module_name_snake}s: {{str(e)}}"
        )

@router.get("/{{module_name_snake}_id}}", response_model={module_name_pascal}Response)
async def get_{module_name_snake}(
    {module_name_snake}_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Obtém {module_name_snake} específico (isolado por empresa)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name_snake}s.read", False) or permissions.get("{module_name_snake}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para visualizar {module_name_snake}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {module_name_pascal}Service(db)
    
    {module_name_snake} = await service.get_{module_name_snake}({module_name_snake}_id, str(tenant_id))
    if not {module_name_snake}:
        raise HTTPException(status_code=404, detail=f"{module_name_pascal} não encontrado")
    
    return {module_name_snake}.to_dict()

@router.put("/{{module_name_snake}_id}}", response_model={module_name_pascal}Response)
async def update_{module_name_snake}(
    {module_name_snake}_id: str,
    {module_name_snake}_data: {module_name_pascal}Update,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Atualiza {module_name_snake} (isolado por empresa)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name_snake}s.update", False) or permissions.get("{module_name_snake}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para atualizar {module_name_snake}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {module_name_pascal}Service(db)
    
    try:
        {module_name_snake} = await service.update_{module_name_snake}({module_name_snake}_id, {module_name_snake}_data, str(tenant_id))
        if not {module_name_snake}:
            raise HTTPException(status_code=404, detail=f"{module_name_pascal} não encontrado")
        
        return {module_name_snake}.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar {module_name_snake}: {{str(e)}}"
        )

@router.delete("/{{module_name_snake}_id}}")
async def delete_{module_name_snake}(
    {module_name_snake}_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Remove {module_name_snake} (soft delete, isolado por empresa)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name_snake}s.delete", False) or permissions.get("{module_name_snake}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para deletar {module_name_snake}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {module_name_pascal}Service(db)
    
    try:
        success = await service.delete_{module_name_snake}({module_name_snake}_id, str(tenant_id))
        if not success:
            raise HTTPException(status_code=404, detail=f"{module_name_pascal} não encontrado")
        
        return {{"message": f"{module_name_pascal} removido com sucesso"}}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar {module_name_snake}: {{str(e)}}"
        )

@router.post("/{{module_name_snake}_id}}/activate")
async def activate_{module_name_snake}(
    {module_name_snake}_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Reativa um {module_name_snake}"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name_snake}s.update", False) or permissions.get("{module_name_snake}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para reativar {module_name_snake}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {module_name_pascal}Service(db)
    
    success = await service.activate_{module_name_snake}({module_name_snake}_id, str(tenant_id))
    if not success:
        raise HTTPException(status_code=404, detail=f"{module_name_pascal} não encontrado")
    
    return {{"message": f"{module_name_pascal} reativado com sucesso"}}

# ==================== ESTATÍSTICAS ====================

@router.get("/stats/summary", response_model={module_name_pascal}Stats)
async def get_{module_name_snake}_stats(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Retorna estatísticas dos {module_name_snake}s"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name_snake}s.read", False) or permissions.get("{module_name_snake}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para visualizar estatísticas"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {module_name_pascal}Service(db)
    
    try:
        stats = await service.get_{module_name_snake}_stats(str(tenant_id))
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {{str(e)}}"
        )
'''
    
    with open(backend_dir / "routes.py", "w", encoding="utf-8") as f:
        f.write(routes_content)
    
    # ==================== FRONTEND ====================
    
    # 1. Tipos TypeScript
    types_content = f'''export interface {module_name_pascal} {{
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}}

export interface Create{module_name_pascal}Data {{
  name: string;
  description?: string;
  is_active?: boolean;
}}

export interface Update{module_name_pascal}Data extends Partial<Create{module_name_pascal}Data> {{}}

export interface {module_name_pascal}Stats {{
  total_{module_name_snake}s: number;
  active_{module_name_snake}s: number;
  inactive_{module_name_snake}s: number;
}}
'''
    
    with open(frontend_types_dir / f"{module_name_snake}.ts", "w", encoding="utf-8") as f:
        f.write(types_content)
    
    # 2. Hook customizado
    hook_content = f'''import {{ useState, useEffect }} from "react";
import {{ useAuth }} from "./useAuth";
import {{ toast }} from "sonner";
import {{ {module_name_pascal}, Create{module_name_pascal}Data, Update{module_name_pascal}Data }} from "@/types/{module_name_snake}";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export function use{module_name_pascal}s() {{
  const {{ token }} = useAuth();
  const [{module_name_snake}s, set{module_name_pascal}s] = useState<{module_name_pascal}[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Buscar todos os {module_name_snake}s
  const fetch{module_name_pascal}s = async () => {{
    if (!token) return;

    try {{
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${{API_BASE_URL}}/company/{module_name_snake}s`, {{
        headers: {{
          "Authorization": `Bearer ${{token}}`,
          "Content-Type": "application/json",
        }},
      }});

      if (!response.ok) {{
        throw new Error(`Erro ao buscar {module_name_snake}s`);
      }}

      const data = await response.json();
      set{module_name_pascal}s(data || []);
    }} catch (error) {{
      console.error(`Erro ao buscar {module_name_snake}s:`, error);
      setError(`Erro ao carregar {module_name_snake}s`);
      toast.error(`Erro ao carregar {module_name_snake}s`);
    }} finally {{
      setLoading(false);
    }}
  }};

  // Criar novo {module_name_snake}
  const create{module_name_pascal} = async ({module_name_snake}Data: Create{module_name_pascal}Data): Promise<{module_name_pascal} | null> => {{
    if (!token) return null;

    try {{
      setLoading(true);
      setError(null);

      const response = await fetch(`${{API_BASE_URL}}/company/{module_name_snake}s`, {{
        method: "POST",
        headers: {{
          "Authorization": `Bearer ${{token}}`,
          "Content-Type": "application/json",
        }},
        body: JSON.stringify({module_name_snake}Data),
      }});

      if (!response.ok) {{
        const errorData = await response.json().catch(() => ({{}}));
        throw new Error(errorData.detail || `Erro ao criar {module_name_snake}`);
      }}

      const new{module_name_pascal} = await response.json();
      set{module_name_pascal}s(prev => [...prev, new{module_name_pascal}]);
      toast.success(`{module_name_pascal} criado com sucesso`);
      return new{module_name_pascal};
    }} catch (error) {{
      console.error(`Erro ao criar {module_name_snake}:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao criar {module_name_snake}`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    }} finally {{
      setLoading(false);
    }}
  }};

  // Atualizar {module_name_snake}
  const update{module_name_pascal} = async ({module_name_snake}Id: string, {module_name_snake}Data: Update{module_name_pascal}Data): Promise<{module_name_pascal} | null> => {{
    if (!token) return null;

    try {{
      setLoading(true);
      setError(null);

      const response = await fetch(`${{API_BASE_URL}}/company/{module_name_snake}s/${{module_name_snake}Id}}`, {{
        method: "PUT",
        headers: {{
          "Authorization": `Bearer ${{token}}`,
          "Content-Type": "application/json",
        }},
        body: JSON.stringify({module_name_snake}Data),
      }});

      if (!response.ok) {{
        const errorData = await response.json().catch(() => ({{}}));
        throw new Error(errorData.detail || `Erro ao atualizar {module_name_snake}`);
      }}

      const updated{module_name_pascal} = await response.json();
      set{module_name_pascal}s(prev => prev.map({module_name_snake} => 
        {module_name_snake}.id === {module_name_snake}Id ? updated{module_name_pascal} : {module_name_snake}
      ));
      toast.success(`{module_name_pascal} atualizado com sucesso`);
      return updated{module_name_pascal};
    }} catch (error) {{
      console.error(`Erro ao atualizar {module_name_snake}:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao atualizar {module_name_snake}`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    }} finally {{
      setLoading(false);
    }}
  }};

  // Deletar {module_name_snake}
  const delete{module_name_pascal} = async ({module_name_snake}Id: string): Promise<boolean> => {{
    if (!token) return false;

    try {{
      setLoading(true);
      setError(null);

      const response = await fetch(`${{API_BASE_URL}}/company/{module_name_snake}s/${{module_name_snake}Id}}`, {{
        method: "DELETE",
        headers: {{
          "Authorization": `Bearer ${{token}}`,
          "Content-Type": "application/json",
        }},
      }});

      if (!response.ok) {{
        const errorData = await response.json().catch(() => ({{}}));
        throw new Error(errorData.detail || `Erro ao deletar {module_name_snake}`);
      }}

      set{module_name_pascal}s(prev => prev.filter({module_name_snake} => {module_name_snake}.id !== {module_name_snake}Id));
      toast.success(`{module_name_pascal} deletado com sucesso`);
      return true;
    }} catch (error) {{
      console.error(`Erro ao deletar {module_name_snake}:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao deletar {module_name_snake}`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    }} finally {{
      setLoading(false);
    }}
  }};

  // Buscar {module_name_snake} específico
  const get{module_name_pascal} = async ({module_name_snake}Id: string): Promise<{module_name_pascal} | null> => {{
    if (!token) return null;

    try {{
      setLoading(true);
      setError(null);

      const response = await fetch(`${{API_BASE_URL}}/company/{module_name_snake}s/${{module_name_snake}Id}}`, {{
        headers: {{
          "Authorization": `Bearer ${{token}}`,
          "Content-Type": "application/json",
        }},
      }});

      if (!response.ok) {{
        throw new Error(`{module_name_pascal} não encontrado`);
      }}

      const {module_name_snake} = await response.json();
      return {module_name_snake};
    }} catch (error) {{
      console.error(`Erro ao buscar {module_name_snake}:`, error);
      setError(`Erro ao buscar {module_name_snake}`);
      return null;
    }} finally {{
      setLoading(false);
    }}
  }};

  // Filtrar {module_name_snake}s
  const filter{module_name_pascal}s = (searchTerm: string) => {{
    return {module_name_snake}s.filter({module_name_snake} =>
      {module_name_snake}.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ({module_name_snake}.description && {module_name_snake}.description.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }};

  // Carregar {module_name_snake}s na inicialização
  useEffect(() => {{
    if (token) {{
      fetch{module_name_pascal}s();
    }}
  }}, [token]);

  return {{
    {module_name_snake}s,
    loading,
    error,
    fetch{module_name_pascal}s,
    create{module_name_pascal},
    update{module_name_pascal},
    delete{module_name_pascal},
    get{module_name_pascal},
    filter{module_name_pascal}s,
  }};
}}
'''
    
    with open(frontend_hooks_dir / f"use{module_name_pascal}.ts", "w", encoding="utf-8") as f:
        f.write(hook_content)
    
    # 3. Página básica
    page_content = f'''import {{ Card, CardContent, CardHeader, CardTitle }} from "@/components/ui/card";
import {{ Button }} from "@/components/ui/button";
import {{ use{module_name_pascal}s }} from "@/hooks/use{module_name_pascal}";

export default function {module_name_pascal}Page() {{
  const {{ {module_name_snake}s, loading, error }} = use{module_name_pascal}s();

  if (loading) {{
    return (
      <div className="flex items-center justify-center h-64">
        <p>Carregando {module_name_snake}s...</p>
      </div>
    );
  }}

  if (error) {{
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-red-500">Erro: {{error}}</p>
      </div>
    );
  }}

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">{module_title}</h1>
        <Button>Novo {module_name_snake}</Button>
      </div>

      <div className="grid gap-4">
        {{module_name_snake}s.map(({module_name_snake}) => (
          <Card key={{module_name_snake}.id}}>
            <CardHeader>
              <CardTitle>{{module_name_snake}.name}}</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{{module_name_snake}.description || "Sem descrição"}}</p>
              <p className="text-sm text-gray-500">
                Status: {{module_name_snake}.is_active ? "Ativo" : "Inativo"}}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {{module_name_snake}s.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">Nenhum {module_name_snake} encontrado</p>
        </div>
      )}
    </div>
  );
}}
'''
    
    with open(frontend_pages_dir / "page.tsx", "w", encoding="utf-8") as f:
        f.write(page_content)
    
    # ==================== INSTRUÇÕES ====================
    
    print("\n✅ Módulo criado com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Criar o modelo SQLAlchemy em core/models/")
    print("2. Adicionar o router no main.py")
    print("3. Criar migration para a nova tabela")
    print("4. Implementar funcionalidades específicas")
    print("5. Adicionar permissões no sistema de roles")
    print("6. Testar a integração")
    
    print(f"\n📁 Arquivos criados:")
    print(f"   Backend:")
    print(f"   - {backend_dir}/__init__.py")
    print(f"   - {backend_dir}/schemas.py")
    print(f"   - {backend_dir}/services.py")
    print(f"   - {backend_dir}/routes.py")
    print(f"   Frontend:")
    print(f"   - {frontend_types_dir}/{module_name_snake}.ts")
    print(f"   - {frontend_hooks_dir}/use{module_name_pascal}.ts")
    print(f"   - {frontend_pages_dir}/page.tsx")
    
    print(f"\n🔗 Endpoints criados:")
    print(f"   POST   /api/v1/company/{module_name_snake}s/")
    print(f"   GET    /api/v1/company/{module_name_snake}s/")
    print(f"   GET    /api/v1/company/{module_name_snake}s/{{id}}")
    print(f"   PUT    /api/v1/company/{module_name_snake}s/{{id}}")
    print(f"   DELETE /api/v1/company/{module_name_snake}s/{{id}}")
    print(f"   POST   /api/v1/company/{module_name_snake}s/{{id}}/activate")
    print(f"   GET    /api/v1/company/{module_name_snake}s/stats/summary")

def main():
    parser = argparse.ArgumentParser(description="Criar novo módulo seguindo o padrão")
    parser.add_argument("--module-name", required=True, help="Nome do módulo (ex: products)")
    parser.add_argument("--module-title", required=True, help="Título do módulo (ex: Produtos)")
    
    args = parser.parse_args()
    
    create_module_structure(args.module_name, args.module_title)

if __name__ == "__main__":
    main()
