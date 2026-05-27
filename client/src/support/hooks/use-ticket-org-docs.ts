import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { OrgDocsData } from "@/types/support/support-types";

export const useTicketOrgDocs = (ticketId: number | undefined, enabled: boolean) => {
  const { apiClient } = useApiClient();
  const [orgDocs, setOrgDocs] = useState<OrgDocsData | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchOrgDocs = useCallback(() => {
    if (!ticketId || !enabled) return;
    setLoading(true);
    apiClient(`/cs/tickets/${ticketId}/org-docs`, { method: "GET" })
      .then((data: OrgDocsData) => setOrgDocs(data))
      .catch(() => setOrgDocs(null))
      .finally(() => setLoading(false));
  }, [apiClient, ticketId, enabled]);

  useEffect(() => {
    fetchOrgDocs();
  }, [fetchOrgDocs]);

  return { orgDocs, loading, refetch: fetchOrgDocs };
};
