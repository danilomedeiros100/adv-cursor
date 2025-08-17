'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: any;
  tenant: any;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  isLoading: true,
  user: null,
  tenant: null,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading, user, tenant, checkAuthStatus } = useAuthStore();
  const [isInitialized, setIsInitialized] = useState(false);

  // Rotas que não precisam de autenticação
  const publicRoutes = ['/auth/login', '/auth/register', '/', '/debug-auth'];
  const isPublicRoute = publicRoutes.some(route => pathname?.startsWith(route));

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        await checkAuthStatus();
      } catch (error) {
        console.error('Erro ao inicializar autenticação:', error);
      } finally {
        setIsInitialized(true);
      }
    };

    initializeAuth();
  }, [checkAuthStatus]);

  useEffect(() => {
    if (!isInitialized) return;

    // Se não está autenticado e não está em uma rota pública, redireciona para login
    if (!isAuthenticated && !isPublicRoute) {
      console.log('Usuário não autenticado, redirecionando para login');
      router.push('/auth/login');
      return;
    }

    // Se está autenticado e está na página de login, redireciona para o dashboard correto
    if (isAuthenticated && pathname === '/auth/login') {
      console.log('Usuário autenticado, redirecionando para dashboard');
      if (user?.is_super_admin) {
        router.push('/superadmin/dashboard');
      } else {
        router.push('/company/dashboard');
      }
      return;
    }
  }, [isAuthenticated, isPublicRoute, pathname, isInitialized, router]);

  // Mostra loading enquanto inicializa
  if (!isInitialized || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, user, tenant }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuthContext = () => useContext(AuthContext);
