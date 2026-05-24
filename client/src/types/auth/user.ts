export interface RegisterRequest {
  firstname: string;
  lastname: string;
  email: string;
  password: string;
  phone_number: string;
  nationality: string;
}

export interface RegisterResponse {
  id: string;
  email: string;
}

export interface RoleAssignment {
  role?: string;
  scope?: string;
}

export type OrgVerificationStatus = "pending" | "approved" | "denied";

export interface OrgSessionEntry {
  role: string;
  org_name: string;
  permissions: string[];
  verification_status: OrgVerificationStatus;
  created_at?: string | null;
}

export interface User {
  // /me response fields (snake_case from API)
  user_id?: number;
  full_name?: string;
  email: string;
  role?: string;
  scope?: string;
  document_type?: string;
  document_number?: string;
  orgs?: Record<string, OrgSessionEntry>;

  // legacy fields kept for auth session
  id?: number;
  firstname?: string;
  lastname?: string;
  fullname?: string;
  phoneNumber?: string;
  authProvider?: string;
  nationality?: string;
  documentType?: string;
  documentNumber?: string;
  isActive?: boolean;
  profilePhoto?: string;
  userRole?: string;
  userScope?: string;
  roles?: RoleAssignment[];
  roleAssignments?: RoleAssignment[];
}
