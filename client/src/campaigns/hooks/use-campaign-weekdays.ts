import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { WeekdayOption } from "@/types/campaigns/campaign-types";

export const useCampaignWeekdays = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [weekdays, setWeekdays] = useState<WeekdayOption[]>([]);

  useEffect(() => {
    if (!organizationId) return;
    apiClient(`/campaigns/weekdays?organizationId=${organizationId}`, { method: "GET" })
      .then((data: WeekdayOption[]) => setWeekdays(data ?? []))
      .catch(() => {});
  }, [organizationId, apiClient]);

  return { weekdays };
};
