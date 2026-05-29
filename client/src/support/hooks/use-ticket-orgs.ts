import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { TicketOrg } from "@/types/support/support-types";

export const useTicketOrgs = () => {
  const { apiClient } = useApiClient();
  const [orgs, setOrgs] = useState<TicketOrg[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchOrgs = useCallback(() => {
    setLoading(true);
    apiClient("/cs/tickets/orgs", { method: "GET" })
      .then((data: TicketOrg[]) => setOrgs(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [apiClient]);

  useEffect(() => {
    fetchOrgs();
  }, [fetchOrgs]);

  return { orgs, loading };
};
