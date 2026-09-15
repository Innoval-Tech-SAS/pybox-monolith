import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { WeekdayOption } from "@/types/campaigns/campaign-types";

export const useCampaignWeekdays = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const { data: weekdays } = useAsyncResource<WeekdayOption[]>(
    () =>
      organizationId
        ? apiClient(`/campaigns/weekdays?organizationId=${organizationId}`, { method: "GET" }).then(
            (data: WeekdayOption[]) => data ?? [],
          )
        : Promise.resolve([]),
    [],
    [organizationId],
  );

  return { weekdays };
};
