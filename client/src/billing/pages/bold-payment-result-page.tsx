import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { Button } from "@/ui/components/button/button";
import { PaymentResultView } from "../components/payment-result-view";
import { BOLD_REDIRECT_COUNTDOWN_SECONDS } from "../constants/bold-payment-result";

export const BoldPaymentResultPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(BOLD_REDIRECT_COUNTDOWN_SECONDS);

  const orderId = searchParams.get("bold-order-id") ?? "";
  const txStatus = searchParams.get("bold-tx-status") ?? "";

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
        <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-lg dark:border-gray-800 dark:bg-gray-900">
          <PaymentResultView status={txStatus} reference={orderId}>
            <Button
              type="button"
              size="sm"
              className="mb-3 w-full"
              onClick={() => navigate("/my-companies", { replace: true })}
            >
              Ir a mis empresas
            </Button>

            <p className="text-xs text-gray-400 dark:text-gray-500">
              Serás redirigido automáticamente en {countdown}s…
            </p>
          </PaymentResultView>
        </div>
      </div>
    </>
  );
};
