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
  FileText, 
  Calendar, 
  Gavel, 
  Users, 
  Eye, 
  Plus, 
  Edit, 
  Trash2,
  Clock,
  AlertTriangle,
  CheckCircle,
  MessageSquare,
  Upload,
  Download
} from "lucide-react";
import { useProcesses } from "@/hooks/useProcesses";
import { Loading } from "@/components/ui/loading";
import { toast } from "sonner";

interface TimelineEvent {
  id: string;
  type: 'petition' | 'decision' | 'publication' | 'hearing' | 'deadline' | 'document' | 'note' | 'other';
  title: string;
  description?: string;
  occurred_at: string;
  created_at?: string;
  metadata?: Record<string, any>;
  documents?: Array<{
    id: string;
    name: string;
    url: string;
  }>;
  created_by?: {
    id: string;
    name: string;
  };
}

interface ProcessTimelineProps {
  processId: string;
}

export function ProcessTimeline({ processId }: ProcessTimelineProps) {
  const { getProcessTimeline } = useProcesses();
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  useEffect(() => {
    loadTimeline();
  }, [processId]);

  const loadTimeline = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.log("Token não encontrado, não carregando timeline");
        setLoading(false);
        return;
      }

      const response = await fetch(`/api/v1/company/processes/${processId}/timeline`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const timelineData = await response.json();
        setTimeline(timelineData);
      } else {
        throw new Error('Erro ao carregar timeline');
      }
    } catch (error) {
      console.error("Erro ao carregar timeline:", error);
      toast.error("Erro ao carregar timeline");
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'petition':
        return <FileText className="h-5 w-5 text-blue-600" />;
      case 'decision':
        return <Gavel className="h-5 w-5 text-green-600" />;
      case 'publication':
        return <Eye className="h-5 w-5 text-purple-600" />;
      case 'hearing':
        return <Users className="h-5 w-5 text-orange-600" />;
      case 'deadline':
        return <Clock className="h-5 w-5 text-red-600" />;
      case 'document':
        return <Upload className="h-5 w-5 text-indigo-600" />;
      case 'note':
        return <MessageSquare className="h-5 w-5 text-gray-600" />;
      default:
        return <Calendar className="h-5 w-5 text-gray-600" />;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'petition':
        return 'border-blue-200 bg-blue-50';
      case 'decision':
        return 'border-green-200 bg-green-50';
      case 'publication':
        return 'border-purple-200 bg-purple-50';
      case 'hearing':
        return 'border-orange-200 bg-orange-50';
      case 'deadline':
        return 'border-red-200 bg-red-50';
      case 'document':
        return 'border-indigo-200 bg-indigo-50';
      case 'note':
        return 'border-gray-200 bg-gray-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getEventTypeLabel = (type: string) => {
    switch (type) {
      case 'petition':
        return 'Petição';
      case 'decision':
        return 'Decisão';
      case 'publication':
        return 'Publicação';
      case 'hearing':
        return 'Audiência';
      case 'deadline':
        return 'Prazo';
      case 'document':
        return 'Documento';
      case 'note':
        return 'Anotação';
      default:
        return 'Outro';
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

  const handleAddEvent = async (eventData: any) => {
    try {
      // TODO: Implementar adição de evento via API
      toast.success("Evento adicionado com sucesso!");
      setIsAddDialogOpen(false);
      await loadTimeline();
    } catch (error) {
      console.error("Erro ao adicionar evento:", error);
      toast.error("Erro ao adicionar evento");
    }
  };

  const handleEditEvent = async (eventId: string, eventData: any) => {
    try {
      // TODO: Implementar edição de evento via API
      toast.success("Evento atualizado com sucesso!");
      await loadTimeline();
    } catch (error) {
      console.error("Erro ao atualizar evento:", error);
      toast.error("Erro ao atualizar evento");
    }
  };

  const handleDeleteEvent = async (eventId: string) => {
    if (!confirm("Tem certeza que deseja excluir este evento?")) {
      return;
    }

    try {
      // TODO: Implementar exclusão de evento via API
      toast.success("Evento excluído com sucesso!");
      await loadTimeline();
    } catch (error) {
      console.error("Erro ao excluir evento:", error);
      toast.error("Erro ao excluir evento");
    }
  };

  if (loading) {
    return <Loading message="Carregando timeline..." />;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Timeline do Processo</h2>
          <p className="text-sm text-gray-600">
            Histórico completo de andamentos e eventos
          </p>
        </div>
        
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Evento
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Adicionar Evento</DialogTitle>
            </DialogHeader>
            <AddTimelineEventForm 
              onSubmit={handleAddEvent}
              onCancel={() => setIsAddDialogOpen(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Timeline */}
      <Card>
        <CardContent className="p-6">
          {timeline.length === 0 ? (
            <div className="text-center py-8">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Nenhum evento registrado
              </h3>
              <p className="text-gray-600 mb-4">
                Comece adicionando o primeiro evento da timeline.
              </p>
              <Button onClick={() => setIsAddDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Adicionar Primeiro Evento
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              {timeline.map((event, index) => (
                <TimelineEventItem
                  key={event.id}
                  event={event}
                  isLast={index === timeline.length - 1}
                  onEdit={handleEditEvent}
                  onDelete={handleDeleteEvent}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

interface TimelineEventItemProps {
  event: TimelineEvent;
  isLast: boolean;
  onEdit: (eventId: string, eventData: any) => void;
  onDelete: (eventId: string) => void;
}

function TimelineEventItem({ event, isLast, onEdit, onDelete }: TimelineEventItemProps) {
  const [isEditing, setIsEditing] = useState(false);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'petition':
        return <FileText className="h-5 w-5 text-blue-600" />;
      case 'decision':
        return <Gavel className="h-5 w-5 text-green-600" />;
      case 'publication':
        return <Eye className="h-5 w-5 text-purple-600" />;
      case 'hearing':
        return <Users className="h-5 w-5 text-orange-600" />;
      case 'deadline':
        return <Clock className="h-5 w-5 text-red-600" />;
      case 'document':
        return <Upload className="h-5 w-5 text-indigo-600" />;
      case 'note':
        return <MessageSquare className="h-5 w-5 text-gray-600" />;
      default:
        return <Calendar className="h-5 w-5 text-gray-600" />;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'petition':
        return 'border-blue-200 bg-blue-50';
      case 'decision':
        return 'border-green-200 bg-green-50';
      case 'publication':
        return 'border-purple-200 bg-purple-50';
      case 'hearing':
        return 'border-orange-200 bg-orange-50';
      case 'deadline':
        return 'border-red-200 bg-red-50';
      case 'document':
        return 'border-indigo-200 bg-indigo-50';
      case 'note':
        return 'border-gray-200 bg-gray-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getEventTypeLabel = (type: string) => {
    switch (type) {
      case 'petition':
        return 'Petição';
      case 'decision':
        return 'Decisão';
      case 'publication':
        return 'Publicação';
      case 'hearing':
        return 'Audiência';
      case 'deadline':
        return 'Prazo';
      case 'document':
        return 'Documento';
      case 'note':
        return 'Anotação';
      default:
        return 'Outro';
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

  return (
    <div className="flex gap-4">
      {/* Timeline Line */}
      <div className="flex flex-col items-center">
        <div className={`p-2 rounded-full border-2 ${getEventColor(event.type)}`}>
          {getEventIcon(event.type)}
        </div>
        {!isLast && (
          <div className="w-0.5 h-16 bg-gray-300 mt-2"></div>
        )}
      </div>

      {/* Event Content */}
      <div className="flex-1 min-w-0">
        <div className={`p-4 rounded-lg border ${getEventColor(event.type)}`}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <Badge variant="outline" className="text-xs">
                  {getEventTypeLabel(event.type)}
                </Badge>
                <span className="text-sm text-gray-500">
                  {formatDate(event.occurred_at)}
                </span>
              </div>
              
              <h3 className="font-semibold text-gray-900 mb-1">
                {event.title}
              </h3>
              
              {event.description && (
                <p className="text-sm text-gray-700 mb-3">
                  {event.description}
                </p>
              )}

              {/* Documents */}
              {event.documents && event.documents.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {event.documents.map((doc) => (
                    <Button
                      key={doc.id}
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => window.open(doc.url, '_blank')}
                    >
                      <Download className="h-3 w-3 mr-1" />
                      {doc.name}
                    </Button>
                  ))}
                </div>
              )}

              {/* Metadata */}
              {event.metadata && Object.keys(event.metadata).length > 0 && (
                <div className="text-xs text-gray-600">
                  {Object.entries(event.metadata).map(([key, value]) => (
                    <div key={key}>
                      <span className="font-medium">{key}:</span> {String(value)}
                    </div>
                  ))}
                </div>
              )}

              {/* Created by */}
              {event.created_by && (
                <div className="text-xs text-gray-500 mt-2">
                  Adicionado por: {event.created_by.name}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex space-x-1 ml-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsEditing(true)}
              >
                <Edit className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(event.id)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

interface AddTimelineEventFormProps {
  onSubmit: (eventData: any) => void;
  onCancel: () => void;
}

function AddTimelineEventForm({ onSubmit, onCancel }: AddTimelineEventFormProps) {
  const [formData, setFormData] = useState({
    type: 'other',
    title: '',
    description: '',
    occurred_at: new Date().toISOString().slice(0, 16)
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tipo de Evento
        </label>
        <select
          value={formData.type}
          onChange={(e) => setFormData({ ...formData, type: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded-md"
        >
          <option value="petition">Petição</option>
          <option value="decision">Decisão</option>
          <option value="publication">Publicação</option>
          <option value="hearing">Audiência</option>
          <option value="deadline">Prazo</option>
          <option value="document">Documento</option>
          <option value="note">Anotação</option>
          <option value="other">Outro</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Título
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded-md"
          placeholder="Título do evento"
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
          placeholder="Descrição do evento (opcional)"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Data e Hora
        </label>
        <input
          type="datetime-local"
          value={formData.occurred_at}
          onChange={(e) => setFormData({ ...formData, occurred_at: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded-md"
          required
        />
      </div>

      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit">
          Adicionar Evento
        </Button>
      </div>
    </form>
  );
}
