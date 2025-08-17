'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Building2, Users, FileText, Shield } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isSuperAdmin, isCompanyUser, isClientUser, isLoading, isInitialized } = useAuth();

  useEffect(() => {
    // Só redireciona se não estiver carregando, estiver inicializado e autenticado
    if (!isLoading && isInitialized && isAuthenticated) {
      if (isSuperAdmin) {
        router.push('/superadmin/dashboard');
      } else if (isCompanyUser) {
        router.push('/company/dashboard');
      } else if (isClientUser) {
        router.push('/client/dashboard');
      }
    }
  }, [isAuthenticated, isSuperAdmin, isCompanyUser, isClientUser, isLoading, isInitialized, router]);

  // Mostra loading enquanto verifica autenticação
  if (isLoading || !isInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <Building2 className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold text-gray-900">SaaS Jurídico</span>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={() => router.push('/auth/login')}>
                Login
              </Button>
              <Button onClick={() => router.push('/auth/login')}>
                Começar Agora
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Modernize seu
            <span className="text-primary"> Escritório de Advocacia</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Sistema completo para gestão de escritórios de advocacia. 
            Controle processos, clientes, documentos e finanças em uma única plataforma.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={() => router.push('/auth/login')}>
              Acessar Sistema
            </Button>
            <Button variant="outline" size="lg">
              Solicitar Demo
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {features.map((feature) => (
            <Card key={feature.title} className="text-center">
              <CardHeader>
                <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>{feature.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* CTA Section */}
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Pronto para começar?
          </h2>
          <p className="text-lg text-gray-600 mb-6">
            Junte-se a centenas de escritórios que já modernizaram suas operações.
          </p>
          <Button size="lg" onClick={() => router.push('/auth/login')}>
            Criar Conta Gratuita
          </Button>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <Building2 className="h-6 w-6" />
              <span className="text-xl font-bold">SaaS Jurídico</span>
            </div>
            <p className="text-gray-400">
              Desenvolvido com ❤️ para modernizar a advocacia brasileira
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

const features = [
  {
    icon: Users,
    title: 'Gestão de Clientes',
    description: 'Cadastre e gerencie seus clientes de forma organizada e eficiente.',
  },
  {
    icon: FileText,
    title: 'Processos Jurídicos',
    description: 'Controle completo de processos com prazos e andamentos automáticos.',
  },
  {
    icon: Building2,
    title: 'Multi-Empresa',
    description: 'Sistema isolado por empresa, garantindo total privacidade dos dados.',
  },
  {
    icon: Shield,
    title: 'Segurança LGPD',
    description: 'Conformidade total com a LGPD e proteção de dados pessoais.',
  },
];
