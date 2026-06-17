import { useState, useEffect } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { ReportResponse } from "@/reports/types/report.types";

export const useReports = (orgId: string) => {
  const { apiClient } = useApiClient();
  const [reports, setReports] = useState<ReportResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = () => {
    if (!orgId) { setLoading(false); return; }
    setLoading(true);
    apiClient(`/reports/?organizationId=${orgId}`)
      .then((data: ReportResponse[]) => setReports(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetch(); }, [orgId]);

  const deleteReport = async (id: string) => {
    await apiClient(`/reports/${id}?organizationId=${orgId}`, { method: "DELETE" });
    setReports((prev) => prev.filter((r) => r.id !== id));
  };

  return { reports, loading, refetch: fetch, deleteReport };
};
