import { useEffect, useMemo, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";

interface PaymentStatusOption {
  value: string;
  label: string;
}

/**
 * Estados de cuota desde el backend, que es la fuente de verdad del enum `PaymentStatus`.
 * Devuelve el mapa código → etiqueta para el chip de "Detalle de obligaciones".
 */
export const usePaymentStatuses = () => {
  const { apiClient } = useApiClient();
  const [statuses, setStatuses] = useState<PaymentStatusOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient<PaymentStatusOption[]>("/payments/statuses", { method: "GET" })
      .then((data) => setStatuses(data ?? []))
      .catch(() => setStatuses([]))
      .finally(() => setLoading(false));
  }, [apiClient]);

  const labels = useMemo(
    () => Object.fromEntries(statuses.map((s) => [s.value, s.label])) as Record<string, string>,
    [statuses],
  );

  return { statuses, labels, loading };
};
