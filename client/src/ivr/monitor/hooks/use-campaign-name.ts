import { useCallback } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { Campaign } from "@/types/campaigns/campaign-types";

/** Nombre de la campaña asociada a un monitor/reporte IVR, para el título de la página. */
export const useCampaignName = (campaignId: string, portfolioId: string) => {
  const { apiClient } = useApiClient();

  const fetchCampaignName = useCallback(() => {
    if (!campaignId || !portfolioId) return Promise.resolve("");
    return apiClient(`/campaigns/${campaignId}?portfolioId=${portfolioId}`, { method: "GET" }).then(
      (campaign: Campaign) => campaign?.name ?? "",
    );
  }, [apiClient, campaignId, portfolioId]);

  const { data } = useAsyncResource<string>(fetchCampaignName, "", [campaignId, portfolioId]);

  return data;
};
