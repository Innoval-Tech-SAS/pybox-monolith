import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { PaymentMethod, PaymentMethodUpdatePayload } from "@/types/payment-methods/payment-method-types";

export interface EditPaymentMethodFormState {
  name: string;
  type: string;
  description: string;
  instructions: string;
  bankName: string;
  accountType: string;
  accountNumber: string;
  paymentLink: string;
  qrImageUrl: string;
  isActive: boolean;
}

const EMPTY_FORM: EditPaymentMethodFormState = {
  name: "",
  type: "",
  description: "",
  instructions: "",
  bankName: "",
  accountType: "",
  accountNumber: "",
  paymentLink: "",
  qrImageUrl: "",
  isActive: true,
};

export const useEditPaymentMethodForm = (
  item: PaymentMethod | null,
  id: string,
  orgId: string,
  onSuccess: () => void,
) => {
  const { apiClient } = useApiClient();
  const [form, setForm] = useState<EditPaymentMethodFormState>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (item) {
      setForm({
        name: item.name,
        type: item.type,
        description: item.description ?? "",
        instructions: item.instructions ?? "",
        bankName: item.bankName ?? "",
        accountType: item.accountType ?? "",
        accountNumber: item.accountNumber ?? "",
        paymentLink: item.paymentLink ?? "",
        qrImageUrl: item.qrImageUrl ?? "",
        isActive: item.isActive,
      });
    }
  }, [item]);

  const field =
    (key: keyof EditPaymentMethodFormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((p) => ({ ...p, [key]: e.target.value }));

  const setType = (type: string) => setForm((p) => ({ ...p, type }));

  const toggleActive = () => setForm((p) => ({ ...p, isActive: !p.isActive }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const nullable = (v: string) => v.trim() || null;
    const payload: PaymentMethodUpdatePayload = {
      name: form.name.trim(),
      type: form.type,
      description: nullable(form.description),
      instructions: nullable(form.instructions),
      bankName: nullable(form.bankName),
      accountType: nullable(form.accountType),
      accountNumber: nullable(form.accountNumber),
      paymentLink: nullable(form.paymentLink),
      qrImageUrl: nullable(form.qrImageUrl),
      isActive: form.isActive,
    };
    try {
      await apiClient(`/payment-methods/${id}?organizationId=${orgId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      onSuccess();
    } finally {
      setSaving(false);
    }
  };

  return { form, saving, field, setType, toggleActive, submit };
};
