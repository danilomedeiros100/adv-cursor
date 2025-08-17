'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'company' | 'superadmin' | 'client';
}

export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user, tenant } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
      return;
    }

    if (!isLoading && isAuthenticated && requiredRole) {
      // Verificar se o usuário tem a role necessária
      const hasRequiredRole = (() => {
        switch (requiredRole) {
          case 'superadmin':
            return user?.is_super_admin;
          case 'company':
            return !user?.is_super_admin;
          case 'client':
            return !tenant && !user?.is_super_admin;
          default:
            return true;
        }
      })();

      if (!hasRequiredRole) {
        router.push('/auth/login');
        return;
      }
    }
  }, [isAuthenticated, isLoading, user, tenant, requiredRole, router]);

  // Mostra loading enquanto verifica autenticação
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  // Se não está autenticado, não renderiza nada (será redirecionado)
  if (!isAuthenticated) {
    return null;
  }

  // Se tem role específica, verifica se tem permissão
  if (requiredRole) {
    const hasRequiredRole = (() => {
      switch (requiredRole) {
        case 'superadmin':
          return user?.is_super_admin;
        case 'company':
          return !user?.is_super_admin;
        case 'client':
          return !tenant && !user?.is_super_admin;
        default:
          return true;
      }
    })();

    if (!hasRequiredRole) {
      return null;
    }
  }

  return <>{children}</>;
}
