export interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  oab_number?: string;
  oab_state?: string;
  position?: string;
  department?: string;
  is_active: boolean;
  is_super_admin: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  preferences: Record<string, unknown>;
  timezone: string;
  language: string;
  last_login?: string;
  created_at: string;
  updated_at?: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  cnpj?: string;
  email: string;
  phone?: string;
  address?: Record<string, unknown>;
  plan_type: string;
  plan_features: Record<string, unknown>;
  max_users: number;
  max_processes: number;
  is_active: boolean;
  is_suspended: boolean;
  trial_ends_at?: string;
  subscription_ends_at?: string;
  settings: Record<string, unknown>;
  branding: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
}

export interface TenantUser {
  id: string;
  tenant_id: string;
  user_id: string;
  role: string;
  permissions: Record<string, unknown>;
  department?: string;
  position?: string;
  is_active: boolean;
  is_primary_admin: boolean;
  created_at: string;
  updated_at?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  tenant_slug?: string;
}

export interface AuthResponse {
  user: User;
  tenant?: Tenant;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthState {
  user: User | null;
  tenant: Tenant | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
