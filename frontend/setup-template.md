# 🚀 Setup do Template Recomendado

## **Shadcn/ui + Next.js 14 + TypeScript**

### **1. Criação do Projeto**
```bash
# Cria projeto Next.js
npx create-next-app@latest saas-juridico-frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"

cd saas-juridico-frontend
```

### **2. Instalação do Shadcn/ui**
```bash
# Inicializa Shadcn/ui
npx shadcn@latest init

# Respostas recomendadas:
# ✔ Would you like to use TypeScript (recommended)? yes
# ✔ Which style would you like to use? › Default
# ✔ Which color would you like to use as base color? › Slate
# ✔ Where is your global CSS file? › app/globals.css
# ✔ Would you like to use CSS variables for colors? › yes
# ✔ Where is your tailwind.config.js located? › tailwind.config.js
# ✔ Configure the import alias for components: › @/components
# ✔ Configure the import alias for utils: › @/lib/utils
# ✔ Are you using React Server Components? › yes
```

### **3. Instalação de Componentes**
```bash
# Componentes essenciais
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
npx shadcn@latest add table
npx shadcn@latest add form
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
npx shadcn@latest add navigation-menu
npx shadcn@latest add avatar
npx shadcn@latest add badge
npx shadcn@latest add toast
npx shadcn@latest add tabs
npx shadcn@latest add select
npx shadcn@latest add textarea
npx shadcn@latest add checkbox
npx shadcn@latest add radio-group
npx shadcn@latest add switch
npx shadcn@latest add progress
npx shadcn@latest add alert
npx shadcn@latest add sheet
npx shadcn@latest add separator
npx shadcn@latest add skeleton
```

### **4. Dependências Adicionais**
```bash
# State Management
npm install zustand @tanstack/react-query

# Forms
npm install react-hook-form @hookform/resolvers zod

# Charts
npm install recharts

# Tables
npm install @tanstack/react-table

# Authentication
npm install next-auth

# Notifications
npm install react-hot-toast

# Date/Time
npm install date-fns

# File Upload
npm install react-dropzone

# Rich Text Editor
npm install @tiptap/react @tiptap/pm @tiptap/starter-kit

# Icons
npm install lucide-react

# Utilities
npm install clsx tailwind-merge
```

### **5. Estrutura de Pastas**
```bash
mkdir -p src/{components,lib,hooks,stores,types,app}
mkdir -p src/components/{ui,forms,charts,layout,features}
mkdir -p src/app/{auth,company,client,superadmin}
```

### **6. Configuração do TypeScript**
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/hooks/*": ["./src/hooks/*"],
      "@/stores/*": ["./src/stores/*"],
      "@/types/*": ["./src/types/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### **7. Configuração do Tailwind**
```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

### **8. Executar o Projeto**
```bash
# Desenvolvimento
npm run dev

# Build
npm run build

# Produção
npm start
```

## **🎨 Templates Alternativos**

### **Opção 2: Next.js SaaS Starter Kit**
```bash
git clone https://github.com/boxyhq/saas-starter-kit.git saas-juridico-frontend
cd saas-juridico-frontend
npm install
```

### **Opção 3: Precedent (Enterprise)**
```bash
git clone https://github.com/steven-tey/precedent.git saas-juridico-frontend
cd saas-juridico-frontend
npm install
```

## **💰 Templates Premium**

### **ThemeForest**
- **Legal Dashboard**: $25-50
- **SaaS Admin**: $30-60
- **Law Firm**: $20-40

### **Creative Tim**
- **Next.js Admin**: $99
- **Material Dashboard**: $149
- **Corporate UI**: $199

---

**Recomendação: Shadcn/ui + Next.js 14** - Melhor custo-benefício e flexibilidade! 🚀
