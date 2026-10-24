import { useApiClient } from "@/hooks/use-api-client";
import type { PaymentAttemptResult } from "@/credits/types/wompi-checkout-types";

interface PaymentAttemptLookup {
  paymentId: string;
  attemptId: string;
  status: string;
}

/**
 * Único lugar con HTTP para la página de retorno de una redirección (Bold: PSE, Botón
 * Bancolombia, 3DS; PayU: PSE) -- el deudor vuelve sin conocer `paymentId`/`attemptId`,
 * solo la `reference` que la pasarela le devolvió en la URL de retorno compartida
 * (`RECEIVABLES_PAYMENT_REDIRECT_RETURN_URL`, reglas de `code-distribution`).
 */
export const usePaymentRedirectReturn = () => {
  const { apiClient } = useApiClient();

  const resolveByReference = async (
    reference: string,
  ): Promise<PaymentAttemptLookup | null> => {
    try {
      return await apiClient<PaymentAttemptLookup>(
        `/credits/payments/by-reference/${reference}`,
        { method: "GET" },
      );
    } catch {
      return null;
    }
  };

  const fetchAttemptStatus = async (
    paymentId: string,
    attemptId: string,
  ): Promise<PaymentAttemptResult | null> => {
    try {
      return await apiClient<PaymentAttemptResult>(
        `/credits/payments/${paymentId}/transactions/${attemptId}`,
        { method: "GET" },
      );
    } catch {
      return null;
    }
  };

  return { resolveByReference, fetchAttemptStatus };
};
