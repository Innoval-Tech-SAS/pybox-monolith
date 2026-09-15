import type { useRegisterOrg } from "@/companies/hooks/use-register-org";
import type { useCountries } from "@/hooks/use-countries";

export interface StepCompanyInfoProps {
  form: ReturnType<typeof useRegisterOrg>;
  countriesData: ReturnType<typeof useCountries>;
  fiscalLabel: string;
  canGoNext: boolean;
  onNext: () => void;
  onCancel: () => void;
}
