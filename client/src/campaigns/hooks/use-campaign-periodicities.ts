import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { PeriodicityOption } from "@/types/campaigns/campaign-types";

export const useCampaignPeriodicities = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const { data: periodicities } = useAsyncResource<PeriodicityOption[]>(
    () =>
      organizationId
        ? apiClient(`/campaigns/periodicities?organizationId=${organizationId}`, { method: "GET" }).then(
            (data: PeriodicityOption[]) => data ?? [],
          )
        : Promise.resolve([]),
    [],
    [organizationId],
  );

  return { periodicities };
};
