'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import SuperAdminLayout from '@/components/layout/SuperAdminLayout';
import { useSuperAdminStore } from '@/stores/superAdminStore';
import { 
  Building2, 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  Shield, 
  Activity,
  DollarSign,
  Database,
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface DashboardStats {
  total_tenants: number;
  active_tenants: number;
  suspended_tenants: number;
  total_users: number;
  active_users: number;
  new_tenants_30_days: number;
  revenue_month: number;
  system_health: 'healthy' | 'warning' | 'critical';
  active_sessions: number;
  storage_used: number;
  storage_total: number;
}

interface Tenant {
  id: string;
  name: string;
  slug: string;
  email: string;
  plan_type: string;
  is_active: boolean;
  is_suspended: boolean;
  created_at: string;
  user_count: number;
  process_count: number;
}

export default function SuperAdminDashboard() {
  const { token } = useSuperAdminStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentTenants, setRecentTenants] = useState<Tenant[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Função auxiliar para formatar números com segurança
  const formatNumber = (value: number | undefined | null, decimals = 1): string => {
    if (value === null || value === undefined || isNaN(value)) {
      return '0';
    }
    return value.toFixed(decimals);
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      if (!token) {
        throw new Error('Token não encontrado');
      }

      // Buscar estatísticas gerais
              const statsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/superadmin/dashboard/overview`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!statsResponse.ok) {
        throw new Error('Erro ao carregar estatísticas');
      }

      const statsData = await statsResponse.json();
      setStats(statsData);

      // Buscar tenants recentes
      const tenantsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/superadmin/tenants?limit=5`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (tenantsResponse.ok) {
        const tenantsData = await tenantsResponse.json();
        setRecentTenants(tenantsData);
      }

    } catch (error) {
      setError(error instanceof Error ? error.message : 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
  };

  const getSystemHealthColor = (health: string) => {
    switch (health) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'critical':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getSystemHealthIcon = (health: string) => {
    switch (health) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4" />;
      case 'critical':
        return <XCircle className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  if (isLoading) {
    return (
      <SuperAdminLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p>Carregando dashboard...</p>
          </div>
        </div>
      </SuperAdminLayout>
    );
  }

  if (error) {
    return (
      <SuperAdminLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-4" />
            <p className="text-red-600">{error}</p>
            <Button onClick={fetchDashboardData} className="mt-4">
              Tentar Novamente
            </Button>
          </div>
        </div>
      </SuperAdminLayout>
    );
  }

  return (
    <SuperAdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600">Visão geral do sistema SaaS Jurídico</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className={getSystemHealthColor(stats?.system_health || 'healthy')}>
              {getSystemHealthIcon(stats?.system_health || 'healthy')}
              <span className="ml-1">Sistema {stats?.system_health || 'healthy'}</span>
            </Badge>
            <Button variant="outline" size="sm">
              <Clock className="h-4 w-4 mr-2" />
              Última atualização: {new Date().toLocaleTimeString()}
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Empresas</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.total_tenants || 0}</div>
              <p className="text-xs text-muted-foreground">
                +{stats?.new_tenants_30_days || 0} nos últimos 30 dias
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Empresas Ativas</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats?.active_tenants || 0}</div>
              <p className="text-xs text-muted-foreground">
                {stats?.suspended_tenants || 0} suspensas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Usuários</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
              <p className="text-xs text-muted-foreground">
                {stats?.active_users || 0} ativos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Receita Mensal</CardTitle>
              <DollarSign className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                R$ {(stats?.revenue_month || 0).toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                <TrendingUp className="h-3 w-3 inline mr-1" />
                +12% vs mês anterior
              </p>
            </CardContent>
          </Card>
        </div>

        {/* System Health & Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Sistema e Performance</CardTitle>
              <CardDescription>Métricas de saúde e performance do sistema</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Sessões Ativas</span>
                    <span className="font-medium">{stats?.active_sessions || 0}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${Math.min((stats?.active_sessions || 0) / 100 * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Armazenamento</span>
                    <span className="font-medium">
                      {formatNumber((stats?.storage_used || 0) / (1024 * 1024 * 1024))}GB / 
                      {formatNumber((stats?.storage_total || 0) / (1024 * 1024 * 1024))}GB
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{ width: `${Math.min(((stats?.storage_used || 0) / Math.max(stats?.storage_total || 1, 1)) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Ações Rápidas</CardTitle>
              <CardDescription>Operações comuns do sistema</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <Building2 className="h-4 w-4 mr-2" />
                Nova Empresa
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Users className="h-4 w-4 mr-2" />
                Gerenciar Usuários
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Database className="h-4 w-4 mr-2" />
                Backup Manual
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Shield className="h-4 w-4 mr-2" />
                Configurações
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Recent Tenants */}
        <Card>
          <CardHeader>
            <CardTitle>Empresas Recentes</CardTitle>
            <CardDescription>Últimas empresas cadastradas no sistema</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentTenants.map((tenant) => (
                <div key={tenant.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <Building2 className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="font-medium">{tenant.name}</h4>
                      <p className="text-sm text-gray-600">{tenant.email}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant={tenant.is_active ? "default" : "secondary"}>
                          {tenant.is_active ? 'Ativa' : 'Inativa'}
                        </Badge>
                        <Badge variant="outline">{tenant.plan_type}</Badge>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">
                      {new Date(tenant.created_at).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-gray-500">
                      {tenant.user_count || 0} usuários • {tenant.process_count || 0} processos
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </SuperAdminLayout>
  );
}
