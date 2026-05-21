export type VerificationChannel = "EMAIL" | "SMS";

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
