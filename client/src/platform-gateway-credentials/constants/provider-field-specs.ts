import { CredentialProvider, ProviderFieldSpec } from "../types/provider-credential-types";

export const PROVIDER_FIELD_SPECS: Record<CredentialProvider, ProviderFieldSpec> = {
  MERCADOPAGO: {
    label: "Mercado Pago",
    secretKeys: ["access_token", "webhook_secret"],
    publicKeys: ["public_key", "application_id"],
    lookupFrom: "application_id",
  },
  BOLD: {
    label: "Bold",
    secretKeys: ["api_key"],
    publicKeys: [],
  },
};

export const PROVIDER_OPTIONS = Object.entries(PROVIDER_FIELD_SPECS).map(
  ([value, spec]) => ({ value: value as CredentialProvider, label: spec.label }),
);
