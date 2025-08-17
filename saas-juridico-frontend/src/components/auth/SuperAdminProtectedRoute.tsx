'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSuperAdminAuth } from '@/hooks/useSuperAdminAuth';

interface SuperAdminProtectedRouteProps {
  children: React.ReactNode;
}

export function SuperAdminProtectedRoute({ children }: SuperAdminProtectedRouteProps) {
  const { isAuthenticated, isLoading, isInitialized } = useSuperAdminAuth();
  const router = useRouter();

  useEffect(() => {
    if (isInitialized && !isLoading && !isAuthenticated) {
      router.push('/superadmin/login');
      return;
    }
  }, [isAuthenticated, isLoading, isInitialized, router]);

  // Mostra loading enquanto verifica autenticação
  if (isLoading || !isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  // Se não está autenticado, não renderiza nada (será redirecionado)
  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
