import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SuperAdmin {
  id: string;
  name: string;
  email: string;
  permissions: Record<string, any>;
  is_active: boolean;
}

interface SuperAdminAuthState {
  superAdmin: SuperAdmin | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface SuperAdminAuthStore extends SuperAdminAuthState {
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export const useSuperAdminStore = create<SuperAdminAuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      superAdmin: null,
      token: typeof window !== 'undefined' ? localStorage.getItem('superadmin_token') : null,
      isAuthenticated: typeof window !== 'undefined' ? !!localStorage.getItem('superadmin_token') : false,
      isLoading: false,
      error: null,

      // Actions
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch(`${API_BASE_URL}/auth/superadmin/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro no login');
          }

          const data = await response.json();
          
          // Store token
          localStorage.setItem('superadmin_token', data.access_token);
          
          set({
            superAdmin: {
              id: data.user.id,
              name: data.user.name,
              email: data.user.email,
              permissions: data.user.permissions || {},
              is_active: data.user.is_active,
            },
            token: data.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Erro desconhecido',
          });
        }
      },

      logout: () => {
        // Clear token
        localStorage.removeItem('superadmin_token');
        
        set({
          superAdmin: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'superadmin-storage',
      partialize: (state) => ({
        superAdmin: state.superAdmin,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Selectors
export const useSuperAdmin = () => useSuperAdminStore((state) => state.superAdmin);
export const useSuperAdminToken = () => useSuperAdminStore((state) => state.token);
export const useSuperAdminIsAuthenticated = () => useSuperAdminStore((state) => state.isAuthenticated);
export const useSuperAdminIsLoading = () => useSuperAdminStore((state) => state.isLoading);
export const useSuperAdminError = () => useSuperAdminStore((state) => state.error);
