import type { PaymentMethodFormState } from "@/companies/hooks/use-payment-method-form";

export interface PaymentMethodFormProps {
  orgId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export interface PaymentMethodStepGeneralProps {
  form: PaymentMethodFormState;
  typeOptions: { value: string; label: string }[];
  field: (key: keyof PaymentMethodFormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  setType: (type: string) => void;
}

export interface PaymentMethodStepBankProps {
  form: PaymentMethodFormState;
  field: (key: keyof PaymentMethodFormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
}

export interface PaymentMethodStepSummaryProps {
  form: PaymentMethodFormState;
  typeLabel: string;
}
