import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { TicketOrg } from "@/types/support/support-types";

export const useTicketOrgs = () => {
  const { apiClient } = useApiClient();
  const { data: orgs, loading } = useAsyncResource<TicketOrg[]>(
    () => apiClient("/cs/tickets/orgs", { method: "GET" }).then((data: TicketOrg[]) => data ?? []),
    [],
    [],
  );

  return { orgs, loading };
};
