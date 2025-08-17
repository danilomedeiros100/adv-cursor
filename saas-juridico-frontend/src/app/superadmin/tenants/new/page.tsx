'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { ArrowLeft, Building2, Save, X } from 'lucide-react';
import SuperAdminLayout from '@/components/layout/SuperAdminLayout';
import { useSuperAdminAuth } from '@/hooks/useSuperAdminAuth';

const createTenantSchema = z.object({
  name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  slug: z.string().min(2, 'Slug deve ter pelo menos 2 caracteres').regex(/^[a-z0-9-]+$/, 'Slug deve conter apenas letras minúsculas, números e hífens'),
  email: z.string().email('Email inválido'),
  phone: z.string().optional(),
  plan_type: z.enum(['free', 'premium', 'enterprise']),
  max_users: z.number().min(1, 'Mínimo 1 usuário').max(1000, 'Máximo 1000 usuários'),
  max_processes: z.number().min(10, 'Mínimo 10 processos').max(10000, 'Máximo 10000 processos'),
  // Campos do usuário owner
  owner_name: z.string().min(2, 'Nome do proprietário deve ter pelo menos 2 caracteres'),
  owner_password: z.string().min(6, 'Senha deve ter pelo menos 6 caracteres'),
  owner_phone: z.string().optional(),
  owner_oab_number: z.string().optional(),
  owner_oab_state: z.string().optional(),
  owner_position: z.string().optional(),
  owner_department: z.string().optional(),
});

type CreateTenantForm = z.infer<typeof createTenantSchema>;

export default function NewTenantPage() {
  const router = useRouter();
  const { token } = useSuperAdminAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<CreateTenantForm>({
    resolver: zodResolver(createTenantSchema),
    defaultValues: {
      name: '',
      slug: '',
      email: '',
      phone: '',
      plan_type: 'free',
      max_users: 5,
      max_processes: 100,
      // Campos do usuário owner
      owner_name: '',
      owner_password: '',
      owner_phone: '',
      owner_oab_number: '',
      owner_oab_state: '',
      owner_position: '',
      owner_department: '',
    },
  });

  const onSubmit = async (data: CreateTenantForm) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/superadmin/super-admin/tenants`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(data),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao criar empresa');
      }

      const newTenant = await response.json();
      router.push(`/superadmin/tenants/${newTenant.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
  };

  const generateSlug = (name: string) => {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  };

  const handleNameChange = (name: string) => {
    const slug = generateSlug(name);
    form.setValue('slug', slug);
  };

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
              <h1 className="text-2xl font-bold">Nova Empresa</h1>
              <p className="text-muted-foreground">Criar uma nova empresa no sistema</p>
            </div>
          </div>
        </div>

        {/* Form */}
        <Card className="max-w-4xl">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Building2 className="h-5 w-5 mr-2" />
              Informações da Empresa
            </CardTitle>
            <CardDescription>
              Preencha os dados da nova empresa. O email informado será usado para contato da empresa e login do proprietário.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                {/* Informações Básicas da Empresa */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Informações da Empresa</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Nome da Empresa *</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="Ex: Escritório de Advocacia Silva"
                              onChange={(e) => {
                                field.onChange(e);
                                handleNameChange(e.target.value);
                              }}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="slug"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Slug *</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="ex: escritorio-silva"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email da Empresa *</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              type="email"
                              placeholder="contato@empresa.com"
                            />
                          </FormControl>
                          <FormMessage />
                          <p className="text-sm text-muted-foreground">
                            Este email será usado para contato da empresa e login do proprietário
                          </p>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="phone"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Telefone</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="(11) 99999-9999"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Configurações do Plano */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Configurações do Plano</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <FormField
                      control={form.control}
                      name="plan_type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Tipo de Plano *</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Selecione o plano" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="free">Free</SelectItem>
                              <SelectItem value="premium">Premium</SelectItem>
                              <SelectItem value="enterprise">Enterprise</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="max_users"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Máximo de Usuários *</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              type="number"
                              min="1"
                              max="1000"
                              onChange={(e) => field.onChange(parseInt(e.target.value))}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="max_processes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Máximo de Processos *</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              type="number"
                              min="10"
                              max="10000"
                              onChange={(e) => field.onChange(parseInt(e.target.value))}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Campos do Usuário Owner */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Informações do Proprietário</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="owner_name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Nome do Proprietário *</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="Ex: João da Silva"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="owner_password"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Senha do Proprietário *</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              type="password"
                              placeholder="********"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="owner_phone"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Telefone do Proprietário</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="(11) 99999-9999"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="owner_oab_number"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Número da OAB</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="123456"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="owner_oab_state"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Estado da OAB</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="SP"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="owner_position"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Cargo do Proprietário</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="Advogado"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="owner_department"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Departamento do Proprietário</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="Diretoria"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-red-600 text-sm">{error}</p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center justify-end space-x-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => router.push('/superadmin/tenants')}
                    disabled={isLoading}
                  >
                    <X className="h-4 w-4 mr-2" />
                    Cancelar
                  </Button>
                  <Button type="submit" disabled={isLoading}>
                    <Save className="h-4 w-4 mr-2" />
                    {isLoading ? 'Criando...' : 'Criar Empresa'}
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </SuperAdminLayout>
  );
}
