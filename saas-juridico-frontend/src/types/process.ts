export interface Process {
  id: string;
  tenant_id: string;
  cnj_number?: string;
  court?: string;
  jurisdiction?: string;
  subject: string;
  status: string; // active, closed, suspended
  client_id: string;
  specialty_id?: string;
  priority: string; // low, normal, high, urgent
  estimated_value?: number;
  notes?: string;
  is_confidential: boolean;
  requires_attention: boolean;
  created_at: string;
  updated_at?: string;
  created_by?: string;
  
  // Relacionamentos
  client?: Client;
  specialty?: Specialty;
  lawyers?: ProcessLawyer[];
}

export interface ProcessLawyer {
  id: string;
  process_id: string;
  lawyer_id: string;
  role: string; // lawyer, assistant, coordinator
  is_primary: boolean;
  can_sign_documents: boolean;
  can_manage_process: boolean;
  can_view_financial: boolean;
  created_at: string;
  updated_at?: string;
  assigned_by?: string;
  
  // Relacionamento
  lawyer?: User;
}

export interface CreateProcessData {
  subject: string;
  cnj_number?: string;
  court?: string;
  jurisdiction?: string;
  client_id: string;
  specialty_id?: string;
  priority?: string;
  estimated_value?: number;
  notes?: string;
  is_confidential?: boolean;
  requires_attention?: boolean;
  lawyers: CreateProcessLawyerData[];
}

export interface CreateProcessLawyerData {
  lawyer_id: string;
  role?: string;
  is_primary?: boolean;
  can_sign_documents?: boolean;
  can_manage_process?: boolean;
  can_view_financial?: boolean;
}

export interface UpdateProcessData extends Partial<CreateProcessData> {
  status?: string;
}

export interface ProcessStats {
  total_processes: number;
  active_processes: number;
  closed_processes: number;
  suspended_processes: number;
  high_priority_processes: number;
  urgent_processes: number;
}

export interface ProcessListResponse {
  processes: Process[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Tipos auxiliares
interface Client {
  id: string;
  name: string;
  email?: string;
  person_type: string;
}

interface Specialty {
  id: string;
  name: string;
  code: string;
}

interface User {
  id: string;
  name: string;
  email: string;
}
