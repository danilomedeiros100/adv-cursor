"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Users, 
  FileText, 
  Calendar, 
  AlertTriangle, 
  Clock, 
  TrendingUp,
  Plus,
  Eye,
  CheckCircle,
  XCircle,
  DollarSign,
  Scale,
  Upload,
  Search,
  RefreshCw
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useProcesses } from "@/hooks/useProcesses";
import { useClients } from "@/hooks/useClients";
import { useDashboard } from "@/hooks/useDashboard";
import { Loading } from "@/components/ui/loading";
import { toast } from "sonner";

interface DashboardStats {
  totalProcesses: number;
  activeProcesses: number;
  urgentDeadlines: number;
  pendingTasks: number;
  completionRate: number;
  totalClients: number;
  monthlyRevenue: number;
}

interface ProcessDeadline {
  id: string;
  title: string;
  due_date: string;
  process_id: string;
  process_subject: string;
  days_left: number;
  status: 'pending' | 'overdue' | 'completed';
}

interface RecentActivity {
  id: string;
  type: 'process_created' | 'deadline_added' | 'document_uploaded' | 'client_added';
  title: string;
  description: string;
  timestamp: string;
  process_id?: string;
}

export default function CompanyDashboardPage() {
  const { user } = useAuth();
  const { processes, fetchProcesses } = useProcesses();
  const { clients, fetchClients } = useClients();
  const { 
    stats, 
    urgentDeadlines, 
    recentActivities, 
    loading, 
    error, 
    refreshDashboard 
  } = useDashboard();

  // Carregar processos e clientes para compatibilidade
  useEffect(() => {
    Promise.all([
      fetchProcesses(),
      fetchClients()
    ]);
  }, []);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'process_created':
        return <Scale className="h-4 w-4 text-blue-600" />;
      case 'document_uploaded':
        return <FileText className="h-4 w-4 text-green-600" />;
      case 'deadline_added':
        return <Clock className="h-4 w-4 text-orange-600" />;
      case 'client_added':
        return <Users className="h-4 w-4 text-purple-600" />;
      default:
        return <Eye className="h-4 w-4 text-gray-600" />;
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <Loading message="Carregando dashboard..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Bem-vindo de volta, {user?.name || 'Advogado'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={refreshDashboard}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processos Ativos</CardTitle>
            <Scale className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeProcesses}</div>
            <p className="text-xs text-muted-foreground">
              de {stats.totalProcesses} total
            </p>
            <Progress value={stats.completionRate} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Prazos Urgentes</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.urgentDeadlines}</div>
            <p className="text-xs text-muted-foreground">
              precisam de atenção
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tarefas Pendentes</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pendingTasks}</div>
            <p className="text-xs text-muted-foreground">
              aguardando ação
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Receita Mensal</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(stats.monthlyRevenue)}
            </div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="h-3 w-3 inline mr-1" />
              +12% vs mês anterior
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Ações Rápidas */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex-col">
              <Plus className="h-6 w-6 mb-2" />
              <span className="text-sm">Novo Processo</span>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col">
              <FileText className="h-6 w-6 mb-2" />
              <span className="text-sm">Nova Petição</span>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col">
              <Calendar className="h-6 w-6 mb-2" />
              <span className="text-sm">Novo Prazo</span>
            </Button>
            
            <Button variant="outline" className="h-20 flex-col">
              <Upload className="h-6 w-6 mb-2" />
              <span className="text-sm">Upload Doc</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Prazos Urgentes */}
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-orange-800">
              <AlertTriangle className="h-5 w-5" />
              <span>Prazos Urgentes</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {urgentDeadlines.map((deadline) => (
                <div key={deadline.id} className="flex items-center justify-between p-3 bg-white rounded-lg border">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <Badge 
                        variant={deadline.status === 'overdue' ? 'destructive' : 'default'}
                        className="text-xs"
                      >
                        {deadline.status === 'overdue' ? 'ATRASADO' : `${deadline.days_left} dias`}
                      </Badge>
                      <span className="font-medium text-sm">{deadline.title}</span>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">{deadline.process_subject}</p>
                  </div>
                  <Button size="sm" variant="outline">
                    Ver Processo
                  </Button>
                </div>
              ))}
              
              {urgentDeadlines.length === 0 && (
                <div className="text-center py-4 text-gray-500">
                  <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                  <p>Nenhum prazo urgente!</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Atividades Recentes */}
        <Card>
          <CardHeader>
            <CardTitle>Atividades Recentes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg">
                  <div className="mt-1">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{activity.title}</p>
                    <p className="text-xs text-gray-600">{activity.description}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {formatDate(activity.timestamp)}
                    </p>
                  </div>
                  {activity.process_id && (
                    <Button size="sm" variant="ghost">
                      <Eye className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Processos que Precisam de Atenção */}
      <Card>
        <CardHeader>
          <CardTitle>Processos que Precisam de Atenção</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {processes.filter(p => p.requires_attention).slice(0, 5).map((process) => (
              <div key={process.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <Badge variant="destructive" className="text-xs">
                      ATENÇÃO
                    </Badge>
                    <span className="font-medium">{process.subject}</span>
                  </div>
                  <p className="text-sm text-gray-600">
                    Cliente: {process.client?.name || 'N/A'} • 
                    CNJ: {process.cnj_number || 'N/A'}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline">
                    Ver Detalhes
                  </Button>
                  <Button size="sm">
                    Ação
                  </Button>
                </div>
              </div>
            ))}
            
            {processes.filter(p => p.requires_attention).length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                <p>Nenhum processo precisa de atenção!</p>
                <p className="text-sm">Todos os processos estão em dia.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
