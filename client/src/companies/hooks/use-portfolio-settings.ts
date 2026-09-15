import { useCallback, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { Portfolio } from "@/types/companies/portfolio-types";

export interface DailyCounterConfig {
  portfolioId: string;
  enabled: boolean;
  reactivationMode: string;
  updatedBy: number | null;
  lastSyncedAt: string | null;
  lastSyncedCutoffDate: string | null;
}

export interface PortfolioInfoUpdate {
  name?: string;
  description?: string;
  country?: string;
}

interface PortfolioSettingsData {
  portfolio: Portfolio | null;
  config: DailyCounterConfig | null;
}

const EMPTY_DATA: PortfolioSettingsData = { portfolio: null, config: null };

export const usePortfolioSettings = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [saving, setSaving] = useState(false);

  const fetchSettings = useCallback(() => {
    if (!portfolioId) return Promise.resolve(EMPTY_DATA);
    return Promise.all([
      apiClient(`/portfolios/${portfolioId}`),
      apiClient(`/portfolios/${portfolioId}/daily-counter-config`),
    ]).then(([pf, cfg]) => ({
      portfolio: pf as Portfolio,
      config: (cfg as DailyCounterConfig) ?? null,
    }));
  }, [portfolioId, apiClient]);

  const { data, loading, error, refetch, setData } = useAsyncResource<PortfolioSettingsData>(
    fetchSettings,
    EMPTY_DATA,
    [portfolioId],
  );
  const { portfolio, config } = data;

  const toggleActive = async (isActive: boolean) => {
    setSaving(true);
    try {
      const updated: Portfolio = await apiClient(`/portfolios/${portfolioId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isActive }),
      });
      setData((prev) => ({ ...prev, portfolio: updated }));
    } finally {
      setSaving(false);
    }
  };

  const updateInfo = async (data: PortfolioInfoUpdate) => {
    setSaving(true);
    try {
      const updated: Portfolio = await apiClient(`/portfolios/${portfolioId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      setData((prev) => ({ ...prev, portfolio: updated }));
    } finally {
      setSaving(false);
    }
  };

  const saveCounterConfig = async (enabled: boolean, reactivationMode: string) => {
    setSaving(true);
    try {
      const updated: DailyCounterConfig = await apiClient(
        `/portfolios/${portfolioId}/daily-counter-config`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ enabled, reactivationMode }),
        },
      );
      setData((prev) => ({ ...prev, config: updated }));
    } finally {
      setSaving(false);
    }
  };

  const syncCounterConfig = async (targetDate?: string) => {
    setSaving(true);
    try {
      const updated: DailyCounterConfig = await apiClient(
        `/portfolios/${portfolioId}/daily-counter-config/sync`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ targetDate: targetDate || null }),
        },
      );
      setData((prev) => ({ ...prev, config: updated }));
    } finally {
      setSaving(false);
    }
  };

  return { portfolio, config, loading, error, saving, toggleActive, updateInfo, saveCounterConfig, syncCounterConfig, refetch };
};
