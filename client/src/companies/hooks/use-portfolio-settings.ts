import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { Portfolio } from "@/types/companies/portfolio-types";

export interface DailyCounterConfig {
  portfolioId: string;
  enabled: boolean;
  reactivationMode: string;
  updatedBy: number | null;
  lastSyncedAt: string | null;
  lastSyncedCutoffDate: string | null;
}

export const usePortfolioSettings = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [config, setConfig] = useState<DailyCounterConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => {
    if (!portfolioId) return;
    setLoading(true);
    Promise.all([
      apiClient(`/portfolios/${portfolioId}`),
      apiClient(`/portfolios/${portfolioId}/daily-counter-config`),
    ])
      .then(([pf, cfg]) => {
        setPortfolio(pf as Portfolio);
        setConfig((cfg as DailyCounterConfig) ?? null);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [portfolioId]);

  useEffect(() => { load(); }, [load]);

  const toggleActive = async (isActive: boolean) => {
    setSaving(true);
    try {
      const updated: Portfolio = await apiClient(`/portfolios/${portfolioId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isActive }),
      });
      setPortfolio(updated);
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
      setConfig(updated);
    } finally {
      setSaving(false);
    }
  };

  return { portfolio, config, loading, saving, toggleActive, saveCounterConfig };
};
