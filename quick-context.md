# ⚡ Contexto Rápido - SaaS Jurídico

> **Use este arquivo quando perder contexto no Cursor!**

## 🎯 Projeto Atual
**SaaS Multi-Tenant para Escritórios de Advocacia**

## 📊 Status
- ✅ **Backend**: FastAPI funcional com 5 módulos
- ✅ **Frontend**: React + Next.js em desenvolvimento  
- ✅ **Infra**: Docker Compose com 11 serviços
- ✅ **Multi-tenant**: Isolamento completo implementado

## 🔧 Comandos Essenciais
```bash
# Iniciar tudo
docker-compose up -d

# Ver logs
docker-compose logs backend

# Acessar banco
docker-compose exec postgres psql -U saas_user -d saas_juridico
```

## 🌐 URLs
- API: http://localhost:8000
- Frontend: http://localhost:3000  
- Grafana: http://localhost:3001
- Docs: http://localhost:8000/docs

## 📁 Estrutura Importante
```
/workspace/
├── backend/apps/          # Módulos da API
├── saas-juridico-frontend/# Interface React
├── docker-compose.yml     # Infra completa
└── README.md             # Doc principal (900+ linhas)
```

## 🎯 Módulos Prontos
1. **auth** - Autenticação multi-tenant
2. **users** - Gestão usuários + hierarquia  
3. **clients** - Cadastro PF/PJ + portal
4. **processes** - CRUD + timeline
5. **specialties** - Especialidades jurídicas

## 🚀 Últimas Implementações
- Interface busca inteligente
- Dashboard com estatísticas  
- Sistema permissões granular
- Portal cliente funcional

## 📋 Próximos Passos
- Sistema financeiro
- Módulo documentos
- Integrações CNJ
- IA jurídica

---
**Sempre referencie este arquivo quando iniciar nova conversa!**