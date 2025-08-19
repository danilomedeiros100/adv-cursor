"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog";
import { 
  Calendar, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  Plus, 
  Edit, 
  Trash2,
  Eye,
  Download
} from "lucide-react";
import { useProcesses } from "@/hooks/useProcesses";
import { Loading } from "@/components/ui/loading";
import { toast } from "sonner";

interface ProcessDeadline {
  id: string;
  title: string;
  description?: string;
  due_date: string;
  deadline_type: 'legal' | 'internal' | 'client';
  status: 'pending' | 'completed' | 'overdue';
  is_critical: boolean;
  notify_days_before: number;
  completed_at?: string;
  completed_by?: {
    id: string;
    name: string;
  };
  created_at: string;
  created_by?: {
    id: string;
    name: string;
  };
}

interface ProcessDeadlinesProps {
  processId: string;
}

export function ProcessDeadlines({ processId }: ProcessDeadlinesProps) {
  const { getProcessDeadlines } = useProcesses();
  const [deadlines, setDeadlines] = useState<ProcessDeadline[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  useEffect(() => {
    loadDeadlines();
  }, [processId]);

  const loadDeadlines = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.log("Token não encontrado, não carregando prazos");
        setLoading(false);
        return;
      }

      const response = await fetch(`/api/v1/company/processes/${processId}/deadlines`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const deadlinesData = await response.json();
        setDeadlines(deadlinesData);
      } else {
        throw new Error('Erro ao carregar prazos');
      }
    } catch (error) {
      console.error("Erro ao carregar prazos:", error);
      toast.error("Erro ao carregar prazos");
    } finally {
      setLoading(false);
    }
  };

  const getDeadlineStatusColor = (status: string) => {
    switch (status) {
      case 'overdue':
        return 'destructive';
      case 'completed':
        return 'default';
      case 'pending':
        return 'secondary';
      default:
        return 'secondary';
    }
  };

  const getDeadlineStatusLabel = (status: string) => {
    switch (status) {
      case 'overdue':
        return 'Atrasado';
      case 'completed':
        return 'Concluído';
      case 'pending':
        return 'Pendente';
      default:
        return status;
    }
  };

  const getDeadlineTypeLabel = (type: string) => {
    switch (type) {
      case 'legal':
        return 'Legal';
      case 'internal':
        return 'Interno';
      case 'client':
        return 'Cliente';
      default:
        return type;
    }
  };

  const getDeadlineTypeColor = (type: string) => {
    switch (type) {
      case 'legal':
        return 'bg-red-100 text-red-800';
      case 'internal':
        return 'bg-blue-100 text-blue-800';
      case 'client':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getDaysLeft = (dueDate: string) => {
    const today = new Date();
    const due = new Date(dueDate);
    const diffTime = due.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const handleAddDeadline = async (deadlineData: any) => {
    try {
      // TODO: Implementar adição de prazo via API
      toast.success("Prazo adicionado com sucesso!");
      setIsAddDialogOpen(false);
      await loadDeadlines();
    } catch (error) {
      console.error("Erro ao adicionar prazo:", error);
      toast.error("Erro ao adicionar prazo");
    }
  };

  const handleCompleteDeadline = async (deadlineId: string) => {
    try {
      // TODO: Implementar conclusão de prazo via API
      toast.success("Prazo marcado como concluído!");
      await loadDeadlines();
    } catch (error) {
      console.error("Erro ao concluir prazo:", error);
      toast.error("Erro ao concluir prazo");
    }
  };

  const handleDeleteDeadline = async (deadlineId: string) => {
    if (!confirm("Tem certeza que deseja excluir este prazo?")) {
      return;
    }

    try {
      // TODO: Implementar exclusão de prazo via API
      toast.success("Prazo excluído com sucesso!");
      await loadDeadlines();
    } catch (error) {
      console.error("Erro ao excluir prazo:", error);
      toast.error("Erro ao excluir prazo");
    }
  };

  // Filtrar prazos por status
  const pendingDeadlines = deadlines.filter(d => d.status === 'pending');
  const overdueDeadlines = deadlines.filter(d => d.status === 'overdue');
  const completedDeadlines = deadlines.filter(d => d.status === 'completed');

  if (loading) {
    return <Loading message="Carregando prazos..." />;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Prazos do Processo</h2>
          <p className="text-sm text-gray-600">
            Gerencie prazos críticos e internos
          </p>
        </div>
        
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Prazo
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Adicionar Prazo</DialogTitle>
            </DialogHeader>
            <AddDeadlineForm 
              onSubmit={handleAddDeadline}
              onCancel={() => setIsAddDialogOpen(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Prazos Atrasados */}
      {overdueDeadlines.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-red-800">
              <AlertTriangle className="h-5 w-5" />
              <span>Prazos Atrasados ({overdueDeadlines.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {overdueDeadlines.map((deadline) => (
                <DeadlineItem
                  key={deadline.id}
                  deadline={deadline}
                  onComplete={handleCompleteDeadline}
                  onDelete={handleDeleteDeadline}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Prazos Pendentes */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Clock className="h-5 w-5" />
            <span>Prazos Pendentes ({pendingDeadlines.length})</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {pendingDeadlines.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <p className="text-gray-600">Nenhum prazo pendente!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {pendingDeadlines.map((deadline) => (
                <DeadlineItem
                  key={deadline.id}
                  deadline={deadline}
                  onComplete={handleCompleteDeadline}
                  onDelete={handleDeleteDeadline}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Prazos Concluídos */}
      {completedDeadlines.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5" />
              <span>Prazos Concluídos ({completedDeadlines.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {completedDeadlines.map((deadline) => (
                <DeadlineItem
                  key={deadline.id}
                  deadline={deadline}
                  onComplete={handleCompleteDeadline}
                  onDelete={handleDeleteDeadline}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Estado vazio */}
      {deadlines.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum prazo registrado
            </h3>
            <p className="text-gray-600 mb-4">
              Comece adicionando o primeiro prazo do processo.
            </p>
            <Button onClick={() => setIsAddDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Primeiro Prazo
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

interface DeadlineItemProps {
  deadline: ProcessDeadline;
  onComplete: (deadlineId: string) => void;
  onDelete: (deadlineId: string) => void;
}

function DeadlineItem({ deadline, onComplete, onDelete }: DeadlineItemProps) {
  const daysLeft = getDaysLeft(deadline.due_date);
  const isOverdue = daysLeft < 0;
  const isCritical = deadline.is_critical || daysLeft <= 3;

  const getDaysLeftText = () => {
    if (isOverdue) {
      return `${Math.abs(daysLeft)} dias atrasado`;
    } else if (daysLeft === 0) {
      return "Vence hoje";
    } else if (daysLeft === 1) {
      return "Vence amanhã";
    } else {
      return `Vence em ${daysLeft} dias`;
    }
  };

  const getDaysLeftColor = () => {
    if (isOverdue) return "text-red-600";
    if (isCritical) return "text-orange-600";
    return "text-gray-600";
  };

  return (
    <div className="flex items-center justify-between p-4 border rounded-lg bg-white">
      <div className="flex-1">
        <div className="flex items-center space-x-2 mb-2">
          <Badge variant={getDeadlineStatusColor(deadline.status)}>
            {getDeadlineStatusLabel(deadline.status)}
          </Badge>
          <span className={`px-2 py-1 rounded text-xs font-medium ${getDeadlineTypeColor(deadline.deadline_type)}`}>
            {getDeadlineTypeLabel(deadline.deadline_type)}
          </span>
          {deadline.is_critical && (
            <Badge variant="destructive" className="text-xs">
              Crítico
            </Badge>
          )}
        </div>
        
        <h3 className="font-medium text-gray-900 mb-1">
          {deadline.title}
        </h3>
        
        {deadline.description && (
          <p className="text-sm text-gray-600 mb-2">
            {deadline.description}
          </p>
        )}
        
        <div className="flex items-center space-x-4 text-sm">
          <span className="text-gray-500">
            Vencimento: {formatDate(deadline.due_date)}
          </span>
          <span className={getDaysLeftColor()}>
            {getDaysLeftText()}
          </span>
        </div>
      </div>
      
      <div className="flex space-x-2">
        {deadline.status === 'pending' && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onComplete(deadline.id)}
          >
            <CheckCircle className="h-4 w-4 mr-1" />
            Concluir
          </Button>
        )}
        
        <Button
          size="sm"
          variant="ghost"
          onClick={() => onDelete(deadline.id)}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}

interface AddDeadlineFormProps {
  onSubmit: (deadlineData: any) => void;
  onCancel: () => void;
}

function AddDeadlineForm({ onSubmit, onCancel }: AddDeadlineFormProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
    deadline_type: 'internal',
    is_critical: false,
    notify_days_before: 3
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Título do Prazo
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded-md"
          placeholder="Ex: Petição inicial"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Descrição
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded-md"
          rows={3}
          placeholder="Descrição do prazo (opcional)"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Data e Hora de Vencimento
        </label>
        <input
          type="datetime-local"
          value={formData.due_date}
          onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded-md"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tipo de Prazo
        </label>
        <select
          value={formData.deadline_type}
          onChange={(e) => setFormData({ ...formData, deadline_type: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded-md"
        >
          <option value="legal">Legal</option>
          <option value="internal">Interno</option>
          <option value="client">Cliente</option>
        </select>
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="is_critical"
          checked={formData.is_critical}
          onChange={(e) => setFormData({ ...formData, is_critical: e.target.checked })}
          className="rounded border-gray-300"
        />
        <label htmlFor="is_critical" className="text-sm font-medium text-gray-700">
          Prazo crítico
        </label>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Notificar (dias antes)
        </label>
        <input
          type="number"
          value={formData.notify_days_before}
          onChange={(e) => setFormData({ ...formData, notify_days_before: parseInt(e.target.value) })}
          className="w-full p-2 border border-gray-300 rounded-md"
          min="1"
          max="30"
        />
      </div>

      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit">
          Adicionar Prazo
        </Button>
      </div>
    </form>
  );
}
