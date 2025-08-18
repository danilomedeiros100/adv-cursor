# 📋 Padrão de Módulos - SaaS Jurídico

## 🎯 Objetivo

Este documento define o **padrão padrão** para todos os módulos do sistema, garantindo consistência, manutenibilidade e escalabilidade. Todos os novos módulos devem seguir este padrão.

---

## 🏗️ Estrutura de Arquivos Padrão

### **Backend - Estrutura de Módulo**
```
backend/apps/{module_name}/
├── __init__.py
├── routes.py          # Endpoints da API
├── schemas.py         # Modelos Pydantic
├── services.py        # Lógica de negócio
└── models.py          # Modelos SQLAlchemy (se específico)
```

### **Frontend - Estrutura de Módulo**
```
saas-juridico-frontend/src/
├── hooks/
│   └── use{ModuleName}.ts    # Hook customizado
├── types/
│   └── {moduleName}.ts       # Tipos TypeScript
├── components/
│   └── features/
│       └── {moduleName}/     # Componentes específicos
└── app/
    └── company/
        └── {module-name}/    # Páginas do módulo
```

---

## 📝 Padrão de Schemas (Pydantic)

### **1. Schema de Criação**
```python
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime

class {ModuleName}Create(BaseModel):
    """Schema para criação de {module_name}"""
    # Campos obrigatórios
    name: str
    email: Optional[str] = None
    
    # Campos opcionais
    description: Optional[str] = None
    is_active: bool = True
    
    # Validações
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Nome é obrigatório")
        if len(v) > 255:
            raise ValueError("Nome deve ter no máximo 255 caracteres")
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError("Email inválido")
        return v
```

### **2. Schema de Atualização**
```python
class {ModuleName}Update(BaseModel):
    """Schema para atualização de {module_name}"""
    name: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    
    # Mesmas validações do Create
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Nome não pode estar vazio")
            if len(v) > 255:
                raise ValueError("Nome deve ter no máximo 255 caracteres")
            return v.strip()
        return v
```

### **3. Schema de Resposta**
```python
class {ModuleName}Response(BaseModel):
    """Schema para resposta de {module_name}"""
    id: str
    tenant_id: str
    name: str
    email: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
```

### **4. Schema de Lista**
```python
class {ModuleName}ListResponse(BaseModel):
    """Schema para resposta de lista de {module_name}"""
    {module_name}s: List[{ModuleName}Response]
    total: int
    page: int
    per_page: int
    total_pages: int
```

### **5. Schema de Estatísticas**
```python
class {ModuleName}Stats(BaseModel):
    """Schema para estatísticas de {module_name}"""
    total_{module_name}s: int
    active_{module_name}s: int
    inactive_{module_name}s: int
    # Outras estatísticas específicas
```

---

## 🔧 Padrão de Serviços

### **Classe de Serviço Padrão**
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from core.models.{module_name} import {ModuleName}
from apps.{module_name}.schemas import {ModuleName}Create, {ModuleName}Update
import uuid

