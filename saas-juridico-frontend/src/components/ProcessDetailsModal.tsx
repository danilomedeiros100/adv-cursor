"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { 
  Scale,
  Calendar,
  Users,
  FileText,
  Building,
  DollarSign,
  Clock,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Edit,
  Plus,
  Eye,
  Download,
  Upload,
  Trash2,
  Star,
  MessageSquare,
  Target,
  Shield,
  History,
  Settings,
  Bell,
  CheckSquare,
  Square,
  UserPlus,
  FileCheck,
  TrendingUp,
  AlertCircle,
  Info,
  ExternalLink,
  X
} from "lucide-react";
import { Process, ProcessTimelineEvent, ProcessDeadline } from "@/types/process";
import { useCNJIntegration } from "@/hooks/useCNJIntegration";
import { useProcesses } from "@/hooks/useProcesses";
import { useAuth } from "@/hooks/useAuth";
import { usePermissions } from "@/hooks/useAuth";
import { toast } from "sonner";

interface ProcessDetailsModalProps {
  process: Process | null;
  isOpen: boolean;
  onClose: () => void;
  onProcessUpdate?: (process: Process) => void;
}

export function ProcessDetailsModal({ 
  process, 
  isOpen, 
  onClose, 
  onProcessUpdate 
}: ProcessDetailsModalProps) {
  const { sincronizarProcesso, verificarStatus } = useCNJIntegration();
  const { getProcessTimeline, getProcessDeadlines, updateProcess } = useProcesses();
  const { user } = useAuth();
  const { hasPermission } = usePermissions();
  
  // Estados
  const [activeTab, setActiveTab] = useState("geral");
  const [cnjStatus, setCnjStatus] = useState<any>(null);
  const [loadingStatus, setLoadingStatus] = useState(false);
  const [timeline, setTimeline] = useState<ProcessTimelineEvent[]>([]);
  const [deadlines, setDeadlines] = useState<ProcessDeadline[]>([]);
  const [loadingTimeline, setLoadingTimeline] = useState(false);
  const [loadingDeadlines, setLoadingDeadlines] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);

  // Carregar dados quando o modal abrir
  useEffect(() => {
    if (process?.id && isOpen) {
      loadProcessData();
    }
  }, [process?.id, isOpen]);

  const loadProcessData = async () => {
    if (!process?.id) return;
    
    // Carregar timeline
    setLoadingTimeline(true);
    const timelineData = await getProcessTimeline(process.id);
    setTimeline(timelineData);
    setLoadingTimeline(false);

    // Carregar prazos
    setLoadingDeadlines(true);
    const deadlinesData = await getProcessDeadlines(process.id);
    setDeadlines(deadlinesData);
    setLoadingDeadlines(false);

    // Verificar status CNJ se houver número
    if (process.cnj_number) {
      checkCNJStatus();
    }
  };

  const checkCNJStatus = async () => {
    if (!process?.cnj_number) return;
    
    setLoadingStatus(true);
    const status = await verificarStatus(process.cnj_number);
    setCnjStatus(status);
    setLoadingStatus(false);
  };

  const handleSync = async () => {
    if (!process?.id) return;
    
    const success = await sincronizarProcesso(process.id);
    if (success) {
      // Recarregar status após sincronização
      setTimeout(checkCNJStatus, 2000);
      // Recarregar timeline
      setTimeout(() => loadProcessData(), 3000);
    }
  };

  const handleRequiresAttention = async () => {
    if (!process?.id) return;
    
    const updatedProcess = await updateProcess(process.id, {
      requires_attention: !process.requires_attention
    });
    
    if (updatedProcess && onProcessUpdate) {
      onProcessUpdate(updatedProcess);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "Não informado";
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const formatDateTime = (dateString: string) => {
    if (!dateString) return "Não informado";
    return new Date(dateString).toLocaleString('pt-BR');
  };

  const formatCurrency = (value?: number) => {
    if (!value) return "Não informado";
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value / 100);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "urgent": return "destructive";
      case "high": return "default";
      case "normal": return "secondary";
      case "low": return "outline";
      default: return "secondary";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "default";
      case "closed": return "secondary";
      case "suspended": return "destructive";
      default: return "secondary";
    }
  };

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case "urgent": return "Urgente";
      case "high": return "Alta";
      case "normal": return "Normal";
      case "low": return "Baixa";
      default: return priority;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "active": return "Ativo";
      case "closed": return "Encerrado";
      case "suspended": return "Suspenso";
      default: return status;
    }
  };

  const getDeadlineStatusColor = (status: string) => {
    switch (status) {
      case "overdue": return "destructive";
      case "delivered": return "default";
      case "open": return "secondary";
      default: return "secondary";
    }
  };

  const getDeadlineStatusLabel = (status: string) => {
    switch (status) {
      case "overdue": return "Atrasado";
      case "delivered": return "Entregue";
      case "open": return "Aberto";
      default: return status;
    }
  };

  const getTimelineEventIcon = (type: string) => {
    switch (type) {
      case "petition": return <FileText className="w-4 h-4" />;
      case "decision": return <Scale className="w-4 h-4" />;
      case "publication": return <Eye className="w-4 h-4" />;
      case "hearing": return <Users className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  const getTimelineEventColor = (type: string) => {
    switch (type) {
      case "petition": return "text-blue-600";
      case "decision": return "text-green-600";
      case "publication": return "text-purple-600";
      case "hearing": return "text-orange-600";
      default: return "text-gray-600";
    }
  };

  // Calcular próximos prazos
  const upcomingDeadlines = deadlines
    .filter(d => d.status === 'open' && new Date(d.due_date) > new Date())
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
    .slice(0, 3);

  // Calcular prazos atrasados
  const overdueDeadlines = deadlines.filter(d => d.status === 'open' && new Date(d.due_date) < new Date());

  if (!process) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="w-[95vw] max-w-[1400px] h-[90vh] max-h-[900px] p-0 overflow-hidden">
        <DialogHeader className="p-6 pb-4 border-b">
          <DialogTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Scale className="w-5 h-5" />
              <span className="text-lg font-semibold">Detalhes do Processo</span>
            </div>
            <div className="flex gap-2">
              {hasPermission("processes.update") && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowEditDialog(true)}
                >
                  <Edit className="w-4 h-4" />
                  <span className="hidden sm:inline">Editar</span>
                </Button>
              )}
                              <Button variant="outline" size="sm" onClick={onClose}>
                  <X className="w-4 h-4" />
                  <span className="hidden sm:inline">Fechar</span>
                </Button>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="flex flex-col lg:flex-row h-full overflow-hidden">
          {/* Coluna lateral - Resumo e Ações */}
          <div className="w-full lg:w-80 p-4 lg:p-6 border-b lg:border-b-0 lg:border-r bg-gray-50 lg:bg-white overflow-y-auto">
            <div className="space-y-4">
              {/* Resumo do Processo */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Resumo</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-sm mb-2">Identificação</h3>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="font-medium">Assunto:</span>
                        <p className="text-gray-600 truncate">{process.subject}</p>
                      </div>
                      <div>
                        <span className="font-medium">CNJ:</span>
                        <p className="text-gray-600 font-mono text-xs">{process.cnj_number || "Não informado"}</p>
                      </div>
                      <div>
                        <span className="font-medium">Cliente:</span>
                        <p className="text-gray-600">{process.client?.name || "Não informado"}</p>
                      </div>
                      <div>
                        <span className="font-medium">Tribunal:</span>
                        <p className="text-gray-600">{process.court || "Não informado"}</p>
                      </div>
                      <div>
                        <span className="font-medium">Comarca:</span>
                        <p className="text-gray-600">{process.jurisdiction || "Não informado"}</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-sm mb-2">Status</h3>
                    <div className="flex gap-2 flex-wrap">
                      <Badge variant={getPriorityColor(process.priority)} className="text-xs">
                        {getPriorityLabel(process.priority)}
                      </Badge>
                      <Badge variant={getStatusColor(process.status)} className="text-xs">
                        {getStatusLabel(process.status)}
                      </Badge>
                      {process.is_confidential && (
                        <Badge variant="outline" className="text-xs">
                          <Shield className="w-3 h-3" />
                          <span className="ml-1">Confidencial</span>
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-sm mb-2">KPIs Rápidos</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Próximos prazos:</span>
                        <Badge variant={upcomingDeadlines.length > 0 ? "default" : "secondary"} className="text-xs">
                          {upcomingDeadlines.length}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span>Atrasados:</span>
                        <Badge variant={overdueDeadlines.length > 0 ? "destructive" : "secondary"} className="text-xs">
                          {overdueDeadlines.length}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span>Valor estimado:</span>
                        <span className="font-medium">{formatCurrency(process.estimated_value)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Última atualização:</span>
                        <span className="text-gray-600">{formatDate(process.updated_at || process.created_at)}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Ações Rápidas */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Ações Rápidas</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {hasPermission("processes.update") && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => setShowEditDialog(true)}
                    >
                      <Edit className="w-4 h-4" />
                      <span>Editar Processo</span>
                    </Button>
                  )}
                  
                  {process.cnj_number && hasPermission("processes.update") && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={handleSync}
                      disabled={loadingStatus}
                    >
                      <RefreshCw className={`w-4 h-4 ${loadingStatus ? 'animate-spin' : ''}`} />
                      <span>Sincronizar CNJ</span>
                    </Button>
                  )}

                  {hasPermission("processes.update") && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start"
                      onClick={handleRequiresAttention}
                    >
                      {process.requires_attention ? (
                        <>
                          <CheckCircle className="w-4 h-4" />
                          <span>Remover Atenção</span>
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="w-4 h-4" />
                          <span>Marcar Atenção</span>
                        </>
                      )}
                    </Button>
                  )}

                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => setActiveTab("geral")}
                  >
                    <MessageSquare className="w-4 h-4" />
                    <span>Adicionar Nota</span>
                  </Button>

                                     <Button
                     variant="outline"
                     size="sm"
                     className="w-full justify-start"
                     onClick={() => setActiveTab("prazos")}
                   >
                     <Plus className="w-4 h-4" />
                     <span>Novo Prazo</span>
                   </Button>
                </CardContent>
              </Card>

              {/* Status CNJ */}
              {process.cnj_number && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Building className="w-4 h-4" />
                      Integração CNJ
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {loadingStatus ? (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Clock className="w-4 h-4 animate-spin" />
                        Verificando...
                      </div>
                    ) : cnjStatus ? (
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2">
                          {cnjStatus.exists ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-yellow-600" />
                          )}
                          <span className="font-medium">
                            {cnjStatus.exists ? "Encontrado" : "Não encontrado"}
                          </span>
                        </div>
                        {cnjStatus.last_update && (
                          <div>
                            <span className="text-gray-600">Última atualização:</span>
                            <p className="font-medium">{formatDate(cnjStatus.last_update)}</p>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-sm text-gray-600">
                        Clique em "Sincronizar CNJ" para verificar
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          {/* Conteúdo principal - Abas */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
              <div className="px-4 lg:px-6 pt-4 border-b">
                <TabsList className="grid w-full grid-cols-3 lg:grid-cols-6 h-auto">
                  <TabsTrigger value="geral" className="text-xs lg:text-sm">Geral</TabsTrigger>
                  <TabsTrigger value="andamentos" className="text-xs lg:text-sm">Andamentos</TabsTrigger>
                  <TabsTrigger value="prazos" className="text-xs lg:text-sm">Prazos</TabsTrigger>
                  <TabsTrigger value="financeiro" className="text-xs lg:text-sm">Financeiro</TabsTrigger>
                  <TabsTrigger value="documentos" className="text-xs lg:text-sm">Documentos</TabsTrigger>
                  <TabsTrigger value="tarefas" className="text-xs lg:text-sm">Tarefas</TabsTrigger>
                </TabsList>
              </div>

              <div className="flex-1 overflow-y-auto p-4 lg:p-6">
                {/* Aba Geral */}
                <TabsContent value="geral" className="mt-0 h-full">
                  <div className="space-y-6">
                    {/* Informações Básicas */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Informações Básicas</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="text-sm font-medium">Assunto</label>
                            <p className="text-sm text-gray-600">{process.subject}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Cliente</label>
                            <p className="text-sm text-gray-600">{process.client?.name || "Não informado"}</p>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <label className="text-sm font-medium">Número CNJ</label>
                            <p className="text-sm font-mono text-gray-600">
                              {process.cnj_number || "Não informado"}
                            </p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Tribunal</label>
                            <p className="text-sm text-gray-600">{process.court || "Não informado"}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Comarca</label>
                            <p className="text-sm text-gray-600">{process.jurisdiction || "Não informado"}</p>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="text-sm font-medium">Valor Estimado</label>
                            <p className="text-sm text-gray-600">{formatCurrency(process.estimated_value)}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Especialidade</label>
                            <p className="text-sm text-gray-600">{process.specialty?.name || "Não informado"}</p>
                          </div>
                        </div>

                        {process.notes && (
                          <div>
                            <label className="text-sm font-medium">Observações</label>
                            <p className="text-sm text-gray-600">{process.notes}</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* Advogados */}
                    {process.lawyers && process.lawyers.length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2">
                            <Users className="w-4 h-4" />
                            Advogados ({process.lawyers.length})
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {process.lawyers.map((lawyer) => (
                              <div key={lawyer.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                <div>
                                  <p className="text-sm font-medium">{lawyer.lawyer?.name}</p>
                                  <p className="text-xs text-gray-500">{lawyer.lawyer?.email}</p>
                                </div>
                                <div className="flex gap-1">
                                  {lawyer.is_primary && (
                                    <Badge variant="default" className="text-xs">Principal</Badge>
                                  )}
                                  <Badge variant="outline" className="text-xs">{lawyer.role}</Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Informações de Sistema */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          Informações de Sistema
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <label className="font-medium">Criado em</label>
                            <p className="text-gray-600">{formatDateTime(process.created_at)}</p>
                          </div>
                          {process.updated_at && (
                            <div>
                              <label className="font-medium">Atualizado em</label>
                              <p className="text-gray-600">{formatDateTime(process.updated_at)}</p>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>

                {/* Aba Andamentos */}
                <TabsContent value="andamentos" className="mt-0 h-full">
                  <Card className="h-full">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                          <History className="w-4 h-4" />
                          Timeline de Andamentos
                        </span>
                                                 <Button variant="outline" size="sm">
                           <Plus className="w-4 h-4" />
                           <span>Adicionar Andamento</span>
                         </Button>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {loadingTimeline ? (
                        <div className="flex items-center justify-center py-8">
                          <Clock className="w-6 h-6 animate-spin" />
                          <span className="ml-2">Carregando timeline...</span>
                        </div>
                      ) : timeline.length > 0 ? (
                        <div className="space-y-4">
                          {timeline.map((event) => (
                            <div key={event.id} className="flex gap-4 p-4 border rounded-lg">
                              <div className={`${getTimelineEventColor(event.type)} mt-1`}>
                                {getTimelineEventIcon(event.type)}
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center justify-between mb-2">
                                  <h4 className="font-medium">{event.title}</h4>
                                  <span className="text-sm text-gray-500">
                                    {formatDateTime(event.occurred_at)}
                                  </span>
                                </div>
                                {event.description && (
                                  <p className="text-sm text-gray-600 mb-2">{event.description}</p>
                                )}
                                <div className="flex gap-2">
                                                                     <Button variant="outline" size="sm">
                                     <MessageSquare className="w-3 h-3" />
                                     <span>Comentar</span>
                                   </Button>
                                                                     <Button variant="outline" size="sm">
                                     <Download className="w-3 h-3" />
                                     <span>Anexos</span>
                                   </Button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          <History className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                          <p>Nenhum andamento registrado</p>
                          <p className="text-sm">Os andamentos aparecerão aqui conforme o processo avança</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Aba Prazos */}
                <TabsContent value="prazos" className="mt-0 h-full">
                  <Card className="h-full">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                          <Calendar className="w-4 h-4" />
                          Prazos e Prazos
                        </span>
                                                 <Button variant="outline" size="sm">
                           <Plus className="w-4 h-4" />
                           <span>Novo Prazo</span>
                         </Button>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {loadingDeadlines ? (
                        <div className="flex items-center justify-center py-8">
                          <Clock className="w-6 h-6 animate-spin" />
                          <span className="ml-2">Carregando prazos...</span>
                        </div>
                      ) : deadlines.length > 0 ? (
                        <div className="space-y-4">
                          {deadlines.map((deadline) => (
                            <div key={deadline.id} className="flex items-center justify-between p-4 border rounded-lg">
                              <div className="flex items-center gap-4">
                                <div className="flex items-center gap-2">
                                  {deadline.status === 'delivered' ? (
                                    <CheckSquare className="w-5 h-5 text-green-600" />
                                  ) : deadline.status === 'overdue' ? (
                                    <AlertCircle className="w-5 h-5 text-red-600" />
                                  ) : (
                                    <Square className="w-5 h-5 text-gray-400" />
                                  )}
                                  <div>
                                    <h4 className="font-medium">{deadline.title}</h4>
                                    <p className="text-sm text-gray-500">
                                      Vencimento: {formatDate(deadline.due_date)}
                                    </p>
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge variant={getDeadlineStatusColor(deadline.status)}>
                                  {getDeadlineStatusLabel(deadline.status)}
                                </Badge>
                                {deadline.assigned_to && (
                                  <span className="text-sm text-gray-500">
                                    {deadline.assigned_to.name}
                                  </span>
                                )}
                                <Button variant="outline" size="sm">
                                  <Edit className="w-3 h-3" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                          <p>Nenhum prazo registrado</p>
                          <p className="text-sm">Adicione prazos para acompanhar as obrigações do processo</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Aba Financeiro */}
                <TabsContent value="financeiro" className="mt-0 h-full">
                  <Card className="h-full">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                          <DollarSign className="w-4 h-4" />
                          Controle Financeiro
                        </span>
                                                 <Button variant="outline" size="sm">
                           <Plus className="w-4 h-4" />
                           <span>Novo Lançamento</span>
                         </Button>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <Card>
                          <CardContent className="p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <TrendingUp className="w-4 h-4 text-green-600" />
                              <span className="text-sm font-medium">Honorários</span>
                            </div>
                            <p className="text-2xl font-bold text-green-600">
                              {formatCurrency(process.estimated_value)}
                            </p>
                            <p className="text-xs text-gray-500">Valor estimado</p>
                          </CardContent>
                        </Card>
                        <Card>
                          <CardContent className="p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <DollarSign className="w-4 h-4 text-blue-600" />
                              <span className="text-sm font-medium">Recebido</span>
                            </div>
                            <p className="text-2xl font-bold text-blue-600">R$ 0,00</p>
                            <p className="text-xs text-gray-500">Total recebido</p>
                          </CardContent>
                        </Card>
                        <Card>
                          <CardContent className="p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <AlertTriangle className="w-4 h-4 text-orange-600" />
                              <span className="text-sm font-medium">Pendente</span>
                            </div>
                            <p className="text-2xl font-bold text-orange-600">
                              {formatCurrency(process.estimated_value)}
                            </p>
                            <p className="text-xs text-gray-500">A receber</p>
                          </CardContent>
                        </Card>
                      </div>

                      <div className="text-center py-8 text-gray-500">
                        <DollarSign className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p>Nenhum lançamento financeiro</p>
                        <p className="text-sm">Adicione honorários, despesas e pagamentos</p>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Aba Documentos */}
                <TabsContent value="documentos" className="mt-0 h-full">
                  <Card className="h-full">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          Documentos
                        </span>
                                                 <Button variant="outline" size="sm">
                           <Upload className="w-4 h-4" />
                           <span>Upload</span>
                         </Button>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center py-8 text-gray-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p>Nenhum documento anexado</p>
                        <p className="text-sm">Faça upload de petições, provas e outros documentos</p>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Aba Tarefas */}
                <TabsContent value="tarefas" className="mt-0 h-full">
                  <Card className="h-full">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                          <CheckSquare className="w-4 h-4" />
                          Tarefas e Checklist
                        </span>
                                                 <Button variant="outline" size="sm">
                           <Plus className="w-4 h-4" />
                           <span>Nova Tarefa</span>
                         </Button>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center py-8 text-gray-500">
                        <CheckSquare className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p>Nenhuma tarefa criada</p>
                        <p className="text-sm">Crie tarefas para organizar o trabalho do processo</p>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </div>
            </Tabs>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
