export type VerificationChannel = "EMAIL" | "SMS";

export type OnboardingStep = "email" | "phone" | "profile" | "organization";

export interface OnboardingStatus {
  emailVerified: boolean;
  phoneVerified: boolean;
  documentComplete: boolean;
  orgComplete: boolean | null;
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

export interface OrgOnboardingData {
  name: string;
  country: string;
  fiscalDocumentNumber: string;
  fiscalDocumentFile: File;
  mercantileDocumentFile: File;
}
