'use client';

import { useAuth } from '@/hooks/useAuth';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function DebugAuthPage() {
  const { user, tenant, isAuthenticated, isLoading, error, token, isClient, isInitialized } = useAuth();
  const [localStorageToken, setLocalStorageToken] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      setLocalStorageToken(token);
    }
  }, []);

  const handleLogin = async () => {
    try {
      const response = await fetch('/api/v1/auth/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'joao.silva@escritorioteste.com.br',
          password: '123456',
          tenant_slug: 'escritorio-teste'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        window.location.reload();
      } else {
        console.error('Erro no login:', await response.text());
      }
    } catch (error) {
      console.error('Erro:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    window.location.reload();
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Debug de Autenticação</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Status da Autenticação</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p><strong>isClient:</strong> {isClient ? '✅ Sim' : '❌ Não'}</p>
            <p><strong>isInitialized:</strong> {isInitialized ? '✅ Sim' : '❌ Não'}</p>
            <p><strong>isLoading:</strong> {isLoading ? '✅ Sim' : '❌ Não'}</p>
            <p><strong>isAuthenticated:</strong> {isAuthenticated ? '✅ Sim' : '❌ Não'}</p>
            <p><strong>Token do Hook:</strong> {token ? '✅ Presente' : '❌ Ausente'}</p>
            <p><strong>Token do localStorage:</strong> {localStorageToken ? '✅ Presente' : '❌ Ausente'}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Dados do Usuário</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {user ? (
              <>
                <p><strong>Nome:</strong> {user.name}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Super Admin:</strong> {user.is_super_admin ? '✅ Sim' : '❌ Não'}</p>
              </>
            ) : (
              <p>❌ Nenhum usuário logado</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Dados do Tenant</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {tenant ? (
              <>
                <p><strong>Nome:</strong> {tenant.name}</p>
                <p><strong>Slug:</strong> {tenant.slug}</p>
                <p><strong>Email:</strong> {tenant.email}</p>
              </>
            ) : (
              <p>❌ Nenhum tenant associado</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Erros</CardTitle>
          </CardHeader>
          <CardContent>
            {error ? (
              <p className="text-red-600">{error}</p>
            ) : (
              <p className="text-green-600">✅ Nenhum erro</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Ações</CardTitle>
        </CardHeader>
        <CardContent className="space-x-4">
          <Button onClick={handleLogin} disabled={isAuthenticated}>
            Fazer Login
          </Button>
          <Button onClick={handleLogout} disabled={!isAuthenticated} variant="destructive">
            Fazer Logout
          </Button>
          <Button onClick={() => window.location.reload()}>
            Recarregar Página
          </Button>
        </CardContent>
      </Card>

      {token && (
        <Card>
          <CardHeader>
            <CardTitle>Token (Primeiros 50 caracteres)</CardTitle>
          </CardHeader>
          <CardContent>
            <code className="text-sm bg-gray-100 p-2 rounded">
              {token.substring(0, 50)}...
            </code>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
