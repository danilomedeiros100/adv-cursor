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
  User,
  Building2
} from "lucide-react";
import { useClients, type Client } from "@/hooks/useClients";
import { Loading } from "@/components/ui/loading";

export default function ClientsPage() {
  const { clients, loading, createClient, updateClient, deleteClient, filterClients } = useClients();
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);

  // Filtrar clientes
  const filteredClients = filterClients(searchTerm);

  // Deletar cliente
  const handleDeleteClient = async (clientId: string) => {
    if (!confirm("Tem certeza que deseja excluir este cliente?")) {
      return;
    }
    await deleteClient(clientId);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("pt-BR");
  };

  const formatCPFCNPJ = (cpfCnpj: string | null) => {
    if (!cpfCnpj) return "-";
    if (cpfCnpj.length === 11) {
      return cpfCnpj.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
    }
    if (cpfCnpj.length === 14) {
      return cpfCnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
    }
    return cpfCnpj;
  };

  if (loading) {
    return (
      <Loading message="Carregando clientes..." />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Clientes</h1>
          <p className="text-muted-foreground">
            Gerencie seus clientes e suas informações
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Novo Cliente
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Criar Novo Cliente</DialogTitle>
            </DialogHeader>
                         <CreateClientForm 
               onSuccess={() => {
                 setIsCreateDialogOpen(false);
               }}
               createClient={createClient}
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
                  placeholder="Buscar por nome, email ou CPF/CNPJ..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Clientes */}
      <Card>
        <CardHeader>
          <CardTitle>
            {filteredClients.length} cliente{filteredClients.length !== 1 ? 's' : ''} encontrado{filteredClients.length !== 1 ? 's' : ''}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cliente</TableHead>
                <TableHead>Contato</TableHead>
                <TableHead>CPF/CNPJ</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Criado em</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredClients.map((client) => (
                <TableRow key={client.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                        {client.person_type === "PF" ? (
                          <User className="w-4 h-4 text-primary" />
                        ) : (
                          <Building2 className="w-4 h-4 text-primary" />
                        )}
                      </div>
                      <div>
                        <div className="font-medium">{client.name}</div>
                        {client.is_vip && (
                          <Badge variant="secondary" className="text-xs">
                            VIP
                          </Badge>
                        )}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      {client.email && (
                        <div className="text-sm">{client.email}</div>
                      )}
                      {client.phone && (
                        <div className="text-sm text-muted-foreground">
                          {client.phone}
                        </div>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm font-mono">
                      {formatCPFCNPJ(client.cpf_cnpj)}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge variant={client.person_type === "PF" ? "default" : "secondary"}>
                      {client.person_type === "PF" ? "Pessoa Física" : "Pessoa Jurídica"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={client.is_active ? "default" : "destructive"}>
                      {client.is_active ? "Ativo" : "Inativo"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm text-muted-foreground">
                      {formatDate(client.created_at)}
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
                          setSelectedClient(client);
                          setIsEditDialogOpen(true);
                        }}>
                          <Eye className="w-4 h-4 mr-2" />
                          Visualizar
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => {
                          setSelectedClient(client);
                          setIsEditDialogOpen(true);
                        }}>
                          <Edit className="w-4 h-4 mr-2" />
                          Editar
                        </DropdownMenuItem>
                                                 <DropdownMenuItem 
                           onClick={() => handleDeleteClient(client.id)}
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

          {filteredClients.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              {searchTerm ? "Nenhum cliente encontrado para esta busca." : "Nenhum cliente cadastrado ainda."}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog de Edição */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Editar Cliente</DialogTitle>
          </DialogHeader>
                     {selectedClient && (
             <EditClientForm 
               client={selectedClient}
               onSuccess={() => {
                 setIsEditDialogOpen(false);
                 setSelectedClient(null);
               }}
               updateClient={updateClient}
             />
           )}
        </DialogContent>
      </Dialog>
      </div>
  );
}

// Componente para criar cliente
function CreateClientForm({ onSuccess, createClient }: { onSuccess: () => void; createClient: (data: any) => Promise<any> }) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    cpf_cnpj: "",
    person_type: "PF" as "PF" | "PJ",
    is_vip: false,
    notes: ""
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await createClient(formData);
      onSuccess();
    } catch (error) {
      console.error("Erro ao criar cliente:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Nome *</label>
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="text-sm font-medium">Tipo de Pessoa *</label>
          <select
            value={formData.person_type}
            onChange={(e) => setFormData({ ...formData, person_type: e.target.value as "PF" | "PJ" })}
            className="w-full p-2 border rounded-md"
            required
          >
            <option value="PF">Pessoa Física</option>
            <option value="PJ">Pessoa Jurídica</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Email</label>
          <Input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>
        <div>
          <label className="text-sm font-medium">Telefone</label>
          <Input
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          />
        </div>
      </div>

      <div>
        <label className="text-sm font-medium">
          {formData.person_type === "PF" ? "CPF" : "CNPJ"}
        </label>
        <Input
          value={formData.cpf_cnpj}
          onChange={(e) => setFormData({ ...formData, cpf_cnpj: e.target.value })}
        />
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="is_vip"
          checked={formData.is_vip}
          onChange={(e) => setFormData({ ...formData, is_vip: e.target.checked })}
        />
        <label htmlFor="is_vip" className="text-sm font-medium">
          Cliente VIP
        </label>
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

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onSuccess}>
          Cancelar
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? "Criando..." : "Criar Cliente"}
        </Button>
      </div>
    </form>
  );
}

// Componente para editar cliente
function EditClientForm({ client, onSuccess, updateClient }: { client: Client; onSuccess: () => void; updateClient: (id: string, data: any) => Promise<any> }) {
  const [formData, setFormData] = useState({
    name: client.name,
    email: client.email || "",
    phone: client.phone || "",
    cpf_cnpj: client.cpf_cnpj || "",
    person_type: client.person_type,
    is_vip: client.is_vip,
    notes: ""
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await updateClient(client.id, formData);
      onSuccess();
    } catch (error) {
      console.error("Erro ao atualizar cliente:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Nome *</label>
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="text-sm font-medium">Tipo de Pessoa *</label>
          <select
            value={formData.person_type}
            onChange={(e) => setFormData({ ...formData, person_type: e.target.value as "PF" | "PJ" })}
            className="w-full p-2 border rounded-md"
            required
          >
            <option value="PF">Pessoa Física</option>
            <option value="PJ">Pessoa Jurídica</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Email</label>
          <Input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>
        <div>
          <label className="text-sm font-medium">Telefone</label>
          <Input
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          />
        </div>
      </div>

      <div>
        <label className="text-sm font-medium">
          {formData.person_type === "PF" ? "CPF" : "CNPJ"}
        </label>
        <Input
          value={formData.cpf_cnpj}
          onChange={(e) => setFormData({ ...formData, cpf_cnpj: e.target.value })}
        />
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="is_vip_edit"
          checked={formData.is_vip}
          onChange={(e) => setFormData({ ...formData, is_vip: e.target.checked })}
        />
        <label htmlFor="is_vip_edit" className="text-sm font-medium">
          Cliente VIP
        </label>
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
