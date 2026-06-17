import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router";
import { CheckCircle, XCircle, Clock } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";

type BoldTxStatus = "APPROVED" | "DECLINED" | "PENDING" | string;

const STATUS_CONFIG: Record<
  string,
  { icon: React.ReactNode; title: string; message: string; color: string }
> = {
  APPROVED: {
    icon: <CheckCircle size={56} className="text-success-500" />,
    title: "¡Pago exitoso!",
    message: "Tu pago fue procesado correctamente. Gracias por tu pago.",
    color: "text-success-600 dark:text-success-400",
  },
  DECLINED: {
    icon: <XCircle size={56} className="text-error-500" />,
    title: "Pago rechazado",
    message:
      "Tu pago no pudo ser procesado. Por favor intenta de nuevo o usa otro método de pago.",
    color: "text-error-600 dark:text-error-400",
  },
  PENDING: {
    icon: <Clock size={56} className="text-warning-500" />,
    title: "Pago en proceso",
    message:
      "Tu pago está siendo verificado. Te notificaremos cuando se confirme.",
    color: "text-warning-600 dark:text-warning-400",
  },
};

const DEFAULT_STATUS = {
  icon: <Clock size={56} className="text-gray-400" />,
  title: "Estado desconocido",
  message:
    "No pudimos determinar el estado de tu pago. Revisa tu factura para más detalles.",
  color: "text-gray-600 dark:text-gray-400",
};

export const BoldPaymentResultPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(8);

  const orderId = searchParams.get("bold-order-id") ?? "";
  const txStatus: BoldTxStatus = searchParams.get("bold-tx-status") ?? "";

  const config = STATUS_CONFIG[txStatus] ?? DEFAULT_STATUS;

  useEffect(() => {
    if (countdown <= 0) {
      navigate("/my-companies", { replace: true });
      return;
    }
    const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown, navigate]);

  return (
    <>
      <PageMeta
        title="Resultado del pago"
        description="Resultado del proceso de pago Bold"
      />
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 dark:bg-gray-900">
        <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-lg dark:border-gray-800 dark:bg-gray-900">
          <div className="mb-5 flex justify-center">{config.icon}</div>
          <h1 className={`mb-2 text-2xl font-bold ${config.color}`}>
            {config.title}
          </h1>
          <p className="mb-4 text-sm text-gray-600 dark:text-gray-400">
            {config.message}
          </p>

          {orderId && (
            <p className="mb-6 rounded-lg bg-gray-100 px-4 py-2 text-xs text-gray-500 dark:bg-gray-800 dark:text-gray-400">
              Referencia:{" "}
              <span className="font-mono font-medium">{orderId}</span>
            </p>
          )}

          <button
            onClick={() => navigate("/my-companies", { replace: true })}
            className="mb-3 w-full rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
          >
            Ir a mis empresas
          </button>

          <p className="text-xs text-gray-400 dark:text-gray-500">
            Serás redirigido automáticamente en {countdown}s…
          </p>
        </div>
      </div>
    </>
  );
};
