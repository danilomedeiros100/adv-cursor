# CRUD de Usuários - Implementação Completa

## 📋 Resumo da Implementação

O CRUD completo de usuários foi implementado com sucesso, incluindo:

- ✅ **Criação de usuários** com diferentes roles (admin, lawyer, assistant, secretary, receptionist)
- ✅ **Validações específicas** para advogados (OAB obrigatória)
- ✅ **Listagem com filtros** (busca, role, departamento, status)
- ✅ **Atualização de dados** e roles
- ✅ **Soft delete** (desativação/reativação)
- ✅ **Alteração de senhas**
- ✅ **Estatísticas** e relatórios
- ✅ **Isolamento por tenant** (multi-tenancy)
- ✅ **Sistema de permissões** baseado em roles

## 🏗️ Arquitetura

### Modelos de Dados

#### 1. User (backend/core/models/user.py)
```python
class User(Base):
    # Informações básicas
    name, email, password_hash
    
    # Informações pessoais
    phone, birth_date, cpf
    
    # Informações profissionais
    oab_number, oab_state, position, department
    
    # Configurações
    is_active, is_super_admin, email_verified, phone_verified
    
    # Segurança
    last_login, last_password_change, failed_login_attempts, locked_until
```

#### 2. TenantUser (backend/core/models/tenant_user.py)
```python
class TenantUser(Base):
    # Relacionamento
    tenant_id, user_id
    
    # Role e permissões
    role, permissions
    
    # Configurações específicas
    department, position, is_active, is_primary_admin
```

#### 3. UserProfile (backend/core/models/user.py)
```python
class UserProfile(Base):
    # Informações profissionais
    bio, experience_years, education, certifications
    
    # Configurações de trabalho
    working_hours, availability
```

### Roles e Permissões

#### Roles Disponíveis
1. **admin** - Acesso total ao sistema
2. **lawyer** - Advogado com acesso a processos e documentos
3. **assistant** - Assistente jurídico
4. **secretary** - Secretário
5. **receptionist** - Recepcionista
6. **user** - Usuário padrão

#### Permissões por Role
```python
DEFAULT_ROLE_PERMISSIONS = {
    "admin": {
        "modules": ["*"],  # Todos os módulos
        "permissions": {
            "clients": {"read": True, "create": True, "update": True, "delete": True},
            "processes": {"read": True, "create": True, "update": True, "delete": True},
            "documents": {"read": True, "create": True, "update": True, "delete": True, "sign": True},
            "financial": {"read": True, "create": True, "update": True, "delete": True},
            "reports": {"read": True, "create": True, "export": True},
            "users": {"read": True, "create": True, "update": True, "delete": True},
            "specialties": {"read": True, "create": True, "update": True, "delete": True},
            "settings": {"read": True, "update": True}
        }
    },
    "lawyer": {
        "modules": ["clients", "processes", "documents", "tasks", "reports"],
        "permissions": {
            "clients": {"read": True, "create": True, "update": True, "delete": False},
            "processes": {"read": True, "create": True, "update": True, "delete": False},
            "documents": {"read": True, "create": True, "update": True, "delete": False, "sign": True},
            "tasks": {"read": True, "create": True, "update": True, "delete": False},
            "reports": {"read": True, "create": False, "export": False}
        }
    }
    # ... outros roles
}
```

## 🚀 Endpoints da API

### Base URL
```
/api/v1/company/users
```

### 1. Criar Usuário
```http
POST /api/v1/company/users
```

**Payload:**
```json
{
    "name": "João Silva",
    "email": "joao.silva@empresa.com",
    "password": "senha123",
    "phone": "(11) 99999-9999",
    "cpf": "123.456.789-00",
    "oab_number": "123456",  // Obrigatório para lawyers
    "oab_state": "SP",       // Obrigatório para lawyers
    "position": "Advogado Sênior",
    "department": "Direito Civil",
    "role": "lawyer",
    "is_active": true
}
```

### 2. Listar Usuários
```http
GET /api/v1/company/users
GET /api/v1/company/users?search=João
GET /api/v1/company/users?role=lawyer
GET /api/v1/company/users?department=Direito Civil
GET /api/v1/company/users?is_active=true
GET /api/v1/company/users?has_oab=true
```

### 3. Obter Usuário Específico
```http
GET /api/v1/company/users/{user_id}
```

### 4. Atualizar Usuário
```http
PUT /api/v1/company/users/{user_id}
```

**Payload:**
```json
{
    "name": "João Silva Atualizado",
    "phone": "(11) 99999-0000",
    "position": "Advogado Pleno",
    "department": "Direito Trabalhista"
}
```

### 5. Atualizar Role
```http
PUT /api/v1/company/users/{user_id}/role?role=admin
```

### 6. Desativar Usuário
```http
DELETE /api/v1/company/users/{user_id}
```

