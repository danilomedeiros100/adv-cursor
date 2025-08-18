'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/useAuth';
import { CNJStatsCard } from '@/components/CNJStatsCard';
import {
  Users,
  FolderOpen,
  FileText,
  DollarSign,
  AlertTriangle,
} from 'lucide-react';

export default function CompanyDashboardPage() {
  const { user } = useAuth();

  const stats = [
    {
      title: 'Total de Clientes',
      value: '156',
      change: '+12%',
      changeType: 'positive' as const,
      icon: Users,
    },
    {
      title: 'Processos Ativos',
      value: '89',
      change: '+5%',
      changeType: 'positive' as const,
      icon: FolderOpen,
    },
    {
      title: 'Documentos',
      value: '1,234',
      change: '+23%',
      changeType: 'positive' as const,
      icon: FileText,
    },
    {
      title: 'Receita Mensal',
      value: 'R$ 45.678',
      change: '+8%',
      changeType: 'positive' as const,
      icon: DollarSign,
    },
  ];

  const recentActivities = [
    {
      id: 1,
      type: 'process',
      title: 'Novo processo criado',
      description: 'Processo #2024/001 - Cliente João Silva',
      time: '2 horas atrás',
    },
    {
      id: 2,
      type: 'document',
      title: 'Documento assinado',
      description: 'Petição inicial - Processo #2024/001',
      time: '4 horas atrás',
    },
    {
      id: 3,
      type: 'client',
      title: 'Novo cliente cadastrado',
      description: 'Maria Santos - Direito Trabalhista',
      time: '1 dia atrás',
    },
  ];

  return (
    <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Bem-vindo de volta, {user?.name}! Aqui está um resumo da sua empresa.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  <span className={stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'}>
                    {stat.change}
                  </span>{' '}
                  desde o mês passado
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* CNJ Integration Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CNJStatsCard />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activities */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Atividades Recentes</CardTitle>
              <CardDescription>
                Últimas atividades da sua empresa
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-4">
                    <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {activity.description}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Ações Rápidas</CardTitle>
              <CardDescription>
                Acesse rapidamente as funcionalidades principais
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <button className="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-3">
                    <Users className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Novo Cliente</p>
                      <p className="text-sm text-muted-foreground">Cadastrar cliente</p>
                    </div>
                  </div>
                </button>

                <button className="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-3">
                    <FolderOpen className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Novo Processo</p>
                      <p className="text-sm text-muted-foreground">Criar processo</p>
                    </div>
                  </div>
                </button>

                <button className="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Novo Documento</p>
                      <p className="text-sm text-muted-foreground">Criar documento</p>
                    </div>
                  </div>
                </button>

                <button className="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-3">
                    <DollarSign className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Lançamento</p>
                      <p className="text-sm text-muted-foreground">Registrar receita</p>
                    </div>
                  </div>
                </button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Alerts */}
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-orange-800">
              <AlertTriangle className="h-5 w-5" />
              <span>Prazos Críticos</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Processo #2024/001 - Petição inicial</span>
                <span className="text-sm font-medium text-orange-600">Vence em 2 dias</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Processo #2024/002 - Contestação</span>
                <span className="text-sm font-medium text-orange-600">Vence em 5 dias</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
  );
}
