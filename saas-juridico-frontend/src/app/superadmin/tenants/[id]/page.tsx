'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, Edit, Save, X, Trash2, AlertTriangle, CheckCircle, Pause } from 'lucide-react';
import SuperAdminLayout from '@/components/layout/SuperAdminLayout';
import { useSuperAdminStore } from '@/stores/superAdminStore';

interface Tenant {
  id: string;
  name: string;
  slug: string;
  email: string;
  phone: string | null;
  plan_type: string;
  plan_features: Record<string, any>;
  max_users: number;
  max_processes: number;
  is_active: boolean;
  is_suspended: boolean;
  settings: Record<string, any>;
  branding: Record<string, any>;
  created_at: string;
}

export default function TenantDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const { token } = useSuperAdminStore();
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<Tenant>>({});

  const tenantId = params.id as string;

  useEffect(() => {
    fetchTenant();
  }, [tenantId]);

  const fetchTenant = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/superadmin/tenants/${tenantId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Erro ao carregar dados do tenant');
      }

      const data = await response.json();
      setTenant(data);
      setFormData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/superadmin/tenants/${tenantId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        throw new Error('Erro ao atualizar tenant');
      }

      const updatedTenant = await response.json();
      setTenant(updatedTenant);
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar');
    } finally {
      setIsSaving(false);
    }
  };

  const handleStatusChange = async (action: 'activate' | 'suspend' | 'deactivate') => {
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

      // Recarregar dados do tenant
      await fetchTenant();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao alterar status');
    }
  };

  const handleDelete = async () => {
    if (!confirm('Tem certeza que deseja excluir este tenant? Esta ação não pode ser desfeita.')) {
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
        throw new Error('Erro ao excluir tenant');
      }

      router.push('/superadmin/tenants');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao excluir');
    }
  };

  if (isLoading) {
    return (
      <SuperAdminLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Carregando...</div>
        </div>
      </SuperAdminLayout>
    );
  }

  if (error) {
    return (
      <SuperAdminLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">Erro: {error}</div>
        </div>
      </SuperAdminLayout>
    );
  }

  if (!tenant) {
    return (
      <SuperAdminLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Tenant não encontrado</div>
        </div>
      </SuperAdminLayout>
    );
  }

  return (
    <SuperAdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/superadmin/tenants')}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Voltar
            </Button>
            <div>
              <h1 className="text-2xl font-bold">{tenant.name}</h1>
              <p className="text-muted-foreground">Detalhes da empresa</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {isEditing ? (
              <>
                <Button
                  onClick={handleSave}
                  disabled={isSaving}
                  size="sm"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {isSaving ? 'Salvando...' : 'Salvar'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsEditing(false);
                    setFormData(tenant);
                  }}
                  size="sm"
                >
                  <X className="h-4 w-4 mr-2" />
                  Cancelar
                </Button>
              </>
            ) : (
              <Button
                onClick={() => setIsEditing(true)}
                size="sm"
              >
                <Edit className="h-4 w-4 mr-2" />
                Editar
              </Button>
            )}
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex items-center space-x-2">
          {tenant.is_suspended ? (
            <Badge variant="destructive" className="flex items-center space-x-1">
              <Pause className="h-3 w-3" />
              <span>Suspenso</span>
            </Badge>
          ) : tenant.is_active ? (
            <Badge variant="default" className="flex items-center space-x-1">
              <CheckCircle className="h-3 w-3" />
              <span>Ativo</span>
            </Badge>
          ) : (
            <Badge variant="secondary" className="flex items-center space-x-1">
              <AlertTriangle className="h-3 w-3" />
              <span>Inativo</span>
            </Badge>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Informações Básicas */}
          <Card>
            <CardHeader>
              <CardTitle>Informações Básicas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Nome</Label>
                  {isEditing ? (
                    <Input
                      id="name"
                      value={formData.name || ''}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{tenant.name}</p>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="slug">Slug</Label>
                  <p className="text-sm text-muted-foreground">{tenant.slug}</p>
                </div>
                
                <div>
                  <Label htmlFor="email">Email</Label>
                  {isEditing ? (
                    <Input
                      id="email"
                      type="email"
                      value={formData.email || ''}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{tenant.email}</p>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="phone">Telefone</Label>
                  {isEditing ? (
                    <Input
                      id="phone"
                      value={formData.phone || ''}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{tenant.phone || 'Não informado'}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Plano e Limites */}
          <Card>
            <CardHeader>
              <CardTitle>Plano e Limites</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="plan_type">Tipo de Plano</Label>
                  {isEditing ? (
                    <Select
                      value={formData.plan_type || ''}
                      onValueChange={(value) => setFormData({ ...formData, plan_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="free">Free</SelectItem>
                        <SelectItem value="premium">Premium</SelectItem>
                        <SelectItem value="enterprise">Enterprise</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <Badge variant="outline">{tenant.plan_type}</Badge>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="max_users">Máx. Usuários</Label>
                  {isEditing ? (
                    <Input
                      id="max_users"
                      type="number"
                      value={formData.max_users || 0}
                      onChange={(e) => setFormData({ ...formData, max_users: parseInt(e.target.value) })}
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{tenant.max_users}</p>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="max_processes">Máx. Processos</Label>
                  {isEditing ? (
                    <Input
                      id="max_processes"
                      type="number"
                      value={formData.max_processes || 0}
                      onChange={(e) => setFormData({ ...formData, max_processes: parseInt(e.target.value) })}
                    />
                  ) : (
                    <p className="text-sm text-muted-foreground">{tenant.max_processes}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Configurações */}
          <Card>
            <CardHeader>
              <CardTitle>Configurações</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <Label>Fuso Horário</Label>
                  <p className="text-sm text-muted-foreground">
                    {tenant.settings?.timezone || 'America/Sao_Paulo'}
                  </p>
                </div>
                <div>
                  <Label>Idioma</Label>
                  <p className="text-sm text-muted-foreground">
                    {tenant.settings?.language || 'pt_BR'}
                  </p>
                </div>
                <div>
                  <Label>Moeda</Label>
                  <p className="text-sm text-muted-foreground">
                    {tenant.settings?.currency || 'BRL'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Ações */}
          <Card>
            <CardHeader>
              <CardTitle>Ações</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {tenant.is_suspended ? (
                <Button
                  onClick={() => handleStatusChange('activate')}
                  className="w-full"
                  variant="default"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Reativar Tenant
                </Button>
              ) : tenant.is_active ? (
                <Button
                  onClick={() => handleStatusChange('suspend')}
                  className="w-full"
                  variant="outline"
                >
                  <Pause className="h-4 w-4 mr-2" />
                  Suspender Tenant
                </Button>
              ) : (
                <Button
                  onClick={() => handleStatusChange('activate')}
                  className="w-full"
                  variant="default"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Ativar Tenant
                </Button>
              )}
              
              <Button
                onClick={handleDelete}
                className="w-full"
                variant="destructive"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Excluir Tenant
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Informações Adicionais */}
        <Card>
          <CardHeader>
            <CardTitle>Informações Adicionais</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label>Data de Criação</Label>
                <p className="text-sm text-muted-foreground">
                  {new Date(tenant.created_at).toLocaleDateString('pt-BR')}
                </p>
              </div>
              <div>
                <Label>ID do Tenant</Label>
                <p className="text-sm text-muted-foreground font-mono">{tenant.id}</p>
              </div>
              <div>
                <Label>Funcionalidades do Plano</Label>
                <div className="flex flex-wrap gap-1 mt-1">
                  {tenant.plan_features?.modules?.map((module: string) => (
                    <Badge key={module} variant="secondary" className="text-xs">
                      {module}
                    </Badge>
                  )) || <span className="text-sm text-muted-foreground">Nenhuma funcionalidade</span>}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </SuperAdminLayout>
  );
}
