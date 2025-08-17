import { useEffect, useState } from 'react';
import { useSuperAdminStore } from '@/stores/superAdminStore';

export function useSuperAdminAuth() {
  const { token, isAuthenticated, isLoading } = useSuperAdminStore();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Aguardar a hidratação do Zustand
    const timer = setTimeout(() => {
      setIsInitialized(true);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  // Verificar se há token no localStorage como fallback
  const getToken = () => {
    if (token) return token;
    if (typeof window !== 'undefined') {
      // Primeiro tenta o token específico do super admin
      const superAdminToken = localStorage.getItem('superadmin_token');
      if (superAdminToken) return superAdminToken;
      
      // Se não existe, verifica se há um token normal de super admin
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        try {
          // Decodifica o token para verificar se é de super admin
          const payload = JSON.parse(atob(accessToken.split('.')[1]));
          if (payload.is_super_admin === true) {
            return accessToken;
          }
        } catch (error) {
          // Token inválido, ignora
        }
      }
    }
    return null;
  };

  const isAuthReady = isInitialized && !isLoading;
  const hasToken = !!getToken();

  return {
    token: getToken(),
    isAuthenticated: isAuthenticated || hasToken,
    isLoading,
    isInitialized: isAuthReady,
    hasToken,
  };
}
