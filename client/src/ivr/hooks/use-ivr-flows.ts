import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { IvrFlowSummary } from "@/ivr/types/ivr-flow-record";

/**
 * Lista de flujos IVR de un portafolio, para selectores (wizard de campaña).
 */
export const useIvrFlows = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [flows, setFlows] = useState<IvrFlowSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!portfolioId) {
      setFlows([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    apiClient(`/ivr/flows/?portfolioId=${portfolioId}`, { method: "GET" })
      .then((data: IvrFlowSummary[]) =>
        setFlows((data ?? []).map((f) => ({ id: f.id, name: f.name }))),
      )
      .catch(() => setFlows([]))
      .finally(() => setLoading(false));
  }, [portfolioId, apiClient]);

  return { flows, loading };
};
