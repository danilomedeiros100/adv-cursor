import { create } from 'zustand';
import { fetchWithAuth } from '@/lib/api';

interface User {
  id: string;
  name: string;
  email: string;
  is_super_admin?: boolean;
}

interface Tenant {
  id: string;
  name: string;
  slug: string;
}

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
  tenant?: Tenant;
}

interface LoginCredentials {
  email: string;
  password: string;
  tenant_slug?: string;
}

interface AuthState {
  user: User | null;
  tenant: Tenant | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  isInitialized: boolean;

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  checkAuthStatus: () => Promise<void>;
  getToken: () => string | null;
  clearError: () => void;
}



export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  tenant: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  isInitialized: false,

  login: async (credentials: LoginCredentials) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await fetchWithAuth('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro no login');
      }

      const data: AuthResponse = await response.json();
      
      // Store tokens
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
      }
      
      set({
        user: data.user,
        tenant: data.tenant || null,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        isInitialized: true,
      });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
      });
      throw error;
    }
  },

  logout: () => {
    // Clear tokens
    if (typeof window !== 'undefined') {
      try {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      } catch (error) {
        console.log('Erro ao limpar tokens:', error);
      }
    }
    
    set({
      user: null,
      tenant: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      isInitialized: true,
    });
  },

  checkAuthStatus: async () => {
    // Evita múltiplas chamadas simultâneas
    const state = get();
    if (state.isLoading || typeof window === 'undefined') {
      return;
    }
    
    set({ isLoading: true });
    
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        // Se não há token, limpa o estado
        set({
          user: null,
          tenant: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
          isInitialized: true,
        });
        return;
      }

      // Verifica se o token é válido
      const response = await fetchWithAuth('/auth/me');

      if (!response.ok) {
        // Token inválido, limpa o estado
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({
          user: null,
          tenant: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
          isInitialized: true,
        });
        return;
      }

      // Token válido, carrega dados do usuário
      const userData = await response.json();
      set({
        user: userData.user,
        tenant: userData.tenant || null,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        isInitialized: true,
      });
    } catch (error) {
      set({
        user: null,
        tenant: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        isInitialized: true,
      });
    }
  },

  getToken: () => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  },

  clearError: () => {
    set({ error: null });
  },
}));



