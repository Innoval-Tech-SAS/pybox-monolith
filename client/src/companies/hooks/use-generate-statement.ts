import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { DebtorStatement } from "@/types/companies/portfolio-debtor-types";

export const useGenerateStatement = (debtorId: string | null, portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = async (creditId?: string): Promise<DebtorStatement | null> => {
    if (!debtorId || !portfolioId) return null;
    setGenerating(true);
    setError(null);
    try {
      return await apiClient<DebtorStatement>(`/debtors/${debtorId}/statements?portfolioId=${portfolioId}`, {
        method: "POST",
        body: JSON.stringify({ creditId: creditId ?? null }),
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al generar el extracto");
      return null;
    } finally {
      setGenerating(false);
    }
  };

  return { generate, generating, error };
};
