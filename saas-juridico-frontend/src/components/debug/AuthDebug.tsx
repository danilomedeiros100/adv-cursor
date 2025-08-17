'use client';

import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useEffect, useState } from 'react';

export function AuthDebug() {
  const { 
    user, 
    tenant, 
    isAuthenticated, 
    isLoading, 
    error,
    isSuperAdmin,
    isCompanyUser,
    isClientUser,
    logout,
    checkAuthStatus
  } = useAuth();

  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const clearStorage = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('auth-storage');
      sessionStorage.clear();
      window.location.reload();
    }
  };

  const getTokenInfo = () => {
    if (typeof window === 'undefined') {
      return 'Executando no servidor';
    }
    
    const token = localStorage.getItem('access_token');
    if (!token) return 'Nenhum token encontrado';
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        exp: new Date(payload.exp * 1000).toLocaleString(),
        user_id: payload.sub,
        email: payload.email,
        is_super_admin: payload.is_super_admin,
        tenant_id: payload.tenant_id,
        tenant_slug: payload.tenant_slug
      };
    } catch (error) {
      return 'Token inválido';
    }
  };

  if (!isClient) {
    return (
      <div className="p-4">
        <Card>
          <CardHeader>
            <CardTitle>Debug de Autenticação</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Carregando...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Debug de Autenticação
            <div className="flex gap-2">
              <Button size="sm" onClick={checkAuthStatus} disabled={isLoading}>
                Verificar Status
              </Button>
              <Button size="sm" variant="outline" onClick={clearStorage}>
                Limpar Storage
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Status Geral */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-500">Status</div>
              <Badge variant={isAuthenticated ? "default" : "secondary"}>
                {isAuthenticated ? "Autenticado" : "Não Autenticado"}
              </Badge>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-500">Carregando</div>
              <Badge variant={isLoading ? "default" : "secondary"}>
                {isLoading ? "Sim" : "Não"}
              </Badge>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-500">Tipo de Usuário</div>
              <Badge variant="outline">
                {isSuperAdmin ? "Super Admin" : isCompanyUser ? "Empresa" : isClientUser ? "Cliente" : "N/A"}
              </Badge>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-500">Tenant</div>
              <Badge variant="outline">
                {tenant ? "Sim" : "Não"}
              </Badge>
            </div>
          </div>

          {/* Token Info */}
          <div>
            <h4 className="font-semibold mb-2">Informações do Token</h4>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
              {JSON.stringify(getTokenInfo(), null, 2)}
            </pre>
          </div>

          {/* User Info */}
          {user && (
            <div>
              <h4 className="font-semibold mb-2">Dados do Usuário</h4>
              <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
                {JSON.stringify(user, null, 2)}
              </pre>
            </div>
          )}

          {/* Tenant Info */}
          {tenant && (
            <div>
              <h4 className="font-semibold mb-2">Dados do Tenant</h4>
              <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
                {JSON.stringify(tenant, null, 2)}
              </pre>
            </div>
          )}

          {/* Error */}
          {error && (
            <div>
              <h4 className="font-semibold mb-2 text-red-600">Erro</h4>
              <div className="bg-red-50 p-2 rounded text-red-700">
                {error}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            <Button onClick={logout} variant="destructive">
              Logout
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
