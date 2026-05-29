import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { TicketCategory } from "@/types/support/support-types";

export const useTicketCategories = () => {
  const { apiClient } = useApiClient();
  const [categories, setCategories] = useState<TicketCategory[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchCategories = useCallback(() => {
    setLoading(true);
    apiClient("/cs/tickets/categories", { method: "GET" })
      .then((data: TicketCategory[]) => setCategories(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [apiClient]);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  return { categories, loading };
};
