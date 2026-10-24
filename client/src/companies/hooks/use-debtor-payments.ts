import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { DebtorCreditWithInstallments } from "@/types/companies/portfolio-debtor-types";

export const useDebtorPayments = (debtorId: string | null, portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [credits, setCredits] = useState<DebtorCreditWithInstallments[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPayments = () => {
    if (!debtorId || !portfolioId) {
      setCredits([]);
      return;
    }
    setLoading(true);
    setError(null);
    apiClient(`/debtors/${debtorId}/payments?portfolioId=${portfolioId}`)
      .then((d: DebtorCreditWithInstallments[]) => setCredits(d ?? []))
      .catch((err) => setError(err instanceof Error ? err.message : "Error al cargar el calendario de pagos"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPayments();
  }, [debtorId, portfolioId]);

  return { credits, loading, error, refetch: fetchPayments };
};
