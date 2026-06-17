import { Card, CardTitle } from "@/ui/components/card";
import type { PaymentMethodStepSummaryProps } from "@/companies/types/payment-method-form-props";

const SummaryRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="rounded-lg border border-gray-100 px-4 py-3 dark:border-gray-800">
    <p className="text-xs font-medium uppercase text-gray-500 dark:text-gray-400">{label}</p>
    <p className="mt-1 break-words text-sm font-medium text-gray-800 dark:text-white/90">
      {value.trim() || "No registrado"}
    </p>
  </div>
);

export const PaymentMethodStepSummary: React.FC<PaymentMethodStepSummaryProps> = ({ form, typeLabel }) => (
  <Card>
    <CardTitle>Resumen</CardTitle>
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <SummaryRow label="Nombre" value={form.name} />
      <SummaryRow label="Tipo" value={typeLabel} />
      <SummaryRow label="Descripción" value={form.description} />
      <SummaryRow label="Instrucciones" value={form.instructions} />
      <SummaryRow label="Banco" value={form.bankName} />
      <SummaryRow label="Tipo de cuenta" value={form.accountType} />
      <SummaryRow label="Número de cuenta" value={form.accountNumber} />
      <SummaryRow label="Enlace de pago" value={form.paymentLink} />
      <SummaryRow label="URL imagen QR" value={form.qrImageUrl} />
    </div>
  </Card>
);
