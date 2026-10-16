import { useEffect, useMemo, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { CreditTypeOption } from "@/credits/types/credit-types";

/**
 * Tipos de crédito desde el backend, que es la fuente de verdad del enum `CreditTypes`.
 * - `types`: opciones {value, label} listas para un <select>.
 * - `labels`: mapa código → etiqueta, para renderizar un tipo suelto.
 */
export const useCreditTypes = () => {
  const { apiClient } = useApiClient();
  const [types, setTypes] = useState<CreditTypeOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient<CreditTypeOption[]>("/credits/types", { method: "GET" })
      .then((data) => setTypes(data ?? []))
      .catch(() => setTypes([]))
      .finally(() => setLoading(false));
  }, [apiClient]);

  const labels = useMemo(
    () => Object.fromEntries(types.map((t) => [t.value, t.label])) as Record<string, string>,
    [types],
  );

  return { types, labels, loading };
};
