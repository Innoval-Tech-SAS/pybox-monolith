export interface PaymentMethod {
  id: string;
  organizationId: string;
  name: string;
  type: string;
  description: string | null;
  instructions: string | null;
  bankName: string | null;
  accountType: string | null;
  accountNumber: string | null;
  paymentLink: string | null;
  qrImageUrl: string | null;
  isActive: boolean;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface PaymentMethodCreatePayload {
  organizationId: string;
  name: string;
  type: string;
  description?: string | null;
  instructions?: string | null;
  bankName?: string | null;
  accountType?: string | null;
  accountNumber?: string | null;
  paymentLink?: string | null;
  qrImageUrl?: string | null;
}

export interface PaymentMethodUpdatePayload {
  name?: string;
  type?: string;
  description?: string | null;
  instructions?: string | null;
  bankName?: string | null;
  accountType?: string | null;
  accountNumber?: string | null;
  paymentLink?: string | null;
  qrImageUrl?: string | null;
  isActive?: boolean;
}
