export interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  birth_date?: string;
  cpf?: string;
  oab_number?: string;
  oab_state?: string;
  position?: string;
  department?: string;
  is_active: boolean;
  is_super_admin: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  preferences: any;
  timezone: string;
  language: string;
  last_login?: string;
  created_at: string;
  updated_at?: string;
  role?: string;
  tenant_permissions?: any;
}

export interface CreateUserData {
  name: string;
  email: string;
  password: string;
  phone?: string;
  birth_date?: string;
  cpf?: string;
  oab_number?: string;
  oab_state?: string;
  position?: string;
  department?: string;
  role: string;
  is_active?: boolean;
  preferences?: any;
  timezone?: string;
  language?: string;
}

export interface UpdateUserData extends Partial<CreateUserData> {
  is_active?: boolean;
}

export interface UserPasswordUpdate {
  current_password: string;
  new_password: string;
}

export interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  role_counts: {
    admin: number;
    lawyer: number;
    assistant: number;
    secretary: number;
    receptionist: number;
    user: number;
  };
  lawyers_with_oab: number;
}

export interface UserSpecialty {
  id: string;
  specialty_id: string;
  specialty_name: string;
  expertise_level: string;
  years_experience?: number;
  certifications: any[];
  created_at: string;
}

export interface CreateUserSpecialtyData {
  specialty_id: string;
  expertise_level?: string;
  years_experience?: number;
}

export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