class {ModuleName}Service:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_{module_name}(self, {module_name}_data: {ModuleName}Create, tenant_id: str) -> {ModuleName}:
        """Cria um novo {module_name} para o tenant"""
        # Verificar duplicatas se necessário
        existing = self.db.query({ModuleName}).filter(
            and_(
                {ModuleName}.tenant_id == tenant_id,
                {ModuleName}.name.ilike({module_name}_data.name)
            )
        ).first()
        
        if existing:
            raise ValueError(f"Já existe um {module_name} com o nome '{module_name}_data.name'")
        
        # Criar novo {module_name}
        {module_name} = {ModuleName}(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name={module_name}_data.name,
            email={module_name}_data.email,
            description={module_name}_data.description,
            is_active={module_name}_data.is_active
        )
        
        self.db.add({module_name})
        self.db.commit()
        self.db.refresh({module_name})
        
        return {module_name}
    
    async def get_{module_name}(self, {module_name}_id: str, tenant_id: str) -> Optional[{ModuleName}]:
        """Busca um {module_name} específico do tenant"""
        return self.db.query({ModuleName}).filter(
            and_(
                {ModuleName}.id == {module_name}_id,
                {ModuleName}.tenant_id == tenant_id
            )
        ).first()
    
    async def list_{module_name}s(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        order_by: str = "name"
    ) -> List[{ModuleName}]:
        """Lista {module_name}s do tenant com filtros"""
        query = self.db.query({ModuleName}).filter({ModuleName}.tenant_id == tenant_id)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    {ModuleName}.name.ilike(f"%{search}%"),
                    {ModuleName}.description.ilike(f"%{search}%")
                )
            )
        
        if is_active is not None:
            query = query.filter({ModuleName}.is_active == is_active)
        
        # Aplicar ordenação
        if order_by == "name":
            query = query.order_by(asc({ModuleName}.name))
        elif order_by == "created_at":
            query = query.order_by(desc({ModuleName}.created_at))
        else:
            query = query.order_by(asc({ModuleName}.name))
        
        return query.offset(skip).limit(limit).all()
    
    async def update_{module_name}(
        self,
        {module_name}_id: str,
        {module_name}_data: {ModuleName}Update,
        tenant_id: str
    ) -> Optional[{ModuleName}]:
        """Atualiza um {module_name}"""
        {module_name} = await self.get_{module_name}({module_name}_id, tenant_id)
        if not {module_name}:
            return None
        
        # Verificar duplicatas se nome foi alterado
        if {module_name}_data.name and {module_name}_data.name != {module_name}.name:
            existing = self.db.query({ModuleName}).filter(
                and_(
                    {ModuleName}.tenant_id == tenant_id,
                    {ModuleName}.name.ilike({module_name}_data.name),
                    {ModuleName}.id != {module_name}_id
                )
            ).first()
            
            if existing:
                raise ValueError(f"Já existe um {module_name} com o nome '{module_name}_data.name'")
        
        # Atualizar campos
        update_data = {module_name}_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr({module_name}, field, value)
        
        self.db.commit()
        self.db.refresh({module_name})
        
        return {module_name}
    
    async def delete_{module_name}(self, {module_name}_id: str, tenant_id: str) -> bool:
        """Remove um {module_name} (soft delete)"""
        {module_name} = await self.get_{module_name}({module_name}_id, tenant_id)
        if not {module_name}:
            return False
        
        # Verificar relacionamentos se necessário
        # if {module_name}.related_items:
        #     raise ValueError("Não é possível excluir um {module_name} que possui itens vinculados")
        
        # Soft delete
        {module_name}.is_active = False
        self.db.commit()
        return True
    
    async def activate_{module_name}(self, {module_name}_id: str, tenant_id: str) -> bool:
        """Reativa um {module_name}"""
        {module_name} = await self.get_{module_name}({module_name}_id, tenant_id)
        if not {module_name}:
            return False
        
        {module_name}.is_active = True
        self.db.commit()
        return True
    
    async def get_{module_name}_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Retorna estatísticas dos {module_name}s do tenant"""
        total = self.db.query({ModuleName}).filter({ModuleName}.tenant_id == tenant_id).count()
        active = self.db.query({ModuleName}).filter(
            and_(
                {ModuleName}.tenant_id == tenant_id,
                {ModuleName}.is_active == True
            )
        ).count()
        inactive = total - active
        
        return {
            "total_{module_name}s": total,
            "active_{module_name}s": active,
            "inactive_{module_name}s": inactive
        }
```

---

## 🌐 Padrão de Rotas (Endpoints)

### **Estrutura de Endpoints Padrão**
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.auth.multi_tenant_auth import MultiTenantAuth
from apps.{module_name}.schemas import (
    {ModuleName}Create, {ModuleName}Update, {ModuleName}Response,
    {ModuleName}ListResponse, {ModuleName}Stats
)
from apps.{module_name}.services import {ModuleName}Service

router = APIRouter(prefix="/{module_name}s", tags=["{ModuleName}s"])

# Instância do sistema de autenticação
auth = MultiTenantAuth()

# ==================== CRUD BÁSICO ====================

@router.post("/", response_model={ModuleName}Response)
async def create_{module_name}(
    {module_name}_data: {ModuleName}Create,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Cria um novo {module_name} (isolado por empresa)"""
    # Permissão verificada automaticamente pelo decorator require_permission
    
    tenant_id = current_user_data["tenant"].id
    service = {ModuleName}Service(db)
    
    try:
        {module_name} = await service.create_{module_name}({module_name}_data, str(tenant_id))
        return {module_name}.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar {module_name}: {str(e)}"
        )

