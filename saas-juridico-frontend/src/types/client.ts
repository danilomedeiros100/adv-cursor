export interface Client {
  id: string;
  tenant_id: string;
  name: string;
  email?: string;
  phone?: string;
  cpf_cnpj?: string;
  person_type: string; // "PF" | "PJ"
  address?: any;
  birth_date?: string;
  occupation?: string;
  company_name?: string;
  company_role?: string;
  is_active: boolean;
  is_vip: boolean;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface CreateClientData {
  name: string;
  email?: string;
  phone?: string;
  cpf_cnpj?: string;
  person_type: string;
  address?: any;
  birth_date?: string;
  occupation?: string;
  company_name?: string;
  company_role?: string;
  is_vip?: boolean;
  notes?: string;
}

export interface UpdateClientData extends Partial<CreateClientData> {
  is_active?: boolean;
}

export interface ClientStats {
  total_clients: number;
  active_clients: number;
  inactive_clients: number;
  pf_clients: number;
  pj_clients: number;
  vip_clients: number;
}

export interface ClientListResponse {
  clients: Client[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
