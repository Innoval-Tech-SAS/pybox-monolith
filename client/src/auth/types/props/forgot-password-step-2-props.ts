import type { Channel, LookupResult } from "@/auth/hooks/use-forgot-password";

export interface ForgotPasswordStep2Props {
  lookup: LookupResult;
  docType: string;
  docNumber: string;
  onNext: (channel: Channel) => void;
  loading: boolean;
}
