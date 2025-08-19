import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  Users, 
  FileText, 
  Calendar, 
  AlertTriangle, 
  Clock, 
  TrendingUp,
  DollarSign,
  Scale,
  Target,
  Zap,
  BarChart3,
  Activity
} from "lucide-react";

interface DashboardStatsProps {
  stats: {
    totalProcesses: number;
    activeProcesses: number;
    urgentDeadlines: number;
    pendingTasks: number;
    completionRate: number;
    totalClients: number;
    monthlyRevenue: number;
  };
}

export function DashboardStats({ stats }: DashboardStatsProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const getGrowthRate = (current: number, previous: number) => {
    if (previous === 0) return 0;
    return ((current - previous) / previous) * 100;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Processos Ativos */}
      <Card className="card-modern bg-gradient-to-br from-blue-50 to-blue-100/50 border-blue-200 hover:shadow-lg transition-all duration-300">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-blue-700">Processos Ativos</CardTitle>
          <div className="p-2 bg-blue-500/10 rounded-lg">
            <Scale className="h-5 w-5 text-blue-600" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-blue-700">{stats.activeProcesses}</div>
          <p className="text-sm text-blue-600/80 mt-1">
            de {stats.totalProcesses} total
          </p>
          <div className="mt-3">
            <Progress value={stats.completionRate} className="h-2 bg-blue-200" />
            <p className="text-xs text-blue-600/80 mt-1">{stats.completionRate}% concluído</p>
          </div>
          <div className="mt-2 flex items-center">
            <TrendingUp className="h-4 w-4 text-blue-600 mr-1" />
            <p className="text-xs text-blue-600/80">
              +{getGrowthRate(stats.activeProcesses, stats.totalProcesses - stats.activeProcesses).toFixed(1)}% vs mês anterior
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Prazos Urgentes */}
      <Card className="card-modern bg-gradient-to-br from-orange-50 to-orange-100/50 border-orange-200 hover:shadow-lg transition-all duration-300">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-orange-700">Prazos Urgentes</CardTitle>
          <div className="p-2 bg-orange-500/10 rounded-lg">
            <AlertTriangle className="h-5 w-5 text-orange-600" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-orange-700">{stats.urgentDeadlines}</div>
          <p className="text-sm text-orange-600/80 mt-1">
            precisam de atenção
          </p>
          <div className="mt-3 flex items-center">
            <Zap className="h-4 w-4 text-orange-600 mr-1" />
            <p className="text-xs text-orange-600/80">Ação imediata necessária</p>
          </div>
          {stats.urgentDeadlines > 0 && (
            <div className="mt-2">
              <Badge variant="destructive" className="text-xs">
                {stats.urgentDeadlines} atrasados
              </Badge>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tarefas Pendentes */}
      <Card className="card-modern bg-gradient-to-br from-purple-50 to-purple-100/50 border-purple-200 hover:shadow-lg transition-all duration-300">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-purple-700">Tarefas Pendentes</CardTitle>
          <div className="p-2 bg-purple-500/10 rounded-lg">
            <Clock className="h-5 w-5 text-purple-600" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-purple-700">{stats.pendingTasks}</div>
          <p className="text-sm text-purple-600/80 mt-1">
            aguardando ação
          </p>
          <div className="mt-3 flex items-center">
            <Target className="h-4 w-4 text-purple-600 mr-1" />
            <p className="text-xs text-purple-600/80">Prioridade alta</p>
          </div>
          <div className="mt-2">
            <Progress value={(stats.pendingTasks / (stats.pendingTasks + stats.activeProcesses)) * 100} className="h-2 bg-purple-200" />
            <p className="text-xs text-purple-600/80 mt-1">Taxa de conclusão</p>
          </div>
        </CardContent>
      </Card>

      {/* Receita Mensal */}
      <Card className="card-modern bg-gradient-to-br from-green-50 to-green-100/50 border-green-200 hover:shadow-lg transition-all duration-300">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-green-700">Receita Mensal</CardTitle>
          <div className="p-2 bg-green-500/10 rounded-lg">
            <DollarSign className="h-5 w-5 text-green-600" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-green-700">
            {formatCurrency(stats.monthlyRevenue)}
          </div>
          <p className="text-sm text-green-600/80 mt-1 flex items-center">
            <TrendingUp className="h-4 w-4 mr-1" />
            +12% vs mês anterior
          </p>
          <div className="mt-3">
            <Progress value={75} className="h-2 bg-green-200" />
            <p className="text-xs text-green-600/80 mt-1">75% da meta atingida</p>
          </div>
          <div className="mt-2">
            <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
              Meta: {formatCurrency(stats.monthlyRevenue * 1.33)}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
