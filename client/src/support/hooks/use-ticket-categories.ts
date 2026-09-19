import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { TicketCategory } from "@/types/support/support-types";

export const useTicketCategories = () => {
  const { apiClient } = useApiClient();
  const { data: categories, loading } = useAsyncResource<TicketCategory[]>(
    () => apiClient("/cs/tickets/categories", { method: "GET" }).then((data: TicketCategory[]) => data ?? []),
    [],
    [],
  );

  return { categories, loading };
};
