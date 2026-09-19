import type { LookupResult } from "@/auth/hooks/use-forgot-password";

export interface ForgotPasswordStep1Props {
  onNext: (docType: string, docNumber: string, result: LookupResult) => void;
  loading: boolean;
}
