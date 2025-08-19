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
  urgent_processes: number;
  completion_rate?: number;
}

export interface ProcessListResponse {
  processes: Process[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Timeline
export interface ProcessTimelineEvent {
  id: string;
  type: 'petition' | 'decision' | 'publication' | 'hearing' | 'other';
  title: string;
  description?: string;
  occurred_at: string;
  created_at?: string;
  metadata?: Record<string, any>;
}

// Prazos
export interface ProcessDeadline {
  id: string;
  title: string;
  due_date: string;
  status: 'open' | 'delivered' | 'overdue';
  assigned_to?: User;
  created_at?: string;
  completed_at?: string;
  notes?: string;
}

// Notas do processo
export interface ProcessNote {
  id: string;
  content: string;
  created_by: User;
  created_at: string;
  updated_at?: string;
  mentions?: string[]; // IDs de usuários mencionados
}

// Documentos do processo
export interface ProcessDocument {
  id: string;
  title: string;
  description?: string;
  file_url: string;
  file_size: number;
  mime_type: string;
  tags: string[];
  created_by: User;
  created_at: string;
  updated_at?: string;
  version: number;
  is_signed?: boolean;
}

// Tarefas do processo
export interface ProcessTask {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  assigned_to?: User;
  due_date?: string;
  completed_at?: string;
  created_by: User;
  created_at: string;
  updated_at?: string;
}

// Partes do processo
export interface ProcessParty {
  id: string;
  name: string;
  type: 'plaintiff' | 'defendant' | 'third_party';
  person_type: 'PF' | 'PJ';
  cpf_cnpj?: string;
  email?: string;
  phone?: string;
  address?: Record<string, any>;
  representatives?: ProcessPartyRepresentative[];
  created_at: string;
  updated_at?: string;
}

export interface ProcessPartyRepresentative {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  relationship: string; // Representante legal, Procurador, etc.
}

// Financeiro do processo
export interface ProcessFinancial {
  id: string;
  type: 'fee' | 'expense' | 'payment' | 'refund';
  title: string;
  description?: string;
  amount: number; // Em centavos
  due_date?: string;
  paid_date?: string;
  status: 'pending' | 'paid' | 'overdue' | 'cancelled';
  category?: string;
  receipt_url?: string;
  created_by: User;
  created_at: string;
  updated_at?: string;
}

// Auditoria do processo
export interface ProcessAuditEvent {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  performed_by: User;
  performed_at: string;
  ip_address?: string;
  user_agent?: string;
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
