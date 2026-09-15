import type { useRegisterOrg } from "@/companies/hooks/use-register-org";

export interface StepDocumentsProps {
  form: ReturnType<typeof useRegisterOrg>;
  fiscalLabel: string;
  mercantileLabel: string;
  canGoNext: boolean;
  onNext: () => void;
  onBack: () => void;
}
