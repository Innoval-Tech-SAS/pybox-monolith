import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { CreditWithPayments } from "@/credits/types/credit-types";

export const useMyCredits = () => {
  const { apiClient } = useApiClient();
  const [credits, setCredits] = useState<CreditWithPayments[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = (await apiClient("/credits/my-credits")) as CreditWithPayments[];
      setCredits(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar los créditos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetch(); }, []);

  return { credits, loading, error, refetch: fetch };
};
