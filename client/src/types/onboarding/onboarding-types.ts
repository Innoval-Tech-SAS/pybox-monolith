export type VerificationChannel = "EMAIL" | "SMS";

export type OnboardingStep = "email" | "set_phone" | "phone" | "profile" | "organization" | "identity" | "set_password";

export type IdentityVerificationStatus = "NO_ENVIADO" | "PENDIENTE" | "APROBADO" | "DENEGADO";

export interface OnboardingStatus {
  emailVerified: boolean;
  phoneSet: boolean;
  phoneVerified: boolean;
  documentComplete: boolean;
  orgComplete: boolean | null;
  identityVerificationStatus: IdentityVerificationStatus | null;
  mustChangePassword: boolean;
  isComplete: boolean;
  missingSteps: string[];
}

export interface RequestOtpRequest {
  channel: VerificationChannel;
}

export interface VerifyOtpRequest {
  channel: VerificationChannel;
  code: string;
}

export interface UpdateProfileRequest {
  documentType: string;
  documentNumber: string;
  nationality: string;
}

export type OnboardingRepMode = "self" | "create";

export interface OrgOnboardingData {
  name: string;
  sector: string;
  country: string;
  fiscalDocumentNumber: string;
  fiscalDocumentFile: File;
  mercantileDocumentFile: File;
  representativeMode: OnboardingRepMode;
  representativeDocumentFile: File;
  repFirstname?: string;
  repLastname?: string;
  repEmail?: string;
  repDocType?: string;
  repDocNumber?: string;
  repPassword?: string;
}
