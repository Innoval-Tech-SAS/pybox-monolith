import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { PaymentMethodCreatePayload } from "@/types/payment-methods/payment-method-types";

export const PAYMENT_METHOD_STEPS = ["Información general", "Datos bancarios / digitales", "Resumen"];

export interface PaymentMethodFormState {
  name: string;
  type: string;
  description: string;
  instructions: string;
  bankName: string;
  accountType: string;
  accountNumber: string;
  paymentLink: string;
  qrImageUrl: string;
}

const EMPTY_FORM: PaymentMethodFormState = {
  name: "",
  type: "",
  description: "",
  instructions: "",
  bankName: "",
  accountType: "",
  accountNumber: "",
  paymentLink: "",
  qrImageUrl: "",
};

export const usePaymentMethodForm = (orgId: string, onSuccess: () => void) => {
  const { apiClient } = useApiClient();

  const [form, setForm] = useState<PaymentMethodFormState>(EMPTY_FORM);
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);

  const isLastStep = step === PAYMENT_METHOD_STEPS.length - 1;
  const canNext = step !== 0 || (!!form.name.trim() && !!form.type);

  const field =
    (key: keyof PaymentMethodFormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((p) => ({ ...p, [key]: e.target.value }));

  const setType = (type: string) => setForm((p) => ({ ...p, type }));

  const nextStep = () => {
    if (!canNext) return;
    setStep((current) => Math.min(current + 1, PAYMENT_METHOD_STEPS.length - 1));
  };

  const prevStep = () => setStep((current) => Math.max(current - 1, 0));

  const submit = async () => {
    if (!isLastStep) {
      nextStep();
      return;
    }
    if (!form.name.trim() || !form.type) return;
    setSaving(true);
    const nullable = (v: string) => v.trim() || null;
    const payload: PaymentMethodCreatePayload = {
      organizationId: orgId,
      name: form.name.trim(),
      type: form.type,
      description: nullable(form.description),
      instructions: nullable(form.instructions),
      bankName: nullable(form.bankName),
      accountType: nullable(form.accountType),
      accountNumber: nullable(form.accountNumber),
      paymentLink: nullable(form.paymentLink),
      qrImageUrl: nullable(form.qrImageUrl),
    };
    try {
      await apiClient("/payment-methods/", { method: "POST", body: JSON.stringify(payload) });
      onSuccess();
    } finally {
      setSaving(false);
    }
  };

  return {
    form,
    step,
    saving,
    isLastStep,
    canNext,
    field,
    setType,
    nextStep,
    prevStep,
    submit,
  };
};