@router.get("/", response_model=List[{ModuleName}Response])
async def list_{module_name}s(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    order_by: str = Query("name", regex="^(name|created_at)$"),
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Lista {module_name}s da empresa (isolado automaticamente)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name}s.read", False) or permissions.get("{module_name}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para visualizar {module_name}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {ModuleName}Service(db)
    
    try:
        {module_name}s = await service.list_{module_name}s(
            str(tenant_id),
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            order_by=order_by
        )
        
        return [{module_name}.to_dict() for {module_name} in {module_name}s]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar {module_name}s: {str(e)}"
        )

@router.get("/{module_name}_id", response_model={ModuleName}Response)
async def get_{module_name}(
    {module_name}_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Obtém {module_name} específico (isolado por empresa)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name}s.read", False) or permissions.get("{module_name}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para visualizar {module_name}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {ModuleName}Service(db)
    
    {module_name} = await service.get_{module_name}({module_name}_id, str(tenant_id))
    if not {module_name}:
        raise HTTPException(status_code=404, detail=f"{ModuleName} não encontrado")
    
    return {module_name}.to_dict()

@router.put("/{module_name}_id", response_model={ModuleName}Response)
async def update_{module_name}(
    {module_name}_id: str,
    {module_name}_data: {ModuleName}Update,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Atualiza {module_name} (isolado por empresa)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name}s.update", False) or permissions.get("{module_name}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para atualizar {module_name}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {ModuleName}Service(db)
    
    try:
        {module_name} = await service.update_{module_name}({module_name}_id, {module_name}_data, str(tenant_id))
        if not {module_name}:
            raise HTTPException(status_code=404, detail=f"{ModuleName} não encontrado")
        
        return {module_name}.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar {module_name}: {str(e)}"
        )

@router.delete("/{module_name}_id")
async def delete_{module_name}(
    {module_name}_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Remove {module_name} (soft delete, isolado por empresa)"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name}s.delete", False) or permissions.get("{module_name}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para deletar {module_name}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {ModuleName}Service(db)
    
    try:
        success = await service.delete_{module_name}({module_name}_id, str(tenant_id))
        if not success:
            raise HTTPException(status_code=404, detail=f"{ModuleName} não encontrado")
        
        return {"message": f"{ModuleName} removido com sucesso"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar {module_name}: {str(e)}"
        )

@router.post("/{module_name}_id/activate")
async def activate_{module_name}(
    {module_name}_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Reativa um {module_name}"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name}s.update", False) or permissions.get("{module_name}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para reativar {module_name}s"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {ModuleName}Service(db)
    
    success = await service.activate_{module_name}({module_name}_id, str(tenant_id))
    if not success:
        raise HTTPException(status_code=404, detail=f"{ModuleName} não encontrado")
    
    return {"message": f"{ModuleName} reativado com sucesso"}

# ==================== ESTATÍSTICAS ====================

@router.get("/stats/summary", response_model={ModuleName}Stats)
async def get_{module_name}_stats(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Retorna estatísticas dos {module_name}s"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("{module_name}s.read", False) or permissions.get("{module_name}s.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para visualizar estatísticas"
        )
    
    tenant_id = current_user_data["tenant"].id
    service = {ModuleName}Service(db)
    
    try:
        stats = await service.get_{module_name}_stats(str(tenant_id))
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )
```

---

## 🎨 Padrão de Modelos (SQLAlchemy)

### **Modelo Padrão**
```python
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid

class {ModuleName}(Base):
    """Modelo para {module_name}s"""
    __tablename__ = "{module_name}s"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Campos básicos
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    email = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Configurações
    settings = Column(JSON, default=dict)
    
    # Auditoria
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="{module_name}s")
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "description": self.description,
            "email": self.email,
            "is_active": self.is_active,
            "settings": self.settings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
```

---

## ⚛️ Padrão de Frontend (React/TypeScript)

### **1. Tipos TypeScript**
```typescript
// types/{moduleName}.ts
export interface {ModuleName} {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  email?: string;
  is_active: boolean;
  settings?: any;
  created_at: string;
  updated_at?: string;
}

export interface Create{ModuleName}Data {
  name: string;
  description?: string;
  email?: string;
  is_active?: boolean;
  settings?: any;
}

export interface Update{ModuleName}Data extends Partial<Create{ModuleName}Data> {}

export interface {ModuleName}Stats {
  total_{module_name}s: number;
  active_{module_name}s: number;
  inactive_{module_name}s: number;
}
```

### **2. Hook Customizado**
```typescript
// hooks/use{ModuleName}.ts
import { useState, useEffect } from "react";
import { useAuth } from "./useAuth";
import { toast } from "sonner";
import { {ModuleName}, Create{ModuleName}Data, Update{ModuleName}Data } from "@/types/{moduleName}";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export function use{ModuleName}s() {
  const { token } = useAuth();
  const [{module_name}s, set{ModuleName}s] = useState<{ModuleName}[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Buscar todos os {module_name}s
  const fetch{ModuleName}s = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/company/{module_name}s`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar {module_name}s`);
      }

      const data = await response.json();
      set{ModuleName}s(data || []);
    } catch (error) {
      console.error(`Erro ao buscar {module_name}s:`, error);
      setError(`Erro ao carregar {module_name}s`);
      toast.error(`Erro ao carregar {module_name}s`);
    } finally {
      setLoading(false);
    }
  };

  // Criar novo {module_name}
  const create{ModuleName} = async ({module_name}Data: Create{ModuleName}Data): Promise<{ModuleName} | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/{module_name}s`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({module_name}Data),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao criar {module_name}`);
      }

      const new{ModuleName} = await response.json();
      set{ModuleName}s(prev => [...prev, new{ModuleName}]);
      toast.success(`{ModuleName} criado com sucesso`);
      return new{ModuleName};
    } catch (error) {
      console.error(`Erro ao criar {module_name}:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao criar {module_name}`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar {module_name}
  const update{ModuleName} = async ({module_name}Id: string, {module_name}Data: Update{ModuleName}Data): Promise<{ModuleName} | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/{module_name}s/${module_name}Id`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({module_name}Data),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao atualizar {module_name}`);
      }

      const updated{ModuleName} = await response.json();
      set{ModuleName}s(prev => prev.map({module_name} => 
        {module_name}.id === {module_name}Id ? updated{ModuleName} : {module_name}
      ));
      toast.success(`{ModuleName} atualizado com sucesso`);
      return updated{ModuleName};
    } catch (error) {
      console.error(`Erro ao atualizar {module_name}:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao atualizar {module_name}`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Deletar {module_name}
  const delete{ModuleName} = async ({module_name}Id: string): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/{module_name}s/${module_name}Id`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao deletar {module_name}`);
      }

      set{ModuleName}s(prev => prev.filter({module_name} => {module_name}.id !== {module_name}Id));
      toast.success(`{ModuleName} deletado com sucesso`);
      return true;
    } catch (error) {
      console.error(`Erro ao deletar {module_name}:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao deletar {module_name}`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Buscar {module_name} específico
  const get{ModuleName} = async ({module_name}Id: string): Promise<{ModuleName} | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/{module_name}s/${module_name}Id`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`{ModuleName} não encontrado`);
      }

      const {module_name} = await response.json();
      return {module_name};
    } catch (error) {
      console.error(`Erro ao buscar {module_name}:`, error);
      setError(`Erro ao buscar {module_name}`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Filtrar {module_name}s
  const filter{ModuleName}s = (searchTerm: string) => {
    return {module_name}s.filter({module_name} =>
      {module_name}.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ({module_name}.description && {module_name}.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
      ({module_name}.email && {module_name}.email.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  };

  // Carregar {module_name}s na inicialização
  useEffect(() => {
    if (token) {
      fetch{ModuleName}s();
    }
  }, [token]);

  return {
    {module_name}s,
    loading,
    error,
    fetch{ModuleName}s,
    create{ModuleName},
    update{ModuleName},
    delete{ModuleName},
    get{ModuleName},
    filter{ModuleName}s,
  };
}
```

---

## 🔐 Padrão de Permissões

### **Permissões Padrão por Módulo**
```python
# Permissões que devem ser implementadas para cada módulo
MODULE_PERMISSIONS = {
    "{module_name}s": {
        "read": "Visualizar {module_name}s",
        "create": "Criar {module_name}s", 
        "update": "Atualizar {module_name}s",
        "delete": "Deletar {module_name}s",
        "manage": "Gerenciar {module_name}s (todas as permissões)"
    }
}

# Permissões por role
ROLE_PERMISSIONS = {
    "admin": {
        "{module_name}s": ["read", "create", "update", "delete", "manage"]
    },
    "lawyer": {
        "{module_name}s": ["read", "create", "update"]
    },
    "assistant": {
        "{module_name}s": ["read", "create"]
    },
    "secretary": {
        "{module_name}s": ["read"]
    }
}
```

---

## 📋 Checklist de Implementação

### **Para cada novo módulo, verificar:**

#### **Backend**
- [ ] ✅ Estrutura de arquivos criada
- [ ] ✅ Schema Pydantic implementado
- [ ] ✅ Modelo SQLAlchemy criado
- [ ] ✅ Serviço implementado
- [ ] ✅ Rotas configuradas
- [ ] ✅ Permissões definidas
- [ ] ✅ Validações implementadas
- [ ] ✅ Soft delete implementado
- [ ] ✅ Estatísticas implementadas
- [ ] ✅ Testes básicos criados

#### **Frontend**
- [ ] ✅ Tipos TypeScript definidos
- [ ] ✅ Hook customizado criado
- [ ] ✅ Componentes básicos implementados
- [ ] ✅ Páginas de CRUD criadas
- [ ] ✅ Integração com API testada
- [ ] ✅ Tratamento de erros implementado
- [ ] ✅ Loading states implementados
- [ ] ✅ Feedback visual (toasts) implementado

#### **Integração**
- [ ] ✅ Módulo registrado no main.py
- [ ] ✅ Rotas incluídas no router
- [ ] ✅ Middleware de autenticação configurado
- [ ] ✅ Isolamento por tenant testado
- [ ] ✅ Permissões testadas
- [ ] ✅ Documentação atualizada

---

## 🎯 Exemplo de Implementação

### **Módulo "Products" (Exemplo)**

#### **1. Backend**
```python
# apps/products/schemas.py
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Nome do produto é obrigatório")
        return v.strip()
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return v

# apps/products/services.py
class ProductService:
    async def create_product(self, product_data: ProductCreate, tenant_id: str):
        # Implementação seguindo o padrão
        pass

# apps/products/routes.py
@router.post("/", response_model=ProductResponse)
async def create_product(product_data: ProductCreate, ...):
    # Implementação seguindo o padrão
    pass
```

#### **2. Frontend**
```typescript
// types/product.ts
export interface Product {
  id: string;
  name: string;
  description?: string;
  price: number;
  category: string;
  // ...
}

// hooks/useProducts.ts
export function useProducts() {
  // Implementação seguindo o padrão
  const createProduct = async (productData: CreateProductData) => {
    // ...
  };
}
```

---

## 📚 Documentação

### **Para cada módulo, criar:**
1. **README específico** com funcionalidades
2. **Documentação da API** (Swagger/OpenAPI)
3. **Exemplos de uso** no frontend
4. **Guia de permissões** específico

### **Manter atualizado:**
- [ ] Lista de módulos implementados
- [ ] Status de implementação
- [ ] Dependências entre módulos
- [ ] Breaking changes

---

## 🚀 Conclusão

Este padrão garante:
- ✅ **Consistência** entre todos os módulos
- ✅ **Manutenibilidade** do código
- ✅ **Escalabilidade** do sistema
- ✅ **Facilidade** de implementação
- ✅ **Qualidade** do código

**Sempre seguir este padrão ao implementar novos módulos!**
