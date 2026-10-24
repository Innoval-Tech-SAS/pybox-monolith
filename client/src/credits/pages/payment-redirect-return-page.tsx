import { useEffect, useRef, useState } from "react";
import { useSearchParams, useNavigate } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { Button } from "@/ui/components/button/button";
import { Badge } from "@/ui/components/badge";
import { usePaymentRedirectReturn } from "@/credits/hooks/use-payment-redirect-return";
import type { PaymentAttemptResult } from "@/credits/types/wompi-checkout-types";

const POLL_INTERVAL_MS = 2500;

const STATUS_META: Record<string, { label: string; color: "success" | "error" | "warning" }> = {
  APPROVED: { label: "Pago aprobado", color: "success" },
  DECLINED: { label: "Pago rechazado", color: "error" },
  ERROR: { label: "Hubo un error con el pago", color: "error" },
  VOIDED: { label: "El pago fue anulado", color: "warning" },
};

/**
 * Retorno de una redirección de Bold (PSE, Botón Bancolombia, 3DS), PayU (PSE) o
 * ePayco (PSE) -- a diferencia del reto embebido de Wompi, el deudor vuelve a esta
 * página sin conocer `paymentId`/`attemptId`. Bold/PayU reenvían NUESTRA `reference`
 * (ver `BoldGateway.create_transaction`/`PayUGateway.create_transaction`); ePayco solo
 * conoce su propio `ref_payco` (`EpaycoGateway._build_response_url`) -- el backend
 * resuelve cualquiera de los dos (ver `PaymentCheckoutService.resolve_by_reference`).
 */
export const PaymentRedirectReturnPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { resolveByReference, fetchAttemptStatus } = usePaymentRedirectReturn();

  const reference = searchParams.get("reference") ?? searchParams.get("ref_payco") ?? "";
  const [paymentId, setPaymentId] = useState<string | null>(null);
  const [attempt, setAttempt] = useState<PaymentAttemptResult | null>(null);
  const [notFound, setNotFound] = useState(false);
  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!reference) {
      setNotFound(true);
      return;
    }
    resolveByReference(reference).then((lookup) => {
      if (!lookup) {
        setNotFound(true);
        return;
      }
      setPaymentId(lookup.paymentId);
      fetchAttemptStatus(lookup.paymentId, lookup.attemptId).then((next) => {
        if (next) setAttempt(next);
      });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reference]);

  useEffect(() => {
    if (!attempt || !paymentId || attempt.status !== "PENDING") return;
    pollTimer.current = setTimeout(async () => {
      const next = await fetchAttemptStatus(paymentId, attempt.id);
      if (next) setAttempt(next);
    }, POLL_INTERVAL_MS);
    return () => {
      if (pollTimer.current) clearTimeout(pollTimer.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt, paymentId]);

  const meta = attempt ? STATUS_META[attempt.status] : null;

  return (
    <>
      <PageMeta title="Resultado del pago" description="Resultado del proceso de pago" />
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 dark:bg-gray-900">
        <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-lg dark:border-gray-800 dark:bg-gray-900">
          {notFound && (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              No encontramos este intento de pago.
            </p>
          )}

          {!notFound && !attempt && (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Verificando tu pago...
            </p>
          )}

          {attempt && !meta && (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Verificando tu pago...
            </p>
          )}

          {attempt && meta && (
            <div className="flex flex-col items-center gap-3">
              <Badge color={meta.color} size="md">{meta.label}</Badge>
              {attempt.providerReference && (
                <p className="rounded-lg bg-gray-100 px-4 py-2 text-xs text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                  Referencia:{" "}
                  <span className="font-mono font-medium">{attempt.providerReference}</span>
                </p>
              )}
            </div>
          )}

          <Button
            type="button"
            size="sm"
            className="mt-6 w-full"
            onClick={() => navigate("/my-credits", { replace: true })}
          >
            Ir a mis créditos
          </Button>
        </div>
      </div>
    </>
  );
};
