import { useCallback } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { PaymentMethod } from "@/types/payment-methods/payment-method-types";

export const usePaymentMethod = (id: string, organizationId: string) => {
  const { apiClient } = useApiClient();

  const fetchItem = useCallback(() => {
    if (!id || !organizationId) return Promise.resolve(null);
    return apiClient(`/payment-methods/${id}?organizationId=${organizationId}`, { method: "GET" }) as Promise<PaymentMethod | null>;
  }, [id, organizationId, apiClient]);

  const { data: item, loading, error, refetch } = useAsyncResource<PaymentMethod | null>(
    fetchItem,
    null,
    [id, organizationId],
  );

  return { item, loading, error, refetch };
};
