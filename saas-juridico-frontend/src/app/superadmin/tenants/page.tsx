'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import SuperAdminLayout from '@/components/layout/SuperAdminLayout';
import { useSuperAdminAuth } from '@/hooks/useSuperAdminAuth';
import { 
  Building2, 
  Search, 
  Plus, 
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Users,
  Activity,
  Pause,
  Play
} from 'lucide-react';

interface Tenant {
  id: string;
  name: string;
  slug: string;
  email: string;
  phone: string;
  plan_type: string;
  is_active: boolean;
  is_suspended: boolean;
  created_at: string;
  user_count: number;
  process_count: number;
}

export default function TenantsPage() {
  const router = useRouter();
  const { token, isInitialized } = useSuperAdminAuth();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    if (isInitialized) {
      fetchTenants();
    }
  }, [isInitialized]);

  const fetchTenants = async () => {
    try {
      console.log('Token no fetchTenants:', token);
      if (!token) {
        throw new Error('Token não encontrado');
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/superadmin/tenants`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Erro ao carregar empresas');
      }

      const data = await response.json();
      setTenants(data);

    } catch (error) {
      setError(error instanceof Error ? error.message : 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredTenants = tenants.filter(tenant => {
    const matchesSearch = tenant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tenant.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tenant.slug.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' ||
                         (statusFilter === 'active' && tenant.is_active && !tenant.is_suspended) ||
                         (statusFilter === 'suspended' && tenant.is_suspended) ||
                         (statusFilter === 'inactive' && !tenant.is_active);

    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (tenant: Tenant) => {
    if (tenant.is_suspended) {
      return <Badge variant="destructive">Suspensa</Badge>;
    }
    if (tenant.is_active) {
      return <Badge variant="default">Ativa</Badge>;
    }
    return <Badge variant="secondary">Inativa</Badge>;
  };

  const getPlanBadge = (planType: string) => {
    const planColors = {
      'basic': 'bg-blue-100 text-blue-800',
      'professional': 'bg-purple-100 text-purple-800',
      'enterprise': 'bg-green-100 text-green-800',
      'premium': 'bg-yellow-100 text-yellow-800'
    };
    
    return (
      <Badge variant="outline" className={planColors[planType as keyof typeof planColors] || 'bg-gray-100 text-gray-800'}>
        {planType}
      </Badge>
    );
  };

  const handleStatusChange = async (tenantId: string, action: 'activate' | 'suspend' | 'deactivate') => {
    try {
      let endpoint = '';
      let method = 'POST';

      switch (action) {
        case 'activate':
          endpoint = `/superadmin/tenants/${tenantId}/activate`;
          break;
        case 'suspend':
          endpoint = `/superadmin/tenants/${tenantId}/suspend`;
          break;
        case 'deactivate':
          endpoint = `/superadmin/tenants/${tenantId}`;
          method = 'DELETE';
          break;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}${endpoint}`,
        {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          ...(action === 'suspend' && { body: JSON.stringify({ reason: 'Suspensão administrativa' }) }),
        }
      );

      if (!response.ok) {
        throw new Error(`Erro ao ${action === 'activate' ? 'ativar' : action === 'suspend' ? 'suspender' : 'desativar'} tenant`);
      }

      // Recarregar lista
      await fetchTenants();
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Erro ao alterar status');
    }
  };

  const handleDelete = async (tenantId: string, tenantName: string) => {
    if (!confirm(`Tem certeza que deseja excluir a empresa "${tenantName}"? Esta ação não pode ser desfeita.`)) {
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/superadmin/tenants/${tenantId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Erro ao excluir empresa');
      }

      // Recarregar lista
      await fetchTenants();
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Erro ao excluir');
    }
  };

  if (isLoading) {
    return (
      <SuperAdminLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p>Carregando empresas...</p>
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
            <Button onClick={fetchTenants} className="mt-4">
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
            <h1 className="text-2xl font-bold text-gray-900">Empresas</h1>
            <p className="text-gray-600">Gerencie todas as empresas do sistema</p>
          </div>
          <Button onClick={() => router.push('/superadmin/tenants/new')}>
            <Plus className="h-4 w-4 mr-2" />
            Nova Empresa
          </Button>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Buscar empresas..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filtrar por status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os status</SelectItem>
                  <SelectItem value="active">Ativas</SelectItem>
                  <SelectItem value="suspended">Suspensas</SelectItem>
                  <SelectItem value="inactive">Inativas</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <Building2 className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total</p>
                  <p className="text-2xl font-bold text-gray-900">{tenants.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <CheckCircle className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Ativas</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {tenants.filter(t => t.is_active && !t.is_suspended).length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <XCircle className="h-8 w-8 text-red-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Suspensas</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {tenants.filter(t => t.is_suspended).length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <Users className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Usuários</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {tenants.reduce((sum, t) => sum + (t.user_count || 0), 0)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tenants List */}
        <Card>
          <CardHeader>
            <CardTitle>Lista de Empresas</CardTitle>
            <CardDescription>
              {filteredTenants.length} empresa(s) encontrada(s)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredTenants.map((tenant) => (
                <div key={tenant.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Building2 className="h-6 w-6 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium">{tenant.name}</h4>
                        {getStatusBadge(tenant)}
                        {getPlanBadge(tenant.plan_type)}
                      </div>
                      <p className="text-sm text-gray-600">{tenant.email}</p>
                      <p className="text-xs text-gray-500">
                        Slug: {tenant.slug} • Criada em {new Date(tenant.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-sm font-medium">{tenant.user_count || 0} usuários</p>
                      <p className="text-xs text-gray-500">{tenant.process_count || 0} processos</p>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => router.push(`/superadmin/tenants/${tenant.id}`)}
                        title="Ver detalhes"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => router.push(`/superadmin/tenants/${tenant.id}`)}>
                            <Eye className="h-4 w-4 mr-2" />
                            Ver detalhes
                          </DropdownMenuItem>
                          
                          {tenant.is_suspended ? (
                            <DropdownMenuItem onClick={() => handleStatusChange(tenant.id, 'activate')}>
                              <Play className="h-4 w-4 mr-2" />
                              Reativar
                            </DropdownMenuItem>
                          ) : tenant.is_active ? (
                            <DropdownMenuItem onClick={() => handleStatusChange(tenant.id, 'suspend')}>
                              <Pause className="h-4 w-4 mr-2" />
                              Suspender
                            </DropdownMenuItem>
                          ) : (
                            <DropdownMenuItem onClick={() => handleStatusChange(tenant.id, 'activate')}>
                              <Play className="h-4 w-4 mr-2" />
                              Ativar
                            </DropdownMenuItem>
                          )}
                          
                          <DropdownMenuItem 
                            onClick={() => handleDelete(tenant.id, tenant.name)}
                            className="text-red-600"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Excluir
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredTenants.length === 0 && (
                <div className="text-center py-8">
                  <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Nenhuma empresa encontrada</p>
                  <p className="text-sm text-gray-400">Tente ajustar os filtros de busca</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </SuperAdminLayout>
  );
}
