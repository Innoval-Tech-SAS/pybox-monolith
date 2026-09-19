import type { ReactNode } from "react";
import type {
  OnboardingStatus,
  VerificationChannel,
} from "@/types/onboarding/onboarding-types";

export interface VerifyChannelStepProps {
  title: string;
  description: string;
  defaultChannel: VerificationChannel;
  onDone: () => void;
  requestOtp: (channel: VerificationChannel) => Promise<void>;
  verifyOtp: (channel: VerificationChannel, code: string) => Promise<void>;
  loading: boolean;
  error: string | null;
  clearError: () => void;
}

export interface StepDoneProps {
  onDone: () => void;
}

export interface OnboardingModalProps {
  isOpen: boolean;
  status: OnboardingStatus;
  onComplete: () => void;
}

export interface OnboardingGuardProps {
  children: ReactNode;
}
