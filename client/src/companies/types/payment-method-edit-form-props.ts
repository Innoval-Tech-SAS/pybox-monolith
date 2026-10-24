import type { EditPaymentMethodFormState } from "@/companies/hooks/use-edit-payment-method-form";
import type { PaymentMethod } from "@/types/payment-methods/payment-method-types";

export interface PaymentMethodEditFormProps {
  item: PaymentMethod;
  orgId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export interface PaymentMethodEditGeneralProps {
  form: EditPaymentMethodFormState;
  typeOptions: { value: string; label: string }[];
  field: (key: keyof EditPaymentMethodFormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  setType: (type: string) => void;
  toggleActive: () => void;
}

export interface PaymentMethodEditBankProps {
  form: EditPaymentMethodFormState;
  field: (key: keyof EditPaymentMethodFormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
}
