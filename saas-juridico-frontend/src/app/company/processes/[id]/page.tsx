"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  ArrowLeft,
  Calendar,
  Clock,
  FileText,
  Users,
  DollarSign,
  AlertTriangle,
  Plus,
  Edit,
  Download,
  Eye,
  CheckCircle,
  XCircle,
  Scale,
  Gavel,
  MessageSquare,
  Upload,
  Search,
  Filter,
  MoreHorizontal
} from "lucide-react";
import { useProcesses } from "@/hooks/useProcesses";
import { Loading } from "@/components/ui/loading";
import { toast } from "sonner";
import { ProcessTimeline } from "@/components/ProcessTimeline";
import { ProcessDeadlines } from "@/components/ProcessDeadlines";
import { ProcessDocuments } from "@/components/ProcessDocuments";
import { ProcessFinancial } from "@/components/ProcessFinancial";
import { ProcessNotes } from "@/components/ProcessNotes";

interface ProcessDetail {
  id: string;
  subject: string;
  cnj_number?: string;
  court?: string;
  jurisdiction?: string;
  status: string;
  priority: string;
  estimated_value?: number;
  notes?: string;
  is_confidential: boolean;
  requires_attention: boolean;
  created_at: string;
  updated_at?: string;
  client?: {
    id: string;
    name: string;
    email?: string;
    phone?: string;
  };
  specialty?: {
    id: string;
    name: string;
    code: string;
  };
  lawyers?: Array<{
    id: string;
    lawyer: {
      id: string;
      name: string;
      email: string;
    };
    role: string;
    is_primary: boolean;
  }>;
}

export default function ProcessDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { getProcess } = useProcesses();
  
  const [process, setProcess] = useState<ProcessDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("timeline");

  const processId = params.id as string;

  useEffect(() => {
    if (processId) {
      loadProcessDetails();
    }
  }, [processId]);

  const loadProcessDetails = async () => {
    setLoading(true);
    try {
      const processData = await getProcess(processId);
      if (processData) {
        setProcess(processData as ProcessDetail);
      } else {
        toast.error("Processo não encontrado");
        router.push("/company/processes");
      }
    } catch (error) {
      console.error("Erro ao carregar processo:", error);
      toast.error("Erro ao carregar detalhes do processo");
    } finally {
      setLoading(false);
    }
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

  const formatCurrency = (value?: number) => {
    if (!value) return "Não informado";
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value / 100); // Assumindo que o valor está em centavos
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  if (loading) {
    return <Loading message="Carregando processo..." />;
  }

  if (!process) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <XCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Processo não encontrado</h2>
          <p className="text-gray-600 mb-4">O processo solicitado não foi encontrado.</p>
          <Button onClick={() => router.push("/company/processes")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar aos Processos
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push("/company/processes")}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{process.subject}</h1>
            <p className="text-muted-foreground">
              CNJ: {process.cnj_number || "Não informado"} • 
              Criado em {formatDate(process.created_at)}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant={getPriorityColor(process.priority)}>
            {getPriorityLabel(process.priority)}
          </Badge>
          <Badge variant={getStatusColor(process.status)}>
            {getStatusLabel(process.status)}
          </Badge>
          {process.requires_attention && (
            <Badge variant="destructive">
              <AlertTriangle className="h-3 w-3 mr-1" />
              Atenção
            </Badge>
          )}
          <Button size="sm">
            <Edit className="h-4 w-4 mr-2" />
            Editar
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Conteúdo Principal */}
        <div className="lg:col-span-3">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
              <TabsTrigger value="documents">Documentos</TabsTrigger>
              <TabsTrigger value="deadlines">Prazos</TabsTrigger>
              <TabsTrigger value="financial">Financeiro</TabsTrigger>
              <TabsTrigger value="notes">Anotações</TabsTrigger>
            </TabsList>

            <TabsContent value="timeline" className="space-y-4">
              <ProcessTimeline processId={process.id} />
            </TabsContent>

            <TabsContent value="documents" className="space-y-4">
              <ProcessDocuments processId={process.id} />
            </TabsContent>

            <TabsContent value="deadlines" className="space-y-4">
              <ProcessDeadlines processId={process.id} />
            </TabsContent>

            <TabsContent value="financial" className="space-y-4">
              <ProcessFinancial processId={process.id} />
            </TabsContent>

            <TabsContent value="notes" className="space-y-4">
              <ProcessNotes processId={process.id} />
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Informações do Processo */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Scale className="h-5 w-5" />
                <span>Informações</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-600">Tribunal</label>
                <p className="text-sm">{process.court || "Não informado"}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-600">Comarca</label>
                <p className="text-sm">{process.jurisdiction || "Não informado"}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-600">Especialidade</label>
                <p className="text-sm">{process.specialty?.name || "Não informado"}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-600">Valor Estimado</label>
                <p className="text-sm font-medium">{formatCurrency(process.estimated_value)}</p>
              </div>
              
              {process.notes && (
                <div>
                  <label className="text-sm font-medium text-gray-600">Observações</label>
                  <p className="text-sm text-gray-700">{process.notes}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Cliente */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Cliente</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <h4 className="font-medium">{process.client?.name}</h4>
                {process.client?.email && (
                  <p className="text-sm text-gray-600">{process.client.email}</p>
                )}
                {process.client?.phone && (
                  <p className="text-sm text-gray-600">{process.client.phone}</p>
                )}
              </div>
              <Button variant="outline" size="sm" className="w-full">
                <Eye className="h-4 w-4 mr-2" />
                Ver Cliente
              </Button>
            </CardContent>
          </Card>

          {/* Equipe */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Equipe</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {process.lawyers?.map((lawyer) => (
                <div key={lawyer.id} className="flex items-center justify-between p-2 border rounded">
                  <div>
                    <p className="text-sm font-medium">{lawyer.lawyer.name}</p>
                    <p className="text-xs text-gray-600">{lawyer.role}</p>
                  </div>
                  {lawyer.is_primary && (
                    <Badge variant="default" className="text-xs">
                      Principal
                    </Badge>
                  )}
                </div>
              ))}
              
              {(!process.lawyers || process.lawyers.length === 0) && (
                <p className="text-sm text-gray-500 text-center py-4">
                  Nenhum advogado atribuído
                </p>
              )}
              
              <Button variant="outline" size="sm" className="w-full">
                <Plus className="h-4 w-4 mr-2" />
                Adicionar Advogado
              </Button>
            </CardContent>
          </Card>

          {/* Ações Rápidas */}
          <Card>
            <CardHeader>
              <CardTitle>Ações Rápidas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start">
                <FileText className="h-4 w-4 mr-2" />
                Nova Petição
              </Button>
              
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Calendar className="h-4 w-4 mr-2" />
                Adicionar Prazo
              </Button>
              
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Upload className="h-4 w-4 mr-2" />
                Upload Documento
              </Button>
              
              <Button variant="outline" size="sm" className="w-full justify-start">
                <MessageSquare className="h-4 w-4 mr-2" />
                Enviar Mensagem
              </Button>
              
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Download className="h-4 w-4 mr-2" />
                Exportar Dados
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
