import { resolvePaymentResultConfig } from "@/billing/utils/payment-result";
import type { PaymentResultViewProps } from "@/billing/types/props/payment-result-view-props";

/**
 * Vista de resultado de pago compartida por Bold (página de redirect) y Mercado Pago
 * (modal). Solo presenta icono/título/mensaje/referencia; el contenedor (página o modal)
 * y las acciones las decide quien la usa.
 */
export const PaymentResultView: React.FC<PaymentResultViewProps> = ({
  status,
  reference,
  children,
}) => {
  const config = resolvePaymentResultConfig(status);

  return (
    <div className="text-center">
      <div className="mb-5 flex justify-center">{config.icon}</div>
      <h2 className={`mb-2 text-2xl font-bold ${config.color}`}>{config.title}</h2>
      <p className="mb-4 text-sm text-gray-600 dark:text-gray-400">{config.message}</p>

      {reference && (
        <p className="mb-6 rounded-lg bg-gray-100 px-4 py-2 text-xs text-gray-500 dark:bg-gray-800 dark:text-gray-400">
          Referencia: <span className="font-mono font-medium">{reference}</span>
        </p>
      )}

      {children}
    </div>
  );
};
