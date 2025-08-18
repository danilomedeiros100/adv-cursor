import { useState, useEffect } from "react";
import { useAuth } from "./useAuth";
import { toast } from "sonner";
import { 
  Process, 
  CreateProcessData, 
  UpdateProcessData, 
  ProcessStats,
  ProcessListResponse
} from "@/types/process";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export function useProcesses() {
  const { token } = useAuth();
  const [processes, setProcesses] = useState<Process[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Buscar todos os processos
  const fetchProcesses = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/company/processes`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar processos`);
      }

      const data = await response.json();
      // Verificar se é ProcessListResponse ou array direto
      if (data && typeof data === 'object' && 'processes' in data) {
        setProcesses(data.processes || []);
      } else {
        setProcesses(data || []);
      }
    } catch (error) {
      console.error(`Erro ao buscar processos:`, error);
      setError(`Erro ao carregar processos`);
      toast.error(`Erro ao carregar processos`);
    } finally {
      setLoading(false);
    }
  };

  // Criar novo processo
  const createProcess = async (processData: CreateProcessData): Promise<Process | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/processes`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(processData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao criar processo`);
      }

      const newProcess = await response.json();
      setProcesses(prev => [...prev, newProcess]);
      toast.success(`Processo criado com sucesso`);
      return newProcess;
    } catch (error) {
      console.error(`Erro ao criar processo:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao criar processo`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar processo
  const updateProcess = async (processId: string, processData: UpdateProcessData): Promise<Process | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/processes/${processId}`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(processData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao atualizar processo`);
      }

      const updatedProcess = await response.json();
      setProcesses(prev => prev.map(process => 
        process.id === processId ? updatedProcess : process
      ));
      toast.success(`Processo atualizado com sucesso`);
      return updatedProcess;
    } catch (error) {
      console.error(`Erro ao atualizar processo:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao atualizar processo`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Deletar processo
  const deleteProcess = async (processId: string): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/processes/${processId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao deletar processo`);
      }

      setProcesses(prev => prev.filter(process => process.id !== processId));
      toast.success(`Processo deletado com sucesso`);
      return true;
    } catch (error) {
      console.error(`Erro ao deletar processo:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao deletar processo`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Buscar processo específico
  const getProcess = async (processId: string): Promise<Process | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/processes/${processId}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Processo não encontrado`);
      }

      const process = await response.json();
      return process;
    } catch (error) {
      console.error(`Erro ao buscar processo:`, error);
      setError(`Erro ao buscar processo`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Obter estatísticas
  const getProcessStats = async (): Promise<ProcessStats | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/processes/stats/summary`, {
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

  // Filtrar processos
  const filterProcesses = (searchTerm: string) => {
    // Garantir que processes seja sempre um array
    if (!Array.isArray(processes)) {
      console.warn('processes não é um array:', processes);
      return [];
    }
    
    return processes.filter(process =>
      process.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (process.cnj_number && process.cnj_number.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (process.court && process.court.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (process.client?.name && process.client.name.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  };

  // Carregar processos na inicialização
  useEffect(() => {
    if (token) {
      fetchProcesses();
    }
  }, [token]);

  return {
    processes,
    loading,
    error,
    fetchProcesses,
    createProcess,
    updateProcess,
    deleteProcess,
    getProcess,
    getProcessStats,
    filterProcesses,
  };
}
