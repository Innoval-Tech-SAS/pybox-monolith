import type { useRegisterOrg } from "@/companies/hooks/use-register-org";

export interface StepRepresentativeProps {
  form: ReturnType<typeof useRegisterOrg>;
  repDocTypes: string[];
  canSubmit: boolean;
  onBack: () => void;
}
