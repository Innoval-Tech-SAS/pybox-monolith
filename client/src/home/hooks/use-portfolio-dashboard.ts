import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { DashboardCampaignOption, MonthlySends, SendStatusCounts } from "@/types/dashboard/dashboard-types";
import type { PortfolioStats } from "@/types/portfolios/portfolio-stats";
import type { CampaignListResponse } from "@/types/campaigns/campaign-types";

/** Stats de un portafolio puntual + envíos mensuales por campaña, para el Home de usuarios de organización. */
export const usePortfolioDashboard = (portfolioId: string) => {
  const { apiClient } = useApiClient();

  const [stats, setStats] = useState<PortfolioStats | null>(null);
  const [statusCounts, setStatusCounts] = useState<SendStatusCounts | null>(null);
  const [campaigns, setCampaigns] = useState<DashboardCampaignOption[]>([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState<string>("");
  const [monthlySends, setMonthlySends] = useState<MonthlySends | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMonthlySends, setLoadingMonthlySends] = useState(false);

  useEffect(() => {
    if (!portfolioId) return;
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      try {
        const [statsResult, campaignsResult, statusCountsResult] = await Promise.all([
          apiClient(`/portfolios/${portfolioId}/stats`, { method: "GET" }),
          apiClient(`/campaigns/?portfolioId=${portfolioId}&pageSize=100`, { method: "GET" }),
          apiClient(`/portfolios/${portfolioId}/send-status-counts`, { method: "GET" }),
        ]);
        if (cancelled) return;
        setStats(statsResult);
        setStatusCounts(statusCountsResult ?? null);
        const options = ((campaignsResult as CampaignListResponse)?.items ?? []).map((c) => ({
          id: c.id,
          name: c.name,
        }));
        setCampaigns(options);
        if (options[0]) setSelectedCampaignId(options[0].id);
      } catch {
        if (!cancelled) {
          setStats(null);
          setStatusCounts(null);
          setCampaigns([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [portfolioId]);

  const loadMonthlySends = useCallback(
    async (campaignId: string) => {
      if (!campaignId) return;
      setLoadingMonthlySends(true);
      try {
        const result = await apiClient(
          `/portfolios/${portfolioId}/monthly-sends?campaignId=${campaignId}`,
          { method: "GET" },
        );
        setMonthlySends(result);
      } catch {
        setMonthlySends(null);
      } finally {
        setLoadingMonthlySends(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [portfolioId],
  );

  useEffect(() => {
    if (selectedCampaignId) loadMonthlySends(selectedCampaignId);
  }, [selectedCampaignId, loadMonthlySends]);

  return {
    stats,
    statusCounts,
    campaigns,
    selectedCampaignId,
    setSelectedCampaignId,
    monthlySends,
    loading,
    loadingMonthlySends,
  };
};
