import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { PaymentMethod } from "@/types/payment-methods/payment-method-types";

export const usePaymentMethod = (id: string, organizationId: string) => {
  const { apiClient } = useApiClient();
  const [item, setItem] = useState<PaymentMethod | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchItem = useCallback(() => {
    if (!id || !organizationId) return;
    setLoading(true);
    apiClient(`/payment-methods/${id}?organizationId=${organizationId}`, { method: "GET" })
      .then((data: PaymentMethod) => setItem(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id, organizationId, apiClient]);

  useEffect(() => {
    fetchItem();
  }, [fetchItem]);

  return { item, loading };
};
