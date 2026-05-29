import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { Select } from "@/ui/components/inputs/select";
import { PageMeta } from "@/ui/pages/page-meta";
import { useApiClient } from "@/hooks/use-api-client";
import { PAYMENT_METHOD_TYPE_LABELS } from "@/constants/payment-methods/payment-method-labels";
import { usePaymentMethod } from "../hooks/use-payment-method";
import { usePaymentMethodTypes } from "../hooks/use-payment-method-types";
import type { PaymentMethodUpdatePayload } from "@/types/payment-methods/payment-method-types";

const SWITCH_BASE =
  "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none";

export const EditPaymentMethodPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const { apiClient } = useApiClient();
  const { item, loading } = usePaymentMethod(id ?? "", orgId);
  const { types } = usePaymentMethodTypes();

  const [form, setForm] = useState({
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
  });
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

  const backPath = `/my-companies/payment-methods?org=${orgId}`;
  const typeOptions = types.map((t) => ({ value: t, label: PAYMENT_METHOD_TYPE_LABELS[t] ?? t }));

  const field =
    (key: keyof typeof form) =>
    (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((p) => ({ ...p, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
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
      navigate(backPath);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <ModuleBase pageTitle="Editar método de pago" breadcrumbItems={[{ label: "Métodos de Pago", path: backPath }]}>
        <div className="flex h-48 items-center justify-center text-gray-400">Cargando...</div>
      </ModuleBase>
    );
  }

  if (!item) {
    return (
      <ModuleBase pageTitle="No encontrado" breadcrumbItems={[{ label: "Métodos de Pago", path: backPath }]}>
        <div className="flex h-48 items-center justify-center text-gray-500">Método de pago no encontrado.</div>
      </ModuleBase>
    );
  }

  return (
    <>
      <PageMeta title="Editar método de pago" description="Editar método de pago" />
      <ModuleBase
        pageTitle={`Editar — ${item.name}`}
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
                <div>
                  <p className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-400">Estado</p>
                  <button
                    type="button"
                    role="switch"
                    aria-checked={form.isActive}
                    onClick={() => setForm((p) => ({ ...p, isActive: !p.isActive }))}
                    className={`${SWITCH_BASE} ${form.isActive ? "bg-brand-500" : "bg-gray-200 dark:bg-gray-700"}`}
                  >
                    <span
                      className={`inline-block size-5 rounded-full bg-white shadow transition-transform ${
                        form.isActive ? "translate-x-5" : "translate-x-0"
                      }`}
                    />
                  </button>
                  <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                    {form.isActive ? "Activo" : "Inactivo"}
                  </span>
                </div>
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
              disabled={saving}
              className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
            >
              {saving ? "Guardando..." : "Guardar cambios"}
            </button>
          </div>
        </form>
      </ModuleBase>
    </>
  );
};
