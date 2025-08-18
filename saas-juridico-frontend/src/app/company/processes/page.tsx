"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { 
  Plus, 
  Search, 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  Eye,
  Scale,
  AlertTriangle,
  Download,
  RefreshCw,
  Clock
} from "lucide-react";
import { useProcesses, type Process } from "@/hooks/useProcesses";
import { useCNJIntegration } from "@/hooks/useCNJIntegration";
import { Loading } from "@/components/ui/loading";
import { SearchableSelect } from "@/components/SearchableSelect";

import { ProcessDetailsModal } from "@/components/ProcessDetailsModal";
import { toast } from "sonner";

export default function ProcessesPage() {
  const { processes, loading, createProcess, updateProcess, deleteProcess, filterProcesses } = useProcesses();
  const { sincronizarProcesso } = useCNJIntegration();
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedProcess, setSelectedProcess] = useState<Process | null>(null);

  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  // Filtrar processos
  const filteredProcesses = filterProcesses(searchTerm) || [];

  // Deletar processo
  const handleDeleteProcess = async (processId: string) => {
    if (!confirm("Tem certeza que deseja excluir este processo?")) {
      return;
    }
    await deleteProcess(processId);
  };

  // Sincronizar processo com CNJ
  const handleSyncProcess = async (processId: string) => {
    await sincronizarProcesso(processId);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("pt-BR");
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

  if (loading) {
    return (
      <Loading message="Carregando processos..." />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Processos</h1>
          <p className="text-muted-foreground">
            Gerencie seus processos jurídicos
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Novo Processo
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Criar Novo Processo</DialogTitle>
            </DialogHeader>
            <CreateProcessForm 
              onSuccess={() => {
                setIsCreateDialogOpen(false);
              }}
              createProcess={createProcess}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por assunto, CNJ, tribunal ou cliente..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Processos */}
      <Card>
        <CardHeader>
          <CardTitle>
            {filteredProcesses.length} processo{filteredProcesses.length !== 1 ? 's' : ''} encontrado{filteredProcesses.length !== 1 ? 's' : ''}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Processo</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>CNJ</TableHead>
                <TableHead>Tribunal</TableHead>
                <TableHead>Prioridade</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Criado em</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredProcesses.map((process) => (
                <TableRow key={process.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Scale className="w-4 h-4 text-primary" />
                      </div>
                      <div>
                        <div className="font-medium">{process.subject}</div>
                        {process.requires_attention && (
                          <Badge variant="destructive" className="text-xs">
                            <AlertTriangle className="w-3 h-3 mr-1" />
                            Atenção
                          </Badge>
                        )}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {process.client?.name || "Cliente não encontrado"}
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm font-mono">
                      {process.cnj_number || "-"}
                    </span>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm">
                      {process.court || "-"}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getPriorityColor(process.priority)}>
                      {getPriorityLabel(process.priority)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStatusColor(process.status)}>
                      {getStatusLabel(process.status)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm text-muted-foreground">
                      {formatDate(process.created_at)}
                    </span>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => {
                          setSelectedProcess(process);
                          setIsDetailsOpen(true);
                        }}>
                          <Eye className="w-4 h-4 mr-2" />
                          Visualizar
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => {
                          setSelectedProcess(process);
                          setIsEditDialogOpen(true);
                        }}>
                          <Edit className="w-4 h-4 mr-2" />
                          Editar
                        </DropdownMenuItem>
                        {process.cnj_number && (
                          <DropdownMenuItem 
                            onClick={() => handleSyncProcess(process.id)}
                          >
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Sincronizar com CNJ
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuItem 
                          onClick={() => handleDeleteProcess(process.id)}
                          className="text-destructive"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {filteredProcesses.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              {searchTerm ? "Nenhum processo encontrado para esta busca." : "Nenhum processo cadastrado ainda."}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog de Edição */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Editar Processo</DialogTitle>
          </DialogHeader>
          {selectedProcess && (
            <EditProcessForm 
              process={selectedProcess}
              onSuccess={() => {
                setIsEditDialogOpen(false);
                setSelectedProcess(null);
              }}
              updateProcess={updateProcess}
            />
          )}
        </DialogContent>
      </Dialog>



      {/* Modal de Detalhes do Processo */}
      <ProcessDetailsModal
        process={selectedProcess}
        isOpen={isDetailsOpen}
        onClose={() => {
          setIsDetailsOpen(false);
          setSelectedProcess(null);
        }}
      />
    </div>
  );
}

// Componente para criar processo
function CreateProcessForm({ onSuccess, createProcess }: { onSuccess: () => void; createProcess: (data: any) => Promise<any> }) {
  const [formData, setFormData] = useState({
    subject: "",
    cnj_number: "",
    court: "",
    jurisdiction: "",
    client_id: "",
    specialty_ids: [] as string[],
    priority: "normal" as "low" | "normal" | "high" | "urgent",
    estimated_value: "",
    notes: "",
    is_confidential: false,
    requires_attention: false,
    lawyers: [] as any[]
  });
  const [loading, setLoading] = useState(false);
  const [importingCNJ, setImportingCNJ] = useState(false);
  const [selectedClient, setSelectedClient] = useState<any[]>([]);
  const [selectedSpecialties, setSelectedSpecialties] = useState<any[]>([]);
  const [selectedLawyers, setSelectedLawyers] = useState<any[]>([]);
  
  const { consultarProcesso } = useCNJIntegration();

  // Função para importar dados do CNJ
  const importarDadosCNJ = async () => {
    if (!formData.cnj_number.trim()) {
      toast.error("Digite um número CNJ válido");
      return;
    }

    setImportingCNJ(true);
    try {
      const dadosCNJ = await consultarProcesso(formData.cnj_number);
      
      if (dadosCNJ) {
        // Função utilitária para extrair valor
        const extractValue = (field: any): string => {
          if (typeof field === 'string') return field;
          if (typeof field === 'object' && field?.nome) return field.nome;
          if (typeof field === 'object' && field?.codigo) return field.codigo;
          return "";
        };

        // Atualizar formulário com dados do CNJ
        setFormData(prev => ({
          ...prev,
          subject: extractValue(dadosCNJ.assunto) || prev.subject,
          court: extractValue(dadosCNJ.tribunal) || prev.court,
          jurisdiction: extractValue(dadosCNJ.orgao_julgador) || prev.jurisdiction,
          estimated_value: dadosCNJ.valor_causa ? 
            (parseFloat(dadosCNJ.valor_causa.replace(/[^\d,.-]/g, '').replace(',', '.')) * 100).toString() : 
            prev.estimated_value,
          notes: `Importado do CNJ em ${new Date().toLocaleString('pt-BR')}. ${prev.notes}`
        }));

        toast.success("Dados importados com sucesso do CNJ!");
      }
    } catch (error) {
      console.error("Erro ao importar dados CNJ:", error);
      toast.error("Erro ao importar dados do CNJ");
    } finally {
      setImportingCNJ(false);
    }
  };

  // Buscar clientes
  const searchClients = async (searchTerm: string) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error("Token não encontrado");
        return [];
      }
      
      const response = await fetch(`/api/v1/company/clients?search=${searchTerm}&limit=10`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        const clientList = data.clients || data || [];
        return clientList.map((client: any) => ({
          id: client.id,
          label: client.name,
          sublabel: client.cpf_cnpj ? `Doc: ${client.cpf_cnpj}` : '',
          description: client.email || ''
        }));
      }
    } catch (error) {
      console.error("Erro ao buscar clientes:", error);
    }
    return [];
  };

  // Buscar especialidades
  const searchSpecialties = async (searchTerm: string) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error("Token não encontrado");
        return [];
      }
      
      const response = await fetch(`/api/v1/company/specialties?search=${searchTerm}&limit=10`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        const specialtyList = data.specialties || data || [];
        return specialtyList.map((specialty: any) => ({
          id: specialty.id,
          label: specialty.name,
          sublabel: specialty.code,
          description: specialty.description || ''
        }));
      }
    } catch (error) {
      console.error("Erro ao buscar especialidades:", error);
    }
    return [];
  };

  // Buscar usuários (advogados)
  const searchUsers = async (searchTerm: string) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error("Token não encontrado");
        return [];
      }
      
      const response = await fetch(`/api/v1/company/users?search=${searchTerm}&limit=10`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Verificar se é UserListResponse ou array direto
        const userList = data.users || data || [];
        return userList.map((user: any) => ({
          id: user.id,
          label: user.name,
          sublabel: user.email,
          description: user.role || ''
        }));
      }
    } catch (error) {
      console.error("Erro ao buscar usuários:", error);
    }
    return [];
  };

  // Manipular seleção de cliente
  const handleClientSelect = (option: any) => {
    if (selectedClient.length > 0) {
      // Remover seleção
      setSelectedClient([]);
      setFormData({ ...formData, client_id: "" });
    } else {
      // Adicionar seleção
      setSelectedClient([option]);
      setFormData({ ...formData, client_id: option.id });
    }
  };

  // Manipular seleção de especialidade
  const handleSpecialtySelect = (option: any) => {
    const isSelected = selectedSpecialties.find(s => s.id === option.id);
    if (isSelected) {
      // Remover especialidade
      const newSpecialties = selectedSpecialties.filter(s => s.id !== option.id);
      setSelectedSpecialties(newSpecialties);
      setFormData({ 
        ...formData, 
        specialty_ids: newSpecialties.map(s => s.id)
      });
    } else {
      // Adicionar especialidade
      const newSpecialties = [...selectedSpecialties, option];
      setSelectedSpecialties(newSpecialties);
      setFormData({ 
        ...formData, 
        specialty_ids: newSpecialties.map(s => s.id)
      });
    }
  };

  // Manipular seleção de advogado
  const handleLawyerSelect = (option: any) => {
    const isSelected = selectedLawyers.find(l => l.id === option.id);
    if (isSelected) {
      // Remover advogado
      const newLawyers = selectedLawyers.filter(l => l.id !== option.id);
      setSelectedLawyers(newLawyers);
      setFormData({ 
        ...formData, 
        lawyers: newLawyers.map((lawyer, index) => ({
          lawyer_id: lawyer.id,
          role: "lawyer",
          is_primary: index === 0, // Primeiro advogado é sempre principal
          can_sign_documents: true,
          can_manage_process: true,
          can_view_financial: false
        }))
      });
    } else {
      // Adicionar advogado
      const newLawyers = [...selectedLawyers, option];
      setSelectedLawyers(newLawyers);
      setFormData({ 
        ...formData, 
        lawyers: newLawyers.map((lawyer, index) => ({
          lawyer_id: lawyer.id,
          role: "lawyer",
          is_primary: index === 0, // Primeiro advogado é sempre principal
          can_sign_documents: true,
          can_manage_process: true,
          can_view_financial: false
        }))
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Validar se tem cliente e pelo menos um advogado
      if (selectedClient.length === 0) {
        alert("Selecione um cliente");
        return;
      }
      if (selectedLawyers.length === 0) {
        alert("Selecione pelo menos um advogado");
        return;
      }

      await createProcess(formData);
      onSuccess();
    } catch (error) {
      console.error("Erro ao criar processo:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Assunto *</label>
          <Input
            value={formData.subject}
            onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="text-sm font-medium">Prioridade</label>
          <select
            value={formData.priority}
            onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
            className="w-full p-2 border rounded-md"
          >
            <option value="low">Baixa</option>
            <option value="normal">Normal</option>
            <option value="high">Alta</option>
            <option value="urgent">Urgente</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Número CNJ</label>
          <div className="flex gap-2">
            <Input
              value={formData.cnj_number}
              onChange={(e) => setFormData({ ...formData, cnj_number: e.target.value })}
              placeholder="0000000-00.0000.0.00.0000"
            />
            <Button
              type="button"
              variant="outline"
              onClick={importarDadosCNJ}
              disabled={importingCNJ || !formData.cnj_number.trim()}
              className="whitespace-nowrap"
            >
              {importingCNJ ? (
                <>
                  <Clock className="w-4 h-4 animate-spin mr-2" />
                  Importando...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  Importar CNJ
                </>
              )}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Digite o número CNJ e clique em "Importar CNJ" para preencher automaticamente
          </p>
        </div>
        <div>
          <label className="text-sm font-medium">Tribunal</label>
          <Input
            value={formData.court}
            onChange={(e) => setFormData({ ...formData, court: e.target.value })}
          />
        </div>
      </div>

      <div>
        <label className="text-sm font-medium">Comarca</label>
        <Input
          value={formData.jurisdiction}
          onChange={(e) => setFormData({ ...formData, jurisdiction: e.target.value })}
        />
      </div>

      {/* Seleção de Cliente */}
      <SearchableSelect
        label="Cliente"
        placeholder="Buscar por nome ou documento..."
        searchFunction={searchClients}
        onSelect={handleClientSelect}
        selectedOptions={selectedClient}
        multiple={false}
        required={true}
      />

      {/* Seleção de Especialidades */}
      <SearchableSelect
        label="Especialidades"
        placeholder="Buscar especialidades..."
        searchFunction={searchSpecialties}
        onSelect={handleSpecialtySelect}
        selectedOptions={selectedSpecialties}
        multiple={true}
        required={false}
      />

      {/* Seleção de Advogados */}
      <SearchableSelect
        label="Advogados"
        placeholder="Buscar advogados..."
        searchFunction={searchUsers}
        onSelect={handleLawyerSelect}
        selectedOptions={selectedLawyers}
        multiple={true}
        required={true}
      />

      <div>
        <label className="text-sm font-medium">Valor Estimado (centavos)</label>
        <Input
          type="number"
          value={formData.estimated_value}
          onChange={(e) => setFormData({ ...formData, estimated_value: e.target.value })}
        />
      </div>

      <div>
        <label className="text-sm font-medium">Observações</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="w-full p-2 border rounded-md"
          rows={3}
        />
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="is_confidential"
            checked={formData.is_confidential}
            onChange={(e) => setFormData({ ...formData, is_confidential: e.target.checked })}
          />
          <label htmlFor="is_confidential" className="text-sm font-medium">
            Confidencial
          </label>
        </div>
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="requires_attention"
            checked={formData.requires_attention}
            onChange={(e) => setFormData({ ...formData, requires_attention: e.target.checked })}
          />
          <label htmlFor="requires_attention" className="text-sm font-medium">
            Requer Atenção
          </label>
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onSuccess}>
          Cancelar
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? "Criando..." : "Criar Processo"}
        </Button>
      </div>
    </form>
  );
}

// Componente para editar processo
function EditProcessForm({ process, onSuccess, updateProcess }: { process: Process; onSuccess: () => void; updateProcess: (id: string, data: any) => Promise<any> }) {
  const [formData, setFormData] = useState({
    subject: process.subject,
    cnj_number: process.cnj_number || "",
    court: process.court || "",
    jurisdiction: process.jurisdiction || "",
    client_id: process.client_id,
    specialty_id: process.specialty_id || "",
    priority: process.priority,
    estimated_value: process.estimated_value?.toString() || "",
    notes: process.notes || "",
    is_confidential: process.is_confidential,
    requires_attention: process.requires_attention,
    status: process.status
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await updateProcess(process.id, formData);
      onSuccess();
    } catch (error) {
      console.error("Erro ao atualizar processo:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Assunto *</label>
          <Input
            value={formData.subject}
            onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="text-sm font-medium">Status</label>
          <select
            value={formData.status}
            onChange={(e) => setFormData({ ...formData, status: e.target.value })}
            className="w-full p-2 border rounded-md"
          >
            <option value="active">Ativo</option>
            <option value="closed">Encerrado</option>
            <option value="suspended">Suspenso</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Prioridade</label>
          <select
            value={formData.priority}
            onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
            className="w-full p-2 border rounded-md"
          >
            <option value="low">Baixa</option>
            <option value="normal">Normal</option>
            <option value="high">Alta</option>
            <option value="urgent">Urgente</option>
          </select>
        </div>
        <div>
          <label className="text-sm font-medium">Número CNJ</label>
          <Input
            value={formData.cnj_number}
            onChange={(e) => setFormData({ ...formData, cnj_number: e.target.value })}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Tribunal</label>
          <Input
            value={formData.court}
            onChange={(e) => setFormData({ ...formData, court: e.target.value })}
          />
        </div>
        <div>
          <label className="text-sm font-medium">Comarca</label>
          <Input
            value={formData.jurisdiction}
            onChange={(e) => setFormData({ ...formData, jurisdiction: e.target.value })}
          />
        </div>
      </div>

      <div>
        <label className="text-sm font-medium">Cliente ID *</label>
        <Input
          value={formData.client_id}
          onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
          required
        />
      </div>

      <div>
        <label className="text-sm font-medium">Valor Estimado (centavos)</label>
        <Input
          type="number"
          value={formData.estimated_value}
          onChange={(e) => setFormData({ ...formData, estimated_value: e.target.value })}
        />
      </div>

      <div>
        <label className="text-sm font-medium">Observações</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="w-full p-2 border rounded-md"
          rows={3}
        />
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="is_confidential_edit"
            checked={formData.is_confidential}
            onChange={(e) => setFormData({ ...formData, is_confidential: e.target.checked })}
          />
          <label htmlFor="is_confidential_edit" className="text-sm font-medium">
            Confidencial
          </label>
        </div>
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="requires_attention_edit"
            checked={formData.requires_attention}
            onChange={(e) => setFormData({ ...formData, requires_attention: e.target.checked })}
          />
          <label htmlFor="requires_attention_edit" className="text-sm font-medium">
            Requer Atenção
          </label>
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onSuccess}>
          Cancelar
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? "Salvando..." : "Salvar Alterações"}
        </Button>
      </div>
    </form>
  );
}
