import { useEffect, useMemo, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { JudicialPriorityOption } from "@/credits/types/judicial-types";

/**
 * Prioridades judiciales desde el backend, que es la fuente de verdad del enum
 * `JudicialPriority`. Devuelve el mapa código → etiqueta para el chip del buzón.
 */
export const useJudicialPriorities = () => {
  const { apiClient } = useApiClient();
  const [priorities, setPriorities] = useState<JudicialPriorityOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient<JudicialPriorityOption[]>("/judicial-notifications/priorities", { method: "GET" })
      .then((data) => setPriorities(data ?? []))
      .catch(() => setPriorities([]))
      .finally(() => setLoading(false));
  }, [apiClient]);

  const labels = useMemo(
    () => Object.fromEntries(priorities.map((p) => [p.value, p.label])) as Record<string, string>,
    [priorities],
  );

  return { priorities, labels, loading };
};
