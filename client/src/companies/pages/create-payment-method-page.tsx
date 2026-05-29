import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { Select } from "@/ui/components/inputs/select";
import { PageMeta } from "@/ui/pages/page-meta";
import { useApiClient } from "@/hooks/use-api-client";
import { PAYMENT_METHOD_TYPE_LABELS } from "@/constants/payment-methods/payment-method-labels";
import { usePaymentMethodTypes } from "../hooks/use-payment-method-types";
import type { PaymentMethodCreatePayload } from "@/types/payment-methods/payment-method-types";

const EMPTY_FORM = {
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

export const CreatePaymentMethodPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const { apiClient } = useApiClient();
  const { types } = usePaymentMethodTypes();

  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const backPath = `/my-companies/payment-methods?org=${orgId}`;
  const typeOptions = types.map((t) => ({ value: t, label: PAYMENT_METHOD_TYPE_LABELS[t] ?? t }));

  const field =
    (key: keyof typeof EMPTY_FORM) =>
    (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((p) => ({ ...p, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.type) return;
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
      navigate(backPath);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageMeta title="Nuevo método de pago" description="Crear método de pago" />
      <ModuleBase
        pageTitle="Nuevo método de pago"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          { label: "Métodos de Pago", path: backPath },
        ]}
      >
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            <Card>
              <CardTitle>Información general</CardTitle>
              <div className="grid grid-cols-1 gap-5">
                <Input
                  label="Nombre *"
                  id="name"
                  value={form.name}
                  onChange={field("name")}
                  placeholder="Nombre del método"
                />
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                    Tipo <span className="text-error-500">*</span>
                  </label>
                  <Select
                    options={typeOptions}
                    value={form.type}
                    placeholder="Seleccionar tipo"
                    onChange={(v) => setForm((p) => ({ ...p, type: v }))}
                  />
                </div>
                <Input
                  label="Descripción"
                  id="description"
                  value={form.description}
                  onChange={field("description")}
                  placeholder="Descripción opcional"
                />
                <Input
                  label="Instrucciones"
                  id="instructions"
                  value={form.instructions}
                  onChange={field("instructions")}
                  placeholder="Instrucciones de pago"
                />
              </div>
            </Card>

            <Card>
              <CardTitle>Datos bancarios / digitales</CardTitle>
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                <Input
                  label="Banco"
                  id="bankName"
                  value={form.bankName}
                  onChange={field("bankName")}
                  placeholder="Nombre del banco"
                />
                <Input
                  label="Tipo de cuenta"
                  id="accountType"
                  value={form.accountType}
                  onChange={field("accountType")}
                  placeholder="Ahorros / Corriente"
                />
                <div className="sm:col-span-2">
                  <Input
                    label="Número de cuenta"
                    id="accountNumber"
                    value={form.accountNumber}
                    onChange={field("accountNumber")}
                    placeholder="Número de cuenta"
                  />
                </div>
                <div className="sm:col-span-2">
                  <Input
                    label="Enlace de pago"
                    id="paymentLink"
                    value={form.paymentLink}
                    onChange={field("paymentLink")}
                    placeholder="https://..."
                  />
                </div>
                <div className="sm:col-span-2">
                  <Input
                    label="URL imagen QR"
                    id="qrImageUrl"
                    value={form.qrImageUrl}
                    onChange={field("qrImageUrl")}
                    placeholder="https://..."
                  />
                </div>
              </div>
            </Card>
          </div>

          <div className="mt-5 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={() => navigate(backPath)}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving || !form.name.trim() || !form.type}
              className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
            >
              {saving ? "Creando..." : "Crear método"}
            </button>
          </div>
        </form>
      </ModuleBase>
    </>
  );
};
