import { useCallback, useEffect, useState } from "react";
import { useApiClient, API_URL } from "@/hooks/use-api-client";
import type { IvrCampaignReport } from "../types/ivr-report-types";

export const useIvrReport = (campaignId: string) => {
  const { apiClient } = useApiClient();
  const [report, setReport] = useState<IvrCampaignReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const fetchReport = useCallback(async () => {
    if (!campaignId) return;
    setLoading(true);
    try {
      const data: IvrCampaignReport = await apiClient(
        `/ivr/reports/campaign/${campaignId}`,
        { method: "GET" },
      );
      setReport(data ?? null);
    } catch {
      setReport(null);
    } finally {
      setLoading(false);
    }
  }, [apiClient, campaignId]);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  /**
   * Descarga el CSV. No se usa `apiClient` porque este devuelve JSON parseado;
   * aquí hace falta el cuerpo crudo para armar el blob de descarga.
   */
  const exportCsv = useCallback(async (fileName: string) => {
    if (!campaignId) return;
    setExporting(true);
    try {
      const response = await fetch(
        `${API_URL}/ivr/reports/campaign/${campaignId}/export`,
        { credentials: "include" },
      );
      if (!response.ok) return;

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${fileName}.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } finally {
      setExporting(false);
    }
  }, [campaignId]);

  return { report, loading, exporting, exportCsv, refresh: fetchReport };
};
