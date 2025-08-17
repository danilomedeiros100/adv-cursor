import { useState, useEffect } from "react";
import { useAuth } from "./useAuth";
import { toast } from "sonner";
import { 
  Specialty, 
  CreateSpecialtyData, 
  UpdateSpecialtyData, 
  SpecialtyStats 
} from "@/types/specialty";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export function useSpecialties() {
  const { token } = useAuth();
  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Buscar todas as especialidades (ativas e inativas)
  const fetchSpecialties = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/company/specialties`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar especialidades`);
      }

      const data = await response.json();
      setSpecialties(data || []);
    } catch (error) {
      console.error(`Erro ao buscar especialidades:`, error);
      setError(`Erro ao carregar especialidades`);
      toast.error(`Erro ao carregar especialidades`);
    } finally {
      setLoading(false);
    }
  };

  // Buscar apenas especialidades ativas
  const fetchActiveSpecialties = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/company/specialties?is_active=true`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar especialidades`);
      }

      const data = await response.json();
      setSpecialties(data || []);
    } catch (error) {
      console.error(`Erro ao buscar especialidades:`, error);
      setError(`Erro ao carregar especialidades`);
      toast.error(`Erro ao carregar especialidades`);
    } finally {
      setLoading(false);
    }
  };

  // Criar nova especialidade
  const createSpecialty = async (specialtyData: CreateSpecialtyData): Promise<Specialty | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/specialties`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(specialtyData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao criar especialidade`);
      }

      const newSpecialty = await response.json();
      setSpecialties(prev => [...prev, newSpecialty]);
      toast.success(`Especialidade criada com sucesso`);
      return newSpecialty;
    } catch (error) {
      console.error(`Erro ao criar especialidade:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao criar especialidade`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar especialidade
  const updateSpecialty = async (specialtyId: string, specialtyData: UpdateSpecialtyData): Promise<Specialty | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/specialties/${specialtyId}`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(specialtyData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao atualizar especialidade`);
      }

      const updatedSpecialty = await response.json();
      setSpecialties(prev => prev.map(specialty => 
        specialty.id === specialtyId ? updatedSpecialty : specialty
      ));
      toast.success(`Especialidade atualizada com sucesso`);
      return updatedSpecialty;
    } catch (error) {
      console.error(`Erro ao atualizar especialidade:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao atualizar especialidade`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Deletar especialidade
  const deleteSpecialty = async (specialtyId: string): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/specialties/${specialtyId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao deletar especialidade`);
      }

      setSpecialties(prev => prev.filter(specialty => specialty.id !== specialtyId));
      toast.success(`Especialidade deletada com sucesso`);
      return true;
    } catch (error) {
      console.error(`Erro ao deletar especialidade:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao deletar especialidade`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Reativar especialidade
  const activateSpecialty = async (specialtyId: string): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/specialties/${specialtyId}/activate`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao reativar especialidade`);
      }

      // Atualizar o status na lista
      setSpecialties(prev => prev.map(specialty => 
        specialty.id === specialtyId ? { ...specialty, is_active: true } : specialty
      ));
      toast.success(`Especialidade reativada com sucesso`);
      return true;
    } catch (error) {
      console.error(`Erro ao reativar especialidade:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao reativar especialidade`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Buscar especialidade específica
  const getSpecialty = async (specialtyId: string): Promise<Specialty | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/specialties/${specialtyId}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Especialidade não encontrada`);
      }

      const specialty = await response.json();
      return specialty;
    } catch (error) {
      console.error(`Erro ao buscar especialidade:`, error);
      setError(`Erro ao buscar especialidade`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Obter estatísticas
  const getSpecialtyStats = async (): Promise<SpecialtyStats | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/specialties/stats/summary`, {
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

  // Filtrar especialidades
  const filterSpecialties = (searchTerm: string) => {
    return specialties.filter(specialty =>
      specialty.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (specialty.description && specialty.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (specialty.code && specialty.code.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  };

  // Carregar especialidades na inicialização
  useEffect(() => {
    if (token) {
      fetchSpecialties();
    }
  }, [token]);

  return {
    specialties,
    loading,
    error,
    fetchSpecialties,
    fetchActiveSpecialties,
    createSpecialty,
    updateSpecialty,
    deleteSpecialty,
    activateSpecialty,
    getSpecialty,
    getSpecialtyStats,
    filterSpecialties,
  };
}
