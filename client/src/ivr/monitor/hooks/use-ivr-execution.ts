import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { IvrExecution } from "../types/ivr-execution-types";

/**
 * Control de la ejecución (bulk) de una campaña IVR: pausar, reanudar,
 * cancelar y ajustar el ritmo de marcación.
 *
 * Una campaña puede tener varios bulks (envíos grandes se trocean en
 * `BATCH_SIZE`, y una campaña recurrente genera uno por disparo). Se opera
 * sobre **el más reciente**, que es lo que suele importar en el monitor; el
 * histórico completo vive en `GET /ivr/executions/campaign/{id}` si hace
 * falta más adelante.
 */
export const useIvrExecution = (campaignId: string) => {
  const { apiClient } = useApiClient();
  const [execution, setExecution] = useState<IvrExecution | null>(null);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState(false);

  const fetchLatest = useCallback(async () => {
    if (!campaignId) return;
    setLoading(true);
    try {
      const list: IvrExecution[] = await apiClient(
        `/ivr/executions/campaign/${campaignId}`,
        { method: "GET" },
      );
      setExecution(list?.[0] ?? null);
    } catch {
      setExecution(null);
    } finally {
      setLoading(false);
    }
  }, [apiClient, campaignId]);

  useEffect(() => {
    fetchLatest();
  }, [fetchLatest]);

  const act = useCallback(
    async (action: "pause" | "resume" | "cancel") => {
      if (!execution) return;
      setActing(true);
      try {
        const updated: IvrExecution = await apiClient(
          `/ivr/executions/${execution.bulkId}/${action}`,
          { method: "POST" },
        );
        setExecution(updated);
      } catch {
        // el toast de error ya lo muestra useApiClient; se refresca por si acaso
        await fetchLatest();
      } finally {
        setActing(false);
      }
    },
    [apiClient, execution, fetchLatest],
  );

  const setAllocation = useCallback(
    async (callsPerSecond: number | null, maxConcurrent: number | null) => {
      if (!execution) return;
      setActing(true);
      try {
        const updated: IvrExecution = await apiClient(
          `/ivr/executions/${execution.bulkId}/allocation`,
          {
            method: "PATCH",
            body: JSON.stringify({ callsPerSecond, maxConcurrent }),
          },
        );
        setExecution(updated);
      } catch {
        await fetchLatest();
      } finally {
        setActing(false);
      }
    },
    [apiClient, execution, fetchLatest],
  );

  return {
    execution,
    loading,
    acting,
    pause: () => act("pause"),
    resume: () => act("resume"),
    cancel: () => act("cancel"),
    setAllocation,
    refresh: fetchLatest,
  };
};
