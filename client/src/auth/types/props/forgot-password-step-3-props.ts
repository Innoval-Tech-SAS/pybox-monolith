import type { Channel } from "@/auth/hooks/use-forgot-password";

export interface ForgotPasswordStep3Props {
  docType: string;
  docNumber: string;
  channel: Channel;
  onNext: (code: string) => void;
  loading: boolean;
}
