import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";

export const usePaymentMethodTypes = () => {
  const { apiClient } = useApiClient();
  const [types, setTypes] = useState<string[]>([]);

  const fetchTypes = useCallback(() => {
    apiClient("/payment-methods/types", { method: "GET" })
      .then((data: string[]) => setTypes(data ?? []))
      .catch(() => {});
  }, [apiClient]);

  useEffect(() => {
    fetchTypes();
  }, [fetchTypes]);

  return { types };
};
