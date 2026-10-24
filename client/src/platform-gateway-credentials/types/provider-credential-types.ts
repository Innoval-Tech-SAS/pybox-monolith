export type CredentialProvider = "MERCADOPAGO" | "BOLD";

export interface ProviderCredential {
  id: string;
  countryCode: string | null;
  provider: CredentialProvider;
  publicConfig: Record<string, string>;
  secretKeys: string[];
  lookupKey: string | null;
  isActive: boolean;
  createdAt: string;
  updatedAt: string | null;
}

export interface ProviderCredentialUpsert {
  countryCode: string | null;
  provider: CredentialProvider;
  secrets: Record<string, string>;
  publicConfig: Record<string, string>;
  lookupKey: string | null;
  isActive: boolean;
}

/** Descripción de los campos esperados por proveedor, para armar el formulario. */
export interface ProviderFieldSpec {
  label: string;
  /** Claves secretas (se cifran; write-only). */
  secretKeys: string[];
  /** Claves no secretas (se muestran en claro). */
  publicKeys: string[];
  /** Si aplica, qué clave pública alimenta el lookup_key (p. ej. application_id de MP). */
  lookupFrom?: string;
}
