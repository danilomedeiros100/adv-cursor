import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  AlertTriangle, 
  Eye, 
  Clock, 
  Calendar,
  CheckCircle,
  XCircle,
  Zap
} from "lucide-react";

interface ProcessDeadline {
  id: string;
  title: string;
  due_date: string;
  process_id: string;
  process_subject: string;
  days_left: number;
  status: 'pending' | 'overdue' | 'completed';
}

interface UrgentDeadlinesProps {
  deadlines: ProcessDeadline[];
  onViewProcess?: (processId: string) => void;
  onViewDeadline?: (deadlineId: string) => void;
}

export function UrgentDeadlines({ deadlines, onViewProcess, onViewDeadline }: UrgentDeadlinesProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'overdue':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'overdue':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      default:
        return <Calendar className="h-4 w-4 text-gray-600" />;
    }
  };

  const getPriorityColor = (daysLeft: number) => {
    if (daysLeft < 0) return 'text-red-600';
    if (daysLeft <= 1) return 'text-orange-600';
    if (daysLeft <= 3) return 'text-yellow-600';
    return 'text-blue-600';
  };

  const getPriorityText = (daysLeft: number) => {
    if (daysLeft < 0) return 'ATRASADO';
    if (daysLeft === 0) return 'VENCE HOJE';
    if (daysLeft === 1) return 'VENCE AMANHÃ';
    return `${daysLeft} DIAS`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const urgentCount = deadlines.filter(d => d.status === 'overdue').length;
  const pendingCount = deadlines.filter(d => d.status === 'pending').length;

  return (
    <Card className="card-modern bg-gradient-to-br from-orange-50 to-orange-100/30 border-orange-200">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2 text-orange-800">
          <div className="p-2 bg-orange-500/10 rounded-lg">
            <AlertTriangle className="h-5 w-5 text-orange-600" />
          </div>
          <span className="text-xl font-semibold">Prazos Urgentes</span>
          <div className="ml-auto flex gap-2">
            {urgentCount > 0 && (
              <Badge variant="destructive" className="text-xs">
                {urgentCount} atrasados
              </Badge>
            )}
            {pendingCount > 0 && (
              <Badge variant="secondary" className="text-xs bg-yellow-100 text-yellow-800">
                {pendingCount} pendentes
              </Badge>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {deadlines.length > 0 ? (
            deadlines.map((deadline) => (
              <div 
                key={deadline.id} 
                className="flex items-center justify-between p-4 bg-white/80 backdrop-blur-sm rounded-xl border border-orange-200/50 hover:bg-white transition-all duration-200"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    {getStatusIcon(deadline.status)}
                    <Badge 
                      variant={deadline.status === 'overdue' ? 'destructive' : 'default'}
                      className={`text-xs font-medium ${getStatusColor(deadline.status)}`}
                    >
                      {getPriorityText(deadline.days_left)}
                    </Badge>
                    <span className="font-medium text-sm text-gray-800">{deadline.title}</span>
                  </div>
                  <p className="text-xs text-gray-600 mb-1">{deadline.process_subject}</p>
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      Vence: {formatDate(deadline.due_date)}
                    </span>
                    <span className={`flex items-center ${getPriorityColor(deadline.days_left)}`}>
                      <Zap className="h-3 w-3 mr-1" />
                      {Math.abs(deadline.days_left)} {deadline.days_left < 0 ? 'dias atrás' : 'dias restantes'}
                    </span>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="button-modern border-orange-200 hover:bg-orange-50"
                    onClick={() => onViewDeadline?.(deadline.id)}
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    Prazo
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="button-modern border-blue-200 hover:bg-blue-50"
                    onClick={() => onViewProcess?.(deadline.process_id)}
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    Processo
                  </Button>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
              <p className="font-medium text-lg">Nenhum prazo urgente!</p>
              <p className="text-sm">Todos os prazos estão em dia.</p>
              <div className="mt-4">
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Sistema atualizado
                </Badge>
              </div>
            </div>
          )}
        </div>

        {/* Resumo dos prazos */}
        {deadlines.length > 0 && (
          <div className="mt-6 pt-4 border-t border-orange-200/50">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-orange-600">{deadlines.length}</p>
                <p className="text-xs text-orange-600/80">Total</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-red-600">{urgentCount}</p>
                <p className="text-xs text-red-600/80">Atrasados</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-yellow-600">{pendingCount}</p>
                <p className="text-xs text-yellow-600/80">Pendentes</p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
