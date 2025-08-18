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
  AlertTriangle
} from "lucide-react";
import { useProcesses, type Process } from "@/hooks/useProcesses";
import { Loading } from "@/components/ui/loading";

export default function ProcessesPage() {
  const { processes, loading, createProcess, updateProcess, deleteProcess, filterProcesses } = useProcesses();
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedProcess, setSelectedProcess] = useState<Process | null>(null);

  // Filtrar processos
  const filteredProcesses = filterProcesses(searchTerm) || [];

  // Deletar processo
  const handleDeleteProcess = async (processId: string) => {
    if (!confirm("Tem certeza que deseja excluir este processo?")) {
      return;
    }
    await deleteProcess(processId);
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
                          setIsEditDialogOpen(true);
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
    client_search: "",
    specialty_ids: [] as string[],
    priority: "normal" as "low" | "normal" | "high" | "urgent",
    estimated_value: "",
    notes: "",
    is_confidential: false,
    requires_attention: false,
    lawyers: [] as any[]
  });
  const [loading, setLoading] = useState(false);
  const [clients, setClients] = useState<any[]>([]);
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [showClientResults, setShowClientResults] = useState(false);
  const [showSpecialtyResults, setShowSpecialtyResults] = useState(false);
  const [showLawyerResults, setShowLawyerResults] = useState(false);
  const [selectedClient, setSelectedClient] = useState<any>(null);
  const [selectedSpecialties, setSelectedSpecialties] = useState<any[]>([]);
  const [selectedLawyers, setSelectedLawyers] = useState<any[]>([]);

  // Buscar clientes
  const searchClients = async (searchTerm: string) => {
    if (!searchTerm || searchTerm.length < 2) {
      setClients([]);
      setShowClientResults(false);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/company/clients?search=${searchTerm}&limit=10`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem('token')}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        const clientList = data.clients || data || [];
        setClients(clientList);
        setShowClientResults(true);
      }
    } catch (error) {
      console.error("Erro ao buscar clientes:", error);
    }
  };

  // Buscar especialidades
  const searchSpecialties = async (searchTerm: string) => {
    if (!searchTerm || searchTerm.length < 2) {
      setSpecialties([]);
      setShowSpecialtyResults(false);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/company/specialties?search=${searchTerm}&limit=10`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem('token')}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        const specialtyList = data.specialties || data || [];
        setSpecialties(specialtyList);
        setShowSpecialtyResults(true);
      }
    } catch (error) {
      console.error("Erro ao buscar especialidades:", error);
    }
  };

  // Buscar usuários (advogados)
  const searchUsers = async (searchTerm: string) => {
    if (!searchTerm || searchTerm.length < 2) {
      setUsers([]);
      setShowLawyerResults(false);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/company/users?search=${searchTerm}&limit=10`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem('token')}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        const userList = data.users || data || [];
        setUsers(userList);
        setShowLawyerResults(true);
      }
    } catch (error) {
      console.error("Erro ao buscar usuários:", error);
    }
  };

  // Selecionar cliente
  const selectClient = (client: any) => {
    setSelectedClient(client);
    setFormData({ ...formData, client_id: client.id, client_search: client.name });
    setShowClientResults(false);
  };

  // Selecionar especialidade
  const selectSpecialty = (specialty: any) => {
    if (!selectedSpecialties.find(s => s.id === specialty.id)) {
      setSelectedSpecialties([...selectedSpecialties, specialty]);
      setFormData({ ...formData, specialty_ids: [...formData.specialty_ids, specialty.id] });
    }
    setShowSpecialtyResults(false);
  };

  // Remover especialidade
  const removeSpecialty = (specialtyId: string) => {
    setSelectedSpecialties(selectedSpecialties.filter(s => s.id !== specialtyId));
    setFormData({ ...formData, specialty_ids: formData.specialty_ids.filter(id => id !== specialtyId) });
  };

  // Selecionar advogado
  const selectLawyer = (user: any) => {
    if (!selectedLawyers.find(l => l.id === user.id)) {
      setSelectedLawyers([...selectedLawyers, user]);
      setFormData({ 
        ...formData, 
        lawyers: [...formData.lawyers, {
          lawyer_id: user.id,
          role: "lawyer",
          is_primary: selectedLawyers.length === 0, // Primeiro advogado é principal
          can_sign_documents: true,
          can_manage_process: true,
          can_view_financial: false
        }]
      });
    }
    setShowLawyerResults(false);
  };

  // Remover advogado
  const removeLawyer = (lawyerId: string) => {
    setSelectedLawyers(selectedLawyers.filter(l => l.id !== lawyerId));
    setFormData({ 
      ...formData, 
      lawyers: formData.lawyers.filter(l => l.lawyer_id !== lawyerId)
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Validar se tem cliente e pelo menos um advogado
      if (!selectedClient) {
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
          <Input
            value={formData.cnj_number}
            onChange={(e) => setFormData({ ...formData, cnj_number: e.target.value })}
          />
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
      <div className="relative">
        <label className="text-sm font-medium">Cliente *</label>
        <Input
          placeholder="Buscar por nome ou documento..."
          value={formData.client_search}
          onChange={(e) => {
            setFormData({ ...formData, client_search: e.target.value });
            searchClients(e.target.value);
          }}
          onFocus={() => {
            if (formData.client_search.length >= 2) {
              setShowClientResults(true);
            }
          }}
        />
        {showClientResults && clients.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
            {clients.map((client) => (
              <div
                key={client.id}
                className="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b last:border-b-0"
                onClick={() => selectClient(client)}
              >
                <div className="font-medium">{client.name}</div>
                <div className="text-sm text-gray-600">
                  {client.cpf_cnpj ? `Doc: ${client.cpf_cnpj}` : ''}
                  {client.email ? ` | ${client.email}` : ''}
                </div>
              </div>
            ))}
          </div>
        )}
        {selectedClient && (
          <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded-md">
            <div className="text-sm font-medium text-green-800">Cliente selecionado: {selectedClient.name}</div>
            <button
              type="button"
              onClick={() => {
                setSelectedClient(null);
                setFormData({ ...formData, client_id: "", client_search: "" });
              }}
              className="text-xs text-green-600 hover:text-green-800"
            >
              Remover
            </button>
          </div>
        )}
      </div>

      {/* Seleção de Especialidades */}
      <div className="relative">
        <label className="text-sm font-medium">Especialidades</label>
        <Input
          placeholder="Buscar especialidades..."
          onChange={(e) => searchSpecialties(e.target.value)}
          onFocus={() => setShowSpecialtyResults(true)}
        />
        {showSpecialtyResults && specialties.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
            {specialties.map((specialty) => (
              <div
                key={specialty.id}
                className="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b last:border-b-0"
                onClick={() => selectSpecialty(specialty)}
              >
                <div className="font-medium">{specialty.name}</div>
                <div className="text-sm text-gray-600">{specialty.description}</div>
              </div>
            ))}
          </div>
        )}
        {selectedSpecialties.length > 0 && (
          <div className="mt-2 space-y-1">
            {selectedSpecialties.map((specialty) => (
              <div key={specialty.id} className="flex items-center justify-between p-2 bg-blue-50 border border-blue-200 rounded-md">
                <span className="text-sm font-medium text-blue-800">{specialty.name}</span>
                <button
                  type="button"
                  onClick={() => removeSpecialty(specialty.id)}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  Remover
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Seleção de Advogados */}
      <div className="relative">
        <label className="text-sm font-medium">Advogados *</label>
        <Input
          placeholder="Buscar advogados..."
          onChange={(e) => searchUsers(e.target.value)}
          onFocus={() => setShowLawyerResults(true)}
        />
        {showLawyerResults && users.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
            {users.map((user) => (
              <div
                key={user.id}
                className="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b last:border-b-0"
                onClick={() => selectLawyer(user)}
              >
                <div className="font-medium">{user.name}</div>
                <div className="text-sm text-gray-600">{user.email}</div>
              </div>
            ))}
          </div>
        )}
        {selectedLawyers.length > 0 && (
          <div className="mt-2 space-y-1">
            {selectedLawyers.map((lawyer, index) => (
              <div key={lawyer.id} className="flex items-center justify-between p-2 bg-purple-50 border border-purple-200 rounded-md">
                <div>
                  <span className="text-sm font-medium text-purple-800">{lawyer.name}</span>
                  {index === 0 && (
                    <span className="ml-2 text-xs bg-purple-200 text-purple-800 px-2 py-1 rounded">Principal</span>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => removeLawyer(lawyer.id)}
                  className="text-xs text-purple-600 hover:text-purple-800"
                >
                  Remover
                </button>
              </div>
            ))}
          </div>
        )}
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
