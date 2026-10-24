export type PaymentGatewayProvider = "WOMPI" | "BOLD" | "PAYU" | "EPAYCO";

export interface PaymentGatewayCredential {
  id: string;
  organizationId: string;
  provider: PaymentGatewayProvider;
  publicConfig: Record<string, string>;
  secretKeys: string[];
  lookupKey: string | null;
  isActive: boolean;
  createdAt: string;
  updatedAt: string | null;
}

export interface PaymentGatewayCredentialCreatePayload {
  provider: PaymentGatewayProvider;
  secrets: Record<string, string>;
  publicConfig: Record<string, string>;
  lookupKey: string | null;
  isActive: boolean;
}

export interface PaymentGatewayCredentialUpdatePayload {
  secrets: Record<string, string>;
  publicConfig?: Record<string, string>;
  lookupKey?: string | null;
  isActive?: boolean;
}

/** Descripción de los campos esperados por pasarela, para armar el formulario. Ver
 * skill `wompi-gateway` para el detalle de qué representa cada llave. */
export interface PaymentGatewayFieldSpec {
  label: string;
  secretKeys: string[];
  publicKeys: string[];
}
