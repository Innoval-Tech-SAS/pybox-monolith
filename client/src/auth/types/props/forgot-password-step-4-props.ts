import type { Channel } from "@/auth/hooks/use-forgot-password";

export interface ForgotPasswordStep4Props {
  docType: string;
  docNumber: string;
  code: string;
  channel: Channel;
  onSuccess: () => void;
  loading: boolean;
}
