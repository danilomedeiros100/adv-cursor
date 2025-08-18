import { useState, useEffect } from "react";
import { useAuth } from "./useAuth";
import { toast } from "sonner";
import { 
  User, 
  CreateUserData, 
  UpdateUserData, 
  UserStats,
  UserSpecialty,
  CreateUserSpecialtyData
} from "@/types/user";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export function useUsers() {
  const { token } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Buscar todos os usuários (apenas ativos por padrão)
  const fetchUsers = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/company/users?is_active=true`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar usuários`);
      }

      const data = await response.json();
      setUsers(data || []);
    } catch (error) {
      console.error(`Erro ao buscar usuários:`, error);
      setError(`Erro ao carregar usuários`);
      toast.error(`Erro ao carregar usuários`);
    } finally {
      setLoading(false);
    }
  };

  // Criar novo usuário
  const createUser = async (userData: CreateUserData): Promise<User | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/users`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao criar usuário`);
      }

      const newUser = await response.json();
      setUsers(prev => [...prev, newUser]);
      toast.success(`Usuário criado com sucesso`);
      return newUser;
    } catch (error) {
      console.error(`Erro ao criar usuário:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao criar usuário`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar usuário
  const updateUser = async (userId: string, userData: UpdateUserData): Promise<User | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/users/${userId}`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao atualizar usuário`);
      }

      const updatedUser = await response.json();
      setUsers(prev => prev.map(user => 
        user.id === userId ? updatedUser : user
      ));
      toast.success(`Usuário atualizado com sucesso`);
      return updatedUser;
    } catch (error) {
      console.error(`Erro ao atualizar usuário:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao atualizar usuário`;
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Deletar usuário
  const deleteUser = async (userId: string): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/users/${userId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao deletar usuário`);
      }

      setUsers(prev => prev.filter(user => user.id !== userId));
      toast.success(`Usuário deletado com sucesso`);
      return true;
    } catch (error) {
      console.error(`Erro ao deletar usuário:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao deletar usuário`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Reativar usuário
  const activateUser = async (userId: string): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/users/${userId}/activate`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao reativar usuário`);
      }

      // Atualizar o status na lista
      setUsers(prev => prev.map(user => 
        user.id === userId ? { ...user, is_active: true } : user
      ));
      toast.success(`Usuário reativado com sucesso`);
      return true;
    } catch (error) {
      console.error(`Erro ao reativar usuário:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao reativar usuário`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Buscar usuário específico
  const getUser = async (userId: string): Promise<User | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/users/${userId}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Usuário não encontrado`);
      }

      const user = await response.json();
      return user;
    } catch (error) {
      console.error(`Erro ao buscar usuário:`, error);
      setError(`Erro ao buscar usuário`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Obter estatísticas
  const getUserStats = async (): Promise<UserStats | null> => {
    if (!token) return null;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/users/stats/summary`, {
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

  // Adicionar especialidade ao usuário
  const addUserSpecialty = async (userId: string, specialtyData: CreateUserSpecialtyData): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/users/${userId}/specialties`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(specialtyData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao adicionar especialidade`);
      }

      toast.success(`Especialidade adicionada com sucesso`);
      return true;
    } catch (error) {
      console.error(`Erro ao adicionar especialidade:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao adicionar especialidade`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Listar especialidades do usuário
  const getUserSpecialties = async (userId: string): Promise<UserSpecialty[]> => {
    if (!token) return [];

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/users/${userId}/specialties`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Erro ao buscar especialidades do usuário`);
      }

      const data = await response.json();
      return data.specialties || [];
    } catch (error) {
      console.error(`Erro ao buscar especialidades do usuário:`, error);
      setError(`Erro ao buscar especialidades do usuário`);
      return [];
    } finally {
      setLoading(false);
    }
  };

  // Remover especialidade do usuário
  const removeUserSpecialty = async (userId: string, specialtyId: string): Promise<boolean> => {
    if (!token) return false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/company/users/${userId}/specialties/${specialtyId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro ao remover especialidade`);
      }

      toast.success(`Especialidade removida com sucesso`);
      return true;
    } catch (error) {
      console.error(`Erro ao remover especialidade:`, error);
      const errorMessage = error instanceof Error ? error.message : `Erro ao remover especialidade`;
      setError(errorMessage);
      toast.error(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Filtrar usuários
  const filterUsers = (searchTerm: string) => {
    return users.filter(user =>
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (user.cpf && user.cpf.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (user.oab_number && user.oab_number.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  };

  // Carregar usuários na inicialização
  useEffect(() => {
    if (token) {
      fetchUsers();
    }
  }, [token]);

  return {
    users,
    loading,
    error,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    activateUser,
    getUser,
    getUserStats,
    addUserSpecialty,
    getUserSpecialties,
    removeUserSpecialty,
    filterUsers,
  };
}
