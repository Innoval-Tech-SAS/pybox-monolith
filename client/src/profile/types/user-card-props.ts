import type { IdentityVerificationStatus, OrgSessionEntry } from "@/types/auth/user";
import type { RoleEntry } from "@/types/users/user-types";

export interface UserCardData {
  userId?: string;
  fullName: string;
  firstname?: string;
  lastname?: string;
  email: string;
  phoneNumber?: string | null;
  authProvider?: string;
  documentType?: string | null;
  documentNumber?: string | null;
  profilePhotoUrl?: string | null;
  role?: string;
  scope?: string;
  isActive?: boolean;
  isEmailVerified?: boolean;
  isPhoneVerified?: boolean;
  mfaEnabled?: boolean;
  identityVerificationStatus?: IdentityVerificationStatus;
  isActiveSessions?: boolean;
  createdAt?: string | null;
  updatedAt?: string | null;
  roles?: RoleEntry[];
  orgs?: Record<string, OrgSessionEntry>;
}

export interface UserCardProps {
  data: UserCardData;
  isOwnProfile?: boolean;
  editPath?: string;
  onForceLogout?: () => void;
}