### 7. Reativar Usuário
```http
POST /api/v1/company/users/{user_id}/activate
```

### 8. Alterar Senha
```http
POST /api/v1/company/users/{user_id}/change-password
```

**Payload:**
```json
{
    "current_password": "senha_atual",
    "new_password": "nova_senha"
}
```

### 9. Estatísticas
```http
GET /api/v1/company/users/stats/summary
```

**Response:**
```json
{
    "total_users": 10,
    "active_users": 8,
    "inactive_users": 2,
    "role_counts": {
        "admin": 1,
        "lawyer": 3,
        "assistant": 2,
        "secretary": 2,
        "receptionist": 1,
        "user": 1
    },
    "lawyers_with_oab": 3
}
```

### 10. Listar Departamentos
```http
GET /api/v1/company/users/departments/list
```

## 🔒 Validações e Segurança

### Validações de Entrada
1. **Email único** - Não permite emails duplicados
2. **CPF válido** - Validação de formato e dígitos
3. **OAB obrigatória** - Para usuários com role "lawyer"
4. **Senha mínima** - Mínimo 6 caracteres
5. **Campos obrigatórios** - name, email, password

### Segurança
1. **Isolamento por tenant** - Usuários só veem dados do seu tenant
2. **Permissões baseadas em roles** - Controle granular de acesso
3. **Soft delete** - Não remove dados permanentemente
4. **Hash de senhas** - Senhas criptografadas com Werkzeug
5. **Tentativas de login** - Bloqueio após 5 tentativas falhadas

### Validações Específicas para Advogados
```python
@validator('oab_number', 'oab_state')
def validate_oab_fields(cls, v, values):
    """Valida campos OAB quando role é lawyer"""
    if values.get('role') == UserRole.LAWYER:
        if 'oab_number' in values and not values['oab_number']:
            raise ValueError("Número OAB é obrigatório para advogados")
        if 'oab_state' in values and not values['oab_state']:
            raise ValueError("Estado OAB é obrigatório para advogados")
    return v
```

## 📊 Funcionalidades Avançadas

### 1. Filtros de Busca
- **Busca por nome, email, CPF, OAB**
- **Filtro por role**
- **Filtro por departamento**
- **Filtro por status (ativo/inativo)**
- **Filtro por presença de OAB**

### 2. Estatísticas
- **Total de usuários**
- **Usuários ativos/inativos**
- **Contagem por role**
- **Advogados com OAB**

### 3. Gestão de Departamentos
- **Lista automática de departamentos**
- **Filtros por departamento**
- **Associação de usuários a departamentos**

### 4. Sistema de Permissões
- **Permissões padrão por role**
- **Permissões personalizadas por usuário**
- **Controle de acesso a módulos**
- **Permissões granulares (read, create, update, delete)**

## 🧪 Testes

### Script de Teste
Execute o script `test_users_crud.py` para testar todas as funcionalidades:

```bash
python test_users_crud.py
```

### Testes Incluídos
1. ✅ Criação de usuários com diferentes roles
2. ✅ Listagem com filtros
3. ✅ Obtenção de usuário específico
4. ✅ Atualização de dados
5. ✅ Atualização de role
6. ✅ Desativação/reativação
7. ✅ Alteração de senha
8. ✅ Estatísticas
9. ✅ Lista de departamentos

## 🔧 Configuração

### 1. Incluir Rotas no main.py
```python
from apps.users.routes import router as users_router

app.include_router(
    users_router,
    prefix="/api/v1/company",
    tags=["Users"]
)
```

### 2. Dependências
- FastAPI
- SQLAlchemy
- Pydantic
- Werkzeug (para hash de senhas)

### 3. Middleware
- **TenantIsolationMiddleware** - Isolamento por tenant
- **MultiTenantAuth** - Autenticação multi-tenant

## 📈 Próximos Passos

### Funcionalidades Futuras
1. **Upload de foto de perfil**
2. **Notificações por email**
3. **Logs de auditoria**
4. **Importação em lote**
5. **Exportação de relatórios**
6. **Integração com OAB**
7. **Sistema de especialidades**
8. **Horários de trabalho**

### Melhorias Técnicas
1. **Cache Redis** para performance
2. **Paginação otimizada**
3. **Busca full-text**
4. **API de webhooks**
5. **Rate limiting**
6. **Logs estruturados**

## 🎯 Conclusão

O CRUD de usuários está **100% funcional** e pronto para produção, com:

- ✅ **Arquitetura robusta** e escalável
- ✅ **Segurança implementada** com isolamento por tenant
- ✅ **Validações completas** incluindo OAB para advogados
- ✅ **Sistema de permissões** granular
- ✅ **API documentada** e testada
- ✅ **Funcionalidades avançadas** como estatísticas e filtros

O sistema está pronto para ser integrado ao frontend e utilizado em produção! 🚀
