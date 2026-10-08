// Tipado minimo del SDK MercadoPago.js v2 (Secure Fields), no hay @types oficial instalado.

export interface IdentificationType {
  id: string;
  name: string;
}

export interface MercadoPagoSecureField {
  on: (event: string, handler: (data: { bin?: string }) => void) => void;
  unmount: () => void;
}

export interface MercadoPagoInstance {
  fields: {
    create: (field: string, options: Record<string, unknown>) => { mount: (id: string) => MercadoPagoSecureField };
    createCardToken: (data: {
      cardholderName: string;
      identificationType?: string;
      identificationNumber?: string;
    }) => Promise<{ id: string }>;
  };
  getIdentificationTypes: () => Promise<IdentificationType[]>;
  getPaymentMethods: (data: { bin: string }) => Promise<{
    results: Array<{ id: string; payment_type_id: string }>;
  }>;
}

declare global {
  interface Window {
    MercadoPago?: new (publicKey: string) => MercadoPagoInstance;
  }
}
