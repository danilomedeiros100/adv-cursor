# 🧠 Gerenciamento de Contexto - SaaS Jurídico

## 📋 Contexto do Projeto

### **Estrutura Principal**
- **Backend**: FastAPI + PostgreSQL (multi-tenant)
- **Frontend**: React + Next.js + TypeScript
- **Infraestrutura**: Docker Compose completo
- **Arquitetura**: Multi-tenant com isolamento total

### **Módulos Implementados**
1. ✅ **Auth** - Sistema de autenticação multi-tenant
2. ✅ **Users** - Gestão de usuários com hierarquia
3. ✅ **Clients** - Cadastro PF/PJ + Portal cliente
4. ✅ **Processes** - CRUD processos + Timeline
5. ✅ **Specialties** - Especialidades jurídicas

### **Arquivos Principais para Referência**
```
/workspace/
├── README.md                    # Documentação principal (900+ linhas)
├── docker-compose.yml          # Infraestrutura completa
├── backend/
│   ├── main.py                 # Entry point da API
│   ├── apps/                   # Módulos da aplicação
│   │   ├── auth/              # Autenticação
│   │   ├── users/             # Usuários
│   │   ├── clients/           # Clientes
│   │   ├── processes/         # Processos
│   │   └── specialties/       # Especialidades
│   └── core/                  # Configurações centrais
└── saas-juridico-frontend/    # Interface React
    └── src/                   # Código fonte frontend
```

### **Padrões do Projeto**
- **Multi-tenant**: Todas tabelas com `tenant_id`
- **Isolamento**: Row-Level Security no PostgreSQL
- **APIs**: RESTful com FastAPI + Pydantic
- **Auth**: JWT com permissões granulares
- **Frontend**: TypeScript + Tailwind CSS

### **Comandos Úteis**
```bash
# Iniciar ambiente
docker-compose up -d

# Logs do backend
docker-compose logs backend

# Executar migrações
docker-compose exec backend alembic upgrade head

# Criar super admin
docker-compose exec backend python scripts/create_superadmin_seed.py
```

### **URLs de Desenvolvimento**
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Grafana: http://localhost:3001
- Adminer: http://localhost:8080

## 🎯 Estado Atual

### **Últimas Implementações**
- Interface de busca inteligente para processos
- Dashboard com estatísticas em tempo real
- Sistema de permissões granular
- Portal do cliente funcional

### **Próximos Passos Planejados**
- Sistema financeiro completo
- Módulo de documentos com versionamento
- Integrações CNJ e tribunais
- IA jurídica para automação

---

**Use este arquivo como referência rápida do contexto do projeto!**