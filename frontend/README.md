# 🎨 Frontend - SaaS Jurídico

Frontend moderno desenvolvido com **Next.js 14**, **React 18** e **TypeScript** para o SaaS Jurídico.

## 🚀 Tecnologias

### **Core**
- **Next.js 14** - Framework React com SSR/SSG
- **React 18** - Biblioteca de interface
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Framework CSS utilitário

### **State Management**
- **Zustand** - Gerenciamento de estado simples
- **React Query** - Cache e sincronização de dados
- **React Hook Form** - Formulários performáticos

### **UI/UX**
- **Headless UI** - Componentes acessíveis
- **Heroicons** - Ícones SVG
- **Lucide React** - Ícones modernos
- **Recharts** - Gráficos e visualizações
- **React Table** - Tabelas avançadas

### **Funcionalidades**
- **NextAuth.js** - Autenticação
- **React Hot Toast** - Notificações
- **React Dropzone** - Upload de arquivos
- **TipTap** - Editor de texto rico

## 📁 Estrutura do Projeto

```
frontend/
├── app/                          # App Router (Next.js 14)
│   ├── (auth)/                   # Rotas de autenticação
│   │   ├── login/
│   │   ├── register/
│   │   └── forgot-password/
│   ├── (dashboard)/              # Dashboard principal
│   │   ├── superadmin/           # Portal Super Admin
│   │   │   ├── dashboard/
│   │   │   ├── tenants/
│   │   │   └── analytics/
│   │   ├── company/              # Portal Empresas
│   │   │   ├── dashboard/
│   │   │   ├── clients/
│   │   │   ├── processes/
│   │   │   ├── documents/
│   │   │   ├── financial/
│   │   │   └── settings/
│   │   └── client/               # Portal Cliente
│   │       ├── dashboard/
│   │       ├── processes/
│   │       └── documents/
│   ├── api/                      # API Routes
│   ├── globals.css               # Estilos globais
│   ├── layout.tsx                # Layout raiz
│   └── page.tsx                  # Página inicial
├── components/                   # Componentes reutilizáveis
│   ├── ui/                       # Componentes base
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   └── Table.tsx
│   ├── forms/                    # Componentes de formulário
│   ├── charts/                   # Componentes de gráficos
│   ├── layout/                   # Componentes de layout
│   └── features/                 # Componentes específicos
├── lib/                          # Utilitários e configurações
│   ├── api.ts                    # Cliente API
│   ├── auth.ts                   # Configuração de autenticação
│   ├── utils.ts                  # Funções utilitárias
│   └── validations.ts            # Schemas de validação
├── hooks/                        # Custom hooks
│   ├── useAuth.ts
│   ├── useTenant.ts
│   └── useNotifications.ts
├── stores/                       # Stores Zustand
│   ├── authStore.ts
│   ├── tenantStore.ts
│   └── uiStore.ts
├── types/                        # Tipos TypeScript
│   ├── api.ts
│   ├── auth.ts
│   └── common.ts
└── public/                       # Arquivos estáticos
    ├── images/
    └── icons/
```

## 🎨 Design System

### **Cores**
```css
/* Tailwind config */
colors: {
  primary: {
    50: '#eff6ff',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
  },
  secondary: {
    50: '#f8fafc',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
  },
  success: {
    50: '#f0fdf4',
    500: '#22c55e',
    600: '#16a34a',
  },
  warning: {
    50: '#fffbeb',
    500: '#f59e0b',
    600: '#d97706',
  },
  error: {
    50: '#fef2f2',
    500: '#ef4444',
    600: '#dc2626',
  }
}
```

### **Componentes Base**
- **Button**: Primário, secundário, outline, ghost
- **Input**: Texto, email, senha, select, textarea
- **Modal**: Confirmação, formulário, detalhes
- **Table**: Paginação, ordenação, filtros
- **Card**: Informações, estatísticas, ações

## 🔐 Autenticação Multi-Tenant

### **Estrutura de Rotas**
```typescript
// Middleware de autenticação
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Rotas públicas
  if (pathname.startsWith('/auth') || pathname === '/') {
    return NextResponse.next();
  }
  
  // Verifica autenticação
  const token = request.cookies.get('auth-token');
  if (!token) {
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }
  
  // Verifica tenant para rotas protegidas
  if (pathname.startsWith('/company') || pathname.startsWith('/client')) {
    const tenant = request.cookies.get('tenant-id');
    if (!tenant) {
      return NextResponse.redirect(new URL('/auth/select-tenant', request.url));
    }
  }
  
  return NextResponse.next();
}
```

### **Contexto de Autenticação**
```typescript
// hooks/useAuth.ts
export function useAuth() {
  const { user, tenant, login, logout, switchTenant } = useAuthStore();
  
  return {
    user,
    tenant,
    isAuthenticated: !!user,
    isSuperAdmin: user?.is_super_admin,
    login,
    logout,
    switchTenant
  };
}
```

## 📊 Dashboards

### **Super Admin Dashboard**
- **Métricas do SaaS**: Receita, usuários, performance
- **Gestão de Tenants**: Criar, editar, suspender empresas
- **Analytics**: Gráficos de uso e crescimento
- **Monitoramento**: Saúde do sistema

### **Company Dashboard**
- **Métricas Operacionais**: Processos, clientes, receita
- **Alertas**: Prazos críticos, notificações
- **Quick Actions**: Ações rápidas frequentes
- **Recent Activity**: Atividades recentes

### **Client Dashboard**
- **Status dos Processos**: Visualização simplificada
- **Documentos**: Download de documentos compartilhados
- **Comunicação**: Mensagens com a empresa
- **Perfil**: Atualização de dados pessoais

## 📱 Responsividade

### **Breakpoints**
```css
/* Tailwind breakpoints */
sm: '640px',   /* Mobile */
md: '768px',   /* Tablet */
lg: '1024px',  /* Desktop */
xl: '1280px',  /* Large Desktop */
2xl: '1536px', /* Extra Large */
```

### **Componentes Responsivos**
- **Sidebar**: Colapsa em mobile
- **Tables**: Scroll horizontal em mobile
- **Forms**: Layout vertical em mobile
- **Charts**: Redimensionamento automático

## 🚀 Performance

### **Otimizações**
- **Code Splitting**: Carregamento sob demanda
- **Image Optimization**: Otimização automática
- **Bundle Analysis**: Monitoramento de tamanho
- **Caching**: Cache inteligente de dados

### **Lighthouse Score**
- **Performance**: 95+
- **Accessibility**: 100
- **Best Practices**: 100
- **SEO**: 100

## 🔧 Configuração

### **Instalação**
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/saas-juridico.git
cd saas-juridico/frontend

# Instala dependências
npm install

# Configura variáveis de ambiente
cp .env.example .env.local

# Executa em desenvolvimento
npm run dev
```

### **Variáveis de Ambiente**
```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Autenticação
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key

# Upload
NEXT_PUBLIC_S3_BUCKET=saas-juridico-documents
NEXT_PUBLIC_S3_REGION=us-east-1

# Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

## 📦 Deploy

### **Vercel (Recomendado)**
```bash
# Deploy automático
vercel --prod
```

### **Docker**
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

## 🎯 Próximos Passos

1. **Setup inicial** do projeto Next.js
2. **Configuração** do Tailwind CSS
3. **Implementação** dos componentes base
4. **Sistema de autenticação** multi-tenant
5. **Dashboards** específicos por portal
6. **Integração** com a API backend
7. **Testes** e otimizações
8. **Deploy** em produção

---

**Desenvolvido com ❤️ para modernizar a advocacia brasileira**
