import type { ProviderCredential } from "@/platform-gateway-credentials/types/provider-credential-types";

export interface CredentialsTableProps {
  items: ProviderCredential[];
  loading: boolean;
  countryLabel: (code: string | null) => string;
  onEdit: (row: ProviderCredential) => void;
  onDelete: (row: ProviderCredential) => void;
}
