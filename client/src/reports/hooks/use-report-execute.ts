import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  ReportExecuteResponse,
  ReportExecutionResponse,
} from "@/reports/types/report.types";

export const useReportExecute = (orgId: string) => {
  const { apiClient } = useApiClient();
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<ReportExecuteResponse | null>(null);

  const execute = async (
    reportId: string,
    mode: "preview" | "audit",
    limit?: number,
  ) => {
    setExecuting(true);
    setResult(null);
    try {
      const body: Record<string, unknown> = { mode };
      if (limit) body.limit = limit;
      const data = await apiClient(
        `/reports/${reportId}/execute?organizationId=${orgId}`,
        { method: "POST", body: JSON.stringify(body) },
      );
      setResult(data as ReportExecuteResponse);
      return data as ReportExecuteResponse;
    } catch {
      return null;
    } finally {
      setExecuting(false);
    }
  };

  const clearResult = () => setResult(null);

  return { executing, result, execute, clearResult };
};

export const useReportExecutions = (orgId: string, reportId: string | null) => {
  const { apiClient } = useApiClient();
  const [executions, setExecutions] = useState<ReportExecutionResponse[]>([]);
  const [loading, setLoading] = useState(false);

  const fetch = () => {
    if (!reportId || !orgId) return;
    setLoading(true);
    apiClient(`/reports/${reportId}/executions?organizationId=${orgId}`)
      .then((data: ReportExecutionResponse[]) => setExecutions(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  return { executions, loading, fetchExecutions: fetch };
};
