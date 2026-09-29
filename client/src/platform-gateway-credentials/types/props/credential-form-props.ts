import type { NationalityOption } from "@/types/countries/country-types";
import type { CredentialProvider, ProviderFieldSpec } from "@/platform-gateway-credentials/types/provider-credential-types";

export interface CredentialFormProps {
  editingId: string | null;
  provider: CredentialProvider;
  onChangeProvider: (value: CredentialProvider) => void;
  countryValue: string;
  onChangeCountry: (value: string) => void;
  countries: NationalityOption[];
  spec: ProviderFieldSpec;
  secrets: Record<string, string>;
  onChangeSecret: (key: string, value: string) => void;
  publicConfig: Record<string, string>;
  onChangePublicConfig: (key: string, value: string) => void;
  isActive: boolean;
  onChangeIsActive: (value: boolean) => void;
  saving: boolean;
  onSave: () => void;
  onCancelEdit: () => void;
}
