import type { PaymentGatewayFieldSpec, PaymentGatewayProvider } from "@/companies/types/payment-gateway-credential-types";

// Campos por pasarela, documentados en la skill `wompi-gateway` (Bold/PayU/ePayco
// quedan con el set mínimo hasta que se investigue cada una con el mismo detalle).
export const PAYMENT_GATEWAY_FIELD_SPECS: Record<PaymentGatewayProvider, PaymentGatewayFieldSpec> = {
  WOMPI: {
    label: "Wompi",
    secretKeys: ["private_key", "events_key", "integrity_key"],
    publicKeys: ["public_key"],
  },
  BOLD: {
    label: "Bold",
    secretKeys: ["identity_key", "secret_key"],
    publicKeys: [],
  },
  PAYU: {
    label: "PayU",
    secretKeys: ["api_key", "api_login"],
    publicKeys: ["merchant_id"],
  },
  EPAYCO: {
    label: "ePayco",
    secretKeys: ["p_key"],
    publicKeys: ["p_cust_id_cliente", "public_key"],
  },
};

export const PAYMENT_GATEWAY_OPTIONS = Object.entries(PAYMENT_GATEWAY_FIELD_SPECS).map(
  ([value, spec]) => ({ value: value as PaymentGatewayProvider, label: spec.label }),
);
