export interface Specialty {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  code?: string;
  is_active: boolean;
  color?: string;
  icon?: string;
  display_order: string;
  requires_oab: boolean;
  min_experience_years?: string;
  created_at: string;
  updated_at?: string;
}

export interface CreateSpecialtyData {
  name: string;
  description?: string;
  code?: string;
  color?: string;
  icon?: string;
  display_order?: string;
  requires_oab?: boolean;
  min_experience_years?: string;
}

export interface UpdateSpecialtyData extends Partial<CreateSpecialtyData> {
  is_active?: boolean;
}

export interface SpecialtyStats {
  total_specialties: number;
  active_specialties: number;
  inactive_specialties: number;
  specialties_with_oab_requirement: number;
  specialties_with_experience_requirement: number;
}

export interface SpecialtyListResponse {
  specialties: Specialty[];
  total: number;
  active_count: number;
  inactive_count: number;
}
