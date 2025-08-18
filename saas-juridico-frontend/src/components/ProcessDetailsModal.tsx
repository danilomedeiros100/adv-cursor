"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
  CheckCircle
} from "lucide-react";
import { Process } from "@/types/process";
import { useCNJIntegration } from "@/hooks/useCNJIntegration";
import { toast } from "sonner";

interface ProcessDetailsModalProps {
  process: Process | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ProcessDetailsModal({ process, isOpen, onClose }: ProcessDetailsModalProps) {
  const { sincronizarProcesso, verificarStatus } = useCNJIntegration();
  const [cnjStatus, setCnjStatus] = useState<any>(null);
  const [loadingStatus, setLoadingStatus] = useState(false);

  useEffect(() => {
    if (process?.cnj_number && isOpen) {
      checkCNJStatus();
    }
  }, [process?.cnj_number, isOpen]);

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
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "Não informado";
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  // Função utilitária para extrair valor de campo que pode ser string ou objeto
  const extractValue = (field: any): string => {
    if (typeof field === 'string') return field;
    if (typeof field === 'object' && field?.nome) return field.nome;
    if (typeof field === 'object' && field?.codigo) return field.codigo;
    return "Não informado";
  };

  const formatCurrency = (value?: number) => {
    if (!value) return "Não informado";
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value / 100); // Assumindo que o valor está em centavos
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "urgent":
        return "destructive";
      case "high":
        return "default";
      case "normal":
        return "secondary";
      case "low":
        return "outline";
      default:
        return "secondary";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "default";
      case "closed":
        return "secondary";
      case "suspended":
        return "destructive";
      default:
        return "secondary";
    }
  };

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case "urgent":
        return "Urgente";
      case "high":
        return "Alta";
      case "normal":
        return "Normal";
      case "low":
        return "Baixa";
      default:
        return priority;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "active":
        return "Ativo";
      case "closed":
        return "Encerrado";
      case "suspended":
        return "Suspenso";
      default:
        return status;
    }
  };

  if (!process) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Scale className="w-5 h-5" />
            Detalhes do Processo
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Informações Básicas */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Informações Básicas</span>
                <div className="flex gap-2">
                  <Badge variant={getPriorityColor(process.priority)}>
                    {getPriorityLabel(process.priority)}
                  </Badge>
                  <Badge variant={getStatusColor(process.status)}>
                    {getStatusLabel(process.status)}
                  </Badge>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Assunto</label>
                  <p className="text-sm text-gray-600">{process.subject}</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Cliente</label>
                  <p className="text-sm text-gray-600">{process.client?.name || "Não informado"}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium">Número CNJ</label>
                  <p className="text-sm font-mono text-gray-600">
                    {process.cnj_number || "Não informado"}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium">Tribunal</label>
                  <p className="text-sm text-gray-600">{extractValue(process.court)}</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Comarca</label>
                  <p className="text-sm text-gray-600">{extractValue(process.jurisdiction)}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
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

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={process.is_confidential}
                    readOnly
                  />
                  <label className="text-sm font-medium">Confidencial</label>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={process.requires_attention}
                    readOnly
                  />
                  <label className="text-sm font-medium">Requer Atenção</label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Integração CNJ */}
          {process.cnj_number && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Building className="w-4 h-4" />
                    Integração CNJ
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleSync}
                    disabled={loadingStatus}
                  >
                    <RefreshCw className={`w-4 h-4 mr-2 ${loadingStatus ? 'animate-spin' : ''}`} />
                    Sincronizar
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loadingStatus ? (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Clock className="w-4 h-4 animate-spin" />
                    Verificando status...
                  </div>
                ) : cnjStatus ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      {cnjStatus.exists ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-yellow-600" />
                      )}
                      <span className="text-sm font-medium">
                        {cnjStatus.exists ? "Processo encontrado na API CNJ" : "Processo não encontrado na API CNJ"}
                      </span>
                    </div>

                    {cnjStatus.exists && (
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <label className="font-medium">Status no CNJ</label>
                          <p className="text-gray-600">{extractValue(cnjStatus.status)}</p>
                        </div>
                        <div>
                          <label className="font-medium">Última Atualização</label>
                          <p className="text-gray-600">{extractValue(cnjStatus.last_update)}</p>
                        </div>
                        <div>
                          <label className="font-medium">Tribunal</label>
                          <p className="text-gray-600">{extractValue(cnjStatus.court)}</p>
                        </div>
                        <div>
                          <label className="font-medium">Assunto</label>
                          <p className="text-gray-600">{extractValue(cnjStatus.subject)}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-gray-600">
                    Clique em "Sincronizar" para verificar o status na API CNJ
                  </div>
                )}
              </CardContent>
            </Card>
          )}

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
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <label className="font-medium">Criado em</label>
                  <p className="text-gray-600">{formatDate(process.created_at)}</p>
                </div>
                {process.updated_at && (
                  <div>
                    <label className="font-medium">Atualizado em</label>
                    <p className="text-gray-600">{formatDate(process.updated_at)}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-end">
          <Button onClick={onClose}>
            Fechar
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
