import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { PeriodicityOption } from "@/types/campaigns/campaign-types";

export const useCampaignPeriodicities = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [periodicities, setPeriodicities] = useState<PeriodicityOption[]>([]);

  useEffect(() => {
    if (!organizationId) return;
    apiClient(`/campaigns/periodicities?organizationId=${organizationId}`, { method: "GET" })
      .then((data: PeriodicityOption[]) => setPeriodicities(data ?? []))
      .catch(() => {});
  }, [organizationId, apiClient]);

  return { periodicities };
};
