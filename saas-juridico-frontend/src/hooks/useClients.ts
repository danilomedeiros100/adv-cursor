import { useState, useEffect } from "react";
import { useAuth } from "./useAuth";
import { toast } from "sonner";
import { 
  Client, 
  CreateClientData, 
  UpdateClientData, 
  ClientStats 
} from "@/types/client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export function useClients() {
  const { token } = useAuth();
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Buscar todos os clientes (apenas ativos por padrão)
  const fetchClients = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/company/clients?is_active=true`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar clientes`);
      }

      const data = await response.json();
      // Verificar se é ClientListResponse ou array direto
      if (data && typeof data === 'object' && 'clients' in data) {
        setClients(data.clients || []);
      } else {
        setClients(data || []);
      }
    } catch (error) {
      console.error(`Erro ao buscar clientes:`, error);
      setError(`Erro ao carregar clientes`);
      toast.error(`Erro ao carregar clientes`);
    } finally {
      setLoading(false);
    }
  };

  // Criar novo cliente
  const createClient = async (clientData: CreateClientData): Promise<Client | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/clients`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(clientData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao criar cliente`);
      }

      const newClient = await response.json();
      setClients(prev => [...prev, newClient]);
      toast.success(`Cliente criado com sucesso`);
      return newClient;
    } catch (error) {
      console.error(`Erro ao criar cliente:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao criar cliente`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar cliente
  const updateClient = async (clientId: string, clientData: UpdateClientData): Promise<Client | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/clients/${clientId}`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(clientData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao atualizar cliente`);
      }

      const updatedClient = await response.json();
      setClients(prev => prev.map(client => 
        client.id === clientId ? updatedClient : client
      ));
      toast.success(`Cliente atualizado com sucesso`);
      return updatedClient;
    } catch (error) {
      console.error(`Erro ao atualizar cliente:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao atualizar cliente`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Deletar cliente
  const deleteClient = async (clientId: string): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/clients/${clientId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao deletar cliente`);
      }

      setClients(prev => prev.filter(client => client.id !== clientId));
      toast.success(`Cliente deletado com sucesso`);
      return true;
    } catch (error) {
      console.error(`Erro ao deletar cliente:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao deletar cliente`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Reativar cliente
  const activateClient = async (clientId: string): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/clients/${clientId}/activate`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao reativar cliente`);
      }

      // Atualizar o status na lista
      setClients(prev => prev.map(client => 
        client.id === clientId ? { ...client, is_active: true } : client
      ));
      toast.success(`Cliente reativado com sucesso`);
      return true;
    } catch (error) {
      console.error(`Erro ao reativar cliente:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao reativar cliente`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Buscar cliente específico
  const getClient = async (clientId: string): Promise<Client | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/clients/${clientId}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Cliente não encontrado`);
      }

      const client = await response.json();
      return client;
    } catch (error) {
      console.error(`Erro ao buscar cliente:`, error);
      setError(`Erro ao buscar cliente`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Obter estatísticas
  const getClientStats = async (): Promise<ClientStats | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/clients/stats/summary`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao obter estatísticas`);
      }

      const stats = await response.json();
      return stats;
    } catch (error) {
      console.error(`Erro ao obter estatísticas:`, error);
      setError(`Erro ao obter estatísticas`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Filtrar clientes
  const filterClients = (searchTerm: string) => {
    // Garantir que clients seja sempre um array
    if (!Array.isArray(clients)) {
      console.warn('clients não é um array:', clients);
      return [];
    }
    
    return clients.filter(client =>
      client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (client.email && client.email.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (client.cpf_cnpj && client.cpf_cnpj.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (client.company_name && client.company_name.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  };

  // Carregar clientes na inicialização
  useEffect(() => {
    if (token) {
      fetchClients();
    }
  }, [token]);

  return {
    clients,
    loading,
    error,
    fetchClients,
    createClient,
    updateClient,
    deleteClient,
    activateClient,
    getClient,
    getClientStats,
    filterClients,
  };
}
