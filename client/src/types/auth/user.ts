export interface RegisterRequest {
  firstname: string;
  lastname: string;
  email: string;
  password: string;
  phoneNumber: string;
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

export type OrgVerificationStatus = "PENDIENTE" | "APROBADO" | "DENEGADO";

export type IdentityVerificationStatus = "NO_ENVIADO" | "PENDIENTE" | "APROBADO" | "DENEGADO";

export interface OrgSessionEntry {
  role: string;
  orgName: string;
  permissions: string[];
  verificationStatus: OrgVerificationStatus;
  createdAt?: string | null;
}

export interface User {
  // /me response fields (camelCase from API)
  userId?: string;
  fullName?: string;
  email: string;
  role?: string;
  scope?: string;
  documentType?: string;
  documentNumber?: string;
  profilePhotoUrl?: string;
  mfaEnabled?: boolean;
  identityVerificationStatus?: IdentityVerificationStatus;
  orgs?: Record<string, OrgSessionEntry>;

  // legacy fields kept for auth session
  firstname?: string;
  lastname?: string;
  fullname?: string;
  phoneNumber?: string;
  authProvider?: string;
  nationality?: string;
  isActive?: boolean;
  profilePhoto?: string;
  userRole?: string;
  userScope?: string;
}
