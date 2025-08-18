import { useState } from "react";
import { useAuth } from "./useAuth";
import { toast } from "sonner";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export interface CNJValidationResult {
  valid: boolean;
  tribunal?: {
    alias: string;
    nome: string;
  };
  componentes?: {
    sequencial: string;
    dv: string;
    ano: string;
    justica: string;
    tribunal: string;
    vara: string;
  };
  numero_formatado?: string;
  error?: string;
}

export interface CNJData {
  numero_processo: string;
  classe_processual: string;
  assunto: string;
  data_distribuicao: string;
  orgao_julgador: string;
  tribunal: string;
  vara: string;
  valor_causa: string;
  partes: any[];
  andamentos: any[];
  documentos: any[];
  status: string;
  ultima_atualizacao: string;
}

export function useCNJIntegration() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Validar número CNJ
  const validateCNJ = async (cnjNumber: string): Promise<CNJValidationResult | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/processes/cnj/validar-cnj/${cnjNumber}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao validar CNJ`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error("Erro ao validar CNJ:", error);
      const errorMessage = error instanceof Error ? error.message : "Erro ao validar CNJ";
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Consultar processo na API CNJ
  const consultarProcesso = async (cnjNumber: string): Promise<CNJData | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/processes/cnj/consultar/${cnjNumber}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao consultar processo`);
      }

      const result = await response.json();
      
      if (result.success) {
        return result.data;
      } else {
        throw new Error(result.detail || "Processo não encontrado");
      }
    } catch (error) {
      console.error("Erro ao consultar processo:", error);
      const errorMessage = error instanceof Error ? error.message : "Erro ao consultar processo";
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Importar processo do CNJ
  const importarProcesso = async (cnjNumber: string): Promise<string | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/processes/cnj/importar/${cnjNumber}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao importar processo`);
      }

      const result = await response.json();
      
      if (result.success) {
        toast.success("Processo importado com sucesso!");
        return result.process_id;
      } else {
        throw new Error(result.detail || "Erro ao importar processo");
      }
    } catch (error) {
      console.error("Erro ao importar processo:", error);
      const errorMessage = error instanceof Error ? error.message : "Erro ao importar processo";
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Sincronizar processo existente
  const sincronizarProcesso = async (processId: string): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/processes/cnj/sincronizar/${processId}`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao sincronizar processo`);
      }

      const result = await response.json();
      
      if (result.success) {
        toast.success("Sincronização iniciada com sucesso!");
        return true;
      } else {
        throw new Error(result.detail || "Erro ao sincronizar processo");
      }
    } catch (error) {
      console.error("Erro ao sincronizar processo:", error);
      const errorMessage = error instanceof Error ? error.message : "Erro ao sincronizar processo";
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Verificar status do processo
  const verificarStatus = async (cnjNumber: string): Promise<any> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/processes/cnj/status/${cnjNumber}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao verificar status`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error("Erro ao verificar status:", error);
      const errorMessage = error instanceof Error ? error.message : "Erro ao verificar status";
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    validateCNJ,
    consultarProcesso,
    importarProcesso,
    sincronizarProcesso,
    verificarStatus,
  };
}
