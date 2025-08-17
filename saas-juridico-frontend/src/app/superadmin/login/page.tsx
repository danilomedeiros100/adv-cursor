'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Shield, User, Lock, AlertTriangle } from 'lucide-react';
import { useSuperAdminStore } from '@/stores/superAdminStore';

const superadminLoginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Senha deve ter pelo menos 6 caracteres'),
});

type SuperAdminLoginForm = z.infer<typeof superadminLoginSchema>;

export default function SuperAdminLoginPage() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useSuperAdminStore();

  const form = useForm<SuperAdminLoginForm>({
    resolver: zodResolver(superadminLoginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: SuperAdminLoginForm) => {
    clearError();
    
    try {
      await login(data.email, data.password);
      router.push('/superadmin/dashboard');
    } catch (error) {
      // Error is handled by the store
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo e Título */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-gradient-to-r from-purple-600 to-blue-600 shadow-lg">
            <Shield className="h-10 w-10 text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-white">
            Super Admin Portal
          </h2>
          <p className="mt-2 text-sm text-gray-300">
            Acesso exclusivo para administradores do sistema
          </p>
        </div>

        {/* Login Form */}
        <Card className="bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader>
            <CardTitle className="text-center text-white">Login Super Admin</CardTitle>
            <CardDescription className="text-center text-gray-300">
              Entre com suas credenciais de super administrador
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-white">Email</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                          <Input
                            {...field}
                            type="email"
                            placeholder="admin@saasjuridico.com"
                            className="pl-10 bg-white/20 border-white/30 text-white placeholder:text-gray-400"
                          />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-white">Senha</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                          <Input
                            {...field}
                            type="password"
                            placeholder="••••••••"
                            className="pl-10 bg-white/20 border-white/30 text-white placeholder:text-gray-400"
                          />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {error && (
                  <div className="flex items-center gap-2 text-sm text-red-300 bg-red-900/20 p-3 rounded-md border border-red-500/30">
                    <AlertTriangle className="h-4 w-4" />
                    {error}
                  </div>
                )}

                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
                  disabled={isLoading}
                >
                  {isLoading ? 'Entrando...' : 'Acessar Portal'}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-gray-400">
          <p>Portal restrito para super administradores</p>
          <p className="mt-1">Acesso controlado e monitorado</p>
        </div>
      </div>
    </div>
  );
}
