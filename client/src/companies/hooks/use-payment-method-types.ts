import { useCallback } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";

export const usePaymentMethodTypes = () => {
  const { apiClient } = useApiClient();

  const fetchTypes = useCallback(
    () => apiClient("/payment-methods/types", { method: "GET" }) as Promise<string[]>,
    [apiClient],
  );

  const { data: types, loading, error, refetch } = useAsyncResource<string[]>(fetchTypes, []);

  return { types, loading, error, refetch };
};
