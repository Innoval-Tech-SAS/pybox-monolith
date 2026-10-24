import type { PaymentMethodCardProps } from "@/types/props/payment-method-card-props";
import { PAYMENT_METHOD_TYPE_LABELS } from "@/constants/payment-methods/payment-method-labels";

export const PaymentMethodCard: React.FC<PaymentMethodCardProps> = ({ method }) => {
  const rows: { label: string; value: string }[] = [];
  if (method.bankName) rows.push({ label: "Banco", value: method.bankName });
  if (method.accountType) rows.push({ label: "Tipo de cuenta", value: method.accountType });
  if (method.accountNumber) rows.push({ label: "Número de cuenta", value: method.accountNumber });
  if (method.description) rows.push({ label: "Descripción", value: method.description });
  if (method.instructions) rows.push({ label: "Instrucciones", value: method.instructions });

  return (
    <div className="rounded-lg border border-gray-100 bg-gray-50 p-3 dark:border-gray-700 dark:bg-white/5">
      <div className="mb-2 flex items-center justify-between gap-2">
        <p className="text-sm font-medium text-gray-800 dark:text-white/90">{method.name}</p>
        <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900 dark:text-blue-300 whitespace-nowrap">
          {PAYMENT_METHOD_TYPE_LABELS[method.type] ?? method.type}
        </span>
      </div>
      {rows.map((r) => (
        <div key={r.label} className="mt-1 flex gap-2 text-xs">
          <span className="shrink-0 text-gray-400 dark:text-gray-500">{r.label}:</span>
          <span className="text-gray-700 dark:text-gray-300">{r.value}</span>
        </div>
      ))}
      {method.paymentLink && (
        <div className="mt-1 flex gap-2 text-xs">
          <span className="shrink-0 text-gray-400 dark:text-gray-500">Enlace:</span>
          <a
            href={method.paymentLink}
            target="_blank"
            rel="noopener noreferrer"
            className="truncate text-blue-600 underline dark:text-blue-400"
          >
            {method.paymentLink}
          </a>
        </div>
      )}
      {method.qrImageUrl && (
        <div className="mt-2">
          <img
            src={method.qrImageUrl}
            alt={`QR ${method.name}`}
            className="h-28 w-28 rounded object-contain"
          />
        </div>
      )}
    </div>
  );
};
