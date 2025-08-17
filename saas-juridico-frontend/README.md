# 🚀 SaaS Jurídico - Frontend

Frontend moderno para o sistema SaaS Jurídico, desenvolvido com Next.js 14, React 18, TypeScript e Shadcn/ui.

## 🛠️ Stack Tecnológica

- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: Shadcn/ui
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **Tables**: TanStack Table
- **Authentication**: NextAuth.js
- **Icons**: Lucide React
- **Notifications**: Sonner

## 🚀 Como Executar

### Pré-requisitos

- Node.js 18+ 
- npm ou yarn

### Instalação

```bash
# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Executar em produção
npm start
```

## 📁 Estrutura do Projeto

```
src/
├── app/                    # App Router (Next.js 14)
│   ├── (auth)/            # Rotas de autenticação
│   │   └── login/         # Página de login
│   ├── (dashboard)/       # Dashboard principal
│   │   ├── superadmin/    # Portal Super Admin
│   │   ├── company/       # Portal Empresas
│   │   └── client/        # Portal Cliente
│   ├── api/               # API Routes
│   └── globals.css        # Estilos globais
├── components/            # Componentes reutilizáveis
│   ├── ui/               # Componentes Shadcn/ui
│   ├── layout/           # Componentes de layout
│   ├── forms/            # Formulários
│   ├── charts/           # Gráficos
│   └── features/         # Funcionalidades específicas
├── hooks/                # Custom hooks
├── stores/               # Stores Zustand
├── types/                # Tipos TypeScript
└── lib/                  # Utilitários e configurações
```

## 🎨 Componentes Principais

### Layout
- `DashboardLayout`: Layout principal com sidebar
- `Sidebar`: Navegação lateral responsiva

### Autenticação
- `LoginPage`: Página de login multi-tenant
- `useAuth`: Hook para gerenciar autenticação
- `usePermissions`: Hook para verificar permissões

### Dashboard
- `CompanyDashboardPage`: Dashboard da empresa
- Cards de estatísticas
- Atividades recentes
- Ações rápidas

## 🔐 Sistema de Autenticação

### Multi-Tenant
- Suporte a múltiplas empresas (tenants)
- Isolamento completo de dados
- URLs específicas por tenant

### Tipos de Usuário
- **Super Admin**: Gerencia toda a plataforma
- **Company User**: Usuário de empresa
- **Client User**: Cliente externo

### Permissões
- Sistema granular de permissões
- Permissões por módulo e ação
- Permissões personalizadas por usuário

## 🎯 Funcionalidades Implementadas

### ✅ Concluído
- [x] Setup do projeto Next.js 14
- [x] Instalação do Shadcn/ui
- [x] Sistema de autenticação básico
- [x] Layout responsivo
- [x] Dashboard da empresa
- [x] Página de login
- [x] Navegação por tipo de usuário
- [x] Sistema de permissões
- [x] Tipos TypeScript

### 🚧 Em Desenvolvimento
- [ ] Integração com API backend
- [ ] Módulo de clientes
- [ ] Módulo de processos
- [ ] Módulo de documentos
- [ ] Módulo financeiro
- [ ] Portal do cliente
- [ ] Portal super admin

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### ESLint

Configurado para ignorar erros durante o build para desenvolvimento rápido.

## 📱 Responsividade

- Design mobile-first
- Sidebar colapsável
- Componentes responsivos
- Breakpoints do Tailwind

## 🎨 Design System

### Cores
- **Primary**: Azul corporativo
- **Secondary**: Cinza neutro
- **Success**: Verde
- **Warning**: Laranja
- **Error**: Vermelho

### Componentes
- Botões com variantes
- Cards informativos
- Formulários validados
- Tabelas responsivas
- Modais e diálogos

## 🚀 Deploy

### Vercel (Recomendado)
```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

---

**Desenvolvido com ❤️ para modernizar a advocacia brasileira**
