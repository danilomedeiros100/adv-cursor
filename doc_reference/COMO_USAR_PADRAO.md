# 🚀 Como Usar o Padrão de Módulos

## 📋 Visão Geral

Este guia explica como usar o **padrão de módulos** definido em `PADRAO_MODULOS.md` para criar novos módulos de forma consistente e eficiente.

---

## 🛠️ Método 1: Script Automático (Recomendado)

### **Criar um novo módulo automaticamente:**

```bash
# Exemplo: Criar módulo "products"
python scripts/create_module_template.py --module-name "products" --module-title "Produtos"

# Exemplo: Criar módulo "documents"
python scripts/create_module_template.py --module-name "documents" --module-title "Documentos"

# Exemplo: Criar módulo "financial"
python scripts/create_module_template.py --module-name "financial" --module-title "Financeiro"
```

### **O que o script faz automaticamente:**

✅ **Backend:**
- Cria estrutura de diretórios
- Gera `schemas.py` com validações
- Gera `services.py` com lógica de negócio
- Gera `routes.py` com endpoints CRUD
- Gera `__init__.py` com imports

✅ **Frontend:**
- Cria tipos TypeScript
- Gera hook customizado
- Cria página básica
- Configura integração com API

✅ **Documentação:**
- Lista arquivos criados
- Mostra endpoints gerados
- Fornece próximos passos

---

## 🛠️ Método 2: Manual (Para casos específicos)

### **1. Estrutura de Diretórios**

```bash
# Backend
mkdir -p backend/apps/{module_name}
touch backend/apps/{module_name}/__init__.py
touch backend/apps/{module_name}/schemas.py
touch backend/apps/{module_name}/services.py
touch backend/apps/{module_name}/routes.py

# Frontend
mkdir -p saas-juridico-frontend/src/app/company/{module-name}
touch saas-juridico-frontend/src/types/{moduleName}.ts
touch saas-juridico-frontend/src/hooks/use{ModuleName}.ts
touch saas-juridico-frontend/src/app/company/{module-name}/page.tsx
```

### **2. Copiar Templates**

Use os templates do `PADRAO_MODULOS.md` e substitua:
- `{module_name}` → nome do módulo (snake_case)
- `{ModuleName}` → nome do módulo (PascalCase)
- `{module_title}` → título do módulo

---

## 📝 Exemplos Práticos

### **Exemplo 1: Módulo "Products"**

```bash
python scripts/create_module_template.py --module-name "products" --module-title "Produtos"
```

**Resultado:**
```
backend/apps/products/
├── __init__.py
├── schemas.py          # ProductCreate, ProductUpdate, ProductResponse
├── services.py         # ProductService
└── routes.py           # CRUD endpoints

saas-juridico-frontend/src/
├── types/products.ts   # Product interface
├── hooks/useProducts.ts # useProducts hook
└── app/company/products/page.tsx
```

**Endpoints criados:**
```
POST   /api/v1/company/products/
GET    /api/v1/company/products/
GET    /api/v1/company/products/{id}
PUT    /api/v1/company/products/{id}
DELETE /api/v1/company/products/{id}
POST   /api/v1/company/products/{id}/activate
GET    /api/v1/company/products/stats/summary
```

### **Exemplo 2: Módulo "Documents"**

```bash
python scripts/create_module_template.py --module-name "documents" --module-title "Documentos"
```

**Resultado:**
```
backend/apps/documents/
├── __init__.py
├── schemas.py          # DocumentCreate, DocumentUpdate, DocumentResponse
├── services.py         # DocumentService
└── routes.py           # CRUD endpoints

saas-juridico-frontend/src/
├── types/documents.ts  # Document interface
├── hooks/useDocuments.ts # useDocuments hook
└── app/company/documents/page.tsx
```

---

## 🔧 Personalizações Comuns

### **1. Adicionar Campos Específicos**

**No schema:**
```python
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float  # Campo específico
    category: str  # Campo específico
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return v
```

**No modelo:**
```python
class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Campos básicos
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Campos específicos
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
```

### **2. Adicionar Relacionamentos**

**No modelo:**
```python
class Product(Base):
    # ... campos básicos ...
    
    # Relacionamentos
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")
    
    # Relacionamento com processos
    process_products = relationship("ProcessProduct", back_populates="product")
```

### **3. Adicionar Endpoints Específicos**

**No routes.py:**
```python
@router.post("/{product_id}/upload-image")
async def upload_product_image(
    product_id: str,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Upload de imagem do produto"""
    # Implementação específica
    pass

@router.get("/{product_id}/reviews")
async def get_product_reviews(
    product_id: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Lista reviews do produto"""
    # Implementação específica
    pass
```

---

## 🔐 Configuração de Permissões

### **1. Adicionar Permissões no Sistema**

**Em `core/models/user_roles.py`:**
```python
DEFAULT_ROLE_PERMISSIONS = {
    "admin": {
        "products": ["read", "create", "update", "delete", "manage"],
        "documents": ["read", "create", "update", "delete", "manage"],
        # ... outros módulos
    },
    "lawyer": {
        "products": ["read", "create", "update"],
        "documents": ["read", "create", "update"],
        # ... outros módulos
    },
    "assistant": {
        "products": ["read", "create"],
        "documents": ["read", "create"],
        # ... outros módulos
    }
}
```

### **2. Verificar Permissões nos Endpoints**

```python
@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(auth.get_current_user_with_tenant)
):
    """Cria um novo produto"""
    # Verifica permissão
    permissions = current_user_data["permissions"]
    if not (permissions.get("products.create", False) or permissions.get("products.manage", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar produtos"
        )
    
    # ... resto da implementação
```

---

## 📋 Checklist de Implementação

### **Após criar o módulo com o script:**

#### **Backend**
- [ ] ✅ Estrutura criada automaticamente
- [ ] 🔧 Criar modelo SQLAlchemy em `core/models/`
- [ ] 🔧 Adicionar router no `main.py`
- [ ] 🔧 Criar migration: `alembic revision --autogenerate -m "Add {module_name} table"`
- [ ] 🔧 Executar migration: `alembic upgrade head`
- [ ] 🔧 Adicionar permissões no sistema de roles
- [ ] 🔧 Testar endpoints com Postman/Insomnia

#### **Frontend**
- [ ] ✅ Estrutura criada automaticamente
- [ ] 🔧 Adicionar rota no sidebar
- [ ] 🔧 Implementar formulários de CRUD
- [ ] 🔧 Adicionar validações específicas
- [ ] 🔧 Implementar filtros avançados
- [ ] 🔧 Testar integração com backend

#### **Integração**
- [ ] 🔧 Testar isolamento por tenant
- [ ] 🔧 Verificar permissões
- [ ] 🔧 Testar soft delete
- [ ] 🔧 Validar estatísticas
- [ ] 🔧 Documentar funcionalidades

---

## 🎯 Exemplo Completo: Módulo "Tasks"

### **1. Criar o módulo:**
```bash
python scripts/create_module_template.py --module-name "tasks" --module-title "Tarefas"
```

### **2. Personalizar schemas:**
```python
# backend/apps/tasks/schemas.py
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high
    assigned_to: Optional[str] = None  # user_id
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ["low", "medium", "high"]:
            raise ValueError("Prioridade deve ser low, medium ou high")
        return v
```

### **3. Criar modelo:**
```python
# backend/core/models/task.py
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
```

### **4. Adicionar no main.py:**
```python
# backend/main.py
from apps.tasks.routes import router as tasks_router

# ... outras rotas ...

app.include_router(
    tasks_router,
    prefix="/api/v1/company",
    tags=["Tasks"]
)
```

### **5. Criar migration:**
```bash
alembic revision --autogenerate -m "Add tasks table"
alembic upgrade head
```

### **6. Testar:**
```bash
# Backend
uvicorn main:app --reload

# Frontend
npm run dev
```

---

## 🚀 Dicas e Boas Práticas

### **1. Nomenclatura**
- **Módulo**: Use nomes descritivos (products, documents, tasks)
- **Classes**: PascalCase (Product, Document, Task)
- **Funções**: snake_case (create_product, get_document)
- **Variáveis**: snake_case (product_data, document_id)

### **2. Validações**
- Sempre valide dados de entrada
- Use mensagens de erro claras
- Implemente validações específicas do negócio

### **3. Segurança**
- Sempre verificar permissões
- Validar tenant_id em todas as operações
- Implementar soft delete quando apropriado

### **4. Performance**
- Use índices no banco de dados
- Implemente paginação em listas grandes
- Otimize queries com joins quando necessário

### **5. Documentação**
- Documente endpoints com docstrings
- Mantenha README atualizado
- Comente código complexo

---

## 🆘 Solução de Problemas

### **Erro: "Module not found"**
```bash
# Verificar se o módulo foi criado corretamente
ls -la backend/apps/{module_name}/

# Verificar imports no main.py
cat backend/main.py | grep {module_name}
```

### **Erro: "Table not found"**
```bash
# Verificar se a migration foi criada
ls -la backend/migrations/versions/ | grep {module_name}

# Executar migrations
alembic upgrade head
```

### **Erro: "Permission denied"**
```python
# Verificar se as permissões foram adicionadas
# Em core/models/user_roles.py
DEFAULT_ROLE_PERMISSIONS = {
    "admin": {
        "{module_name}s": ["read", "create", "update", "delete", "manage"]
    }
}
```

### **Erro: "Hook not found"**
```bash
# Verificar se o hook foi criado
ls -la saas-juridico-frontend/src/hooks/ | grep use{ModuleName}

# Verificar imports
cat saas-juridico-frontend/src/app/company/{module-name}/page.tsx
```

---

## 📞 Suporte

Se encontrar problemas:

1. **Verificar logs** do backend e frontend
2. **Consultar documentação** em `PADRAO_MODULOS.md`
3. **Verificar exemplos** dos módulos existentes
4. **Testar com Postman** para isolar problemas
5. **Criar issue** no repositório com detalhes

---

**🎯 Lembre-se: Sempre seguir o padrão para manter consistência no projeto!**
