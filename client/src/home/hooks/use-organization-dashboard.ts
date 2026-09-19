import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  DashboardCampaignOption,
  MonthlySends,
  OrganizationStats,
  SendStatusCounts,
} from "@/types/dashboard/dashboard-types";

/** Stats agregadas de la organización + envíos mensuales por campaña, para el Home de admin de organización. */
export const useOrganizationDashboard = (organizationId: string) => {
  const { apiClient } = useApiClient();

  const [stats, setStats] = useState<OrganizationStats | null>(null);
  const [statusCounts, setStatusCounts] = useState<SendStatusCounts | null>(null);
  const [campaigns, setCampaigns] = useState<DashboardCampaignOption[]>([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState<string>("");
  const [monthlySends, setMonthlySends] = useState<MonthlySends | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMonthlySends, setLoadingMonthlySends] = useState(false);

  useEffect(() => {
    if (!organizationId) return;
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      try {
        const [statsResult, campaignsResult, statusCountsResult] = await Promise.all([
          apiClient(`/dashboard/organization-stats?organizationId=${organizationId}`, { method: "GET" }),
          apiClient(`/dashboard/campaigns?organizationId=${organizationId}`, { method: "GET" }),
          apiClient(`/dashboard/send-status-counts?organizationId=${organizationId}`, { method: "GET" }),
        ]);
        if (cancelled) return;
        setStats(statsResult);
        setStatusCounts(statusCountsResult ?? null);
        setCampaigns(campaignsResult ?? []);
        if (campaignsResult?.[0]) {
          setSelectedCampaignId(campaignsResult[0].id);
        }
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
  }, [organizationId]);

  const loadMonthlySends = useCallback(
    async (campaignId: string) => {
      if (!campaignId) return;
      setLoadingMonthlySends(true);
      try {
        const result = await apiClient(
          `/dashboard/monthly-sends?organizationId=${organizationId}&campaignId=${campaignId}`,
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
    [organizationId],
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
