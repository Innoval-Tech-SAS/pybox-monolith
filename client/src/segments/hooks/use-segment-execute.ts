import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  SegmentExecuteResponse,
  SegmentExecutionResponse,
} from "@/segments/types/segment.types";

export const useSegmentExecute = (orgId: string) => {
  const { apiClient } = useApiClient();
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<SegmentExecuteResponse | null>(null);

  const execute = async (
    segmentId: number,
    mode: "preview" | "audit",
    limit?: number,
  ) => {
    setExecuting(true);
    setResult(null);
    try {
      const body: Record<string, unknown> = { mode };
      if (limit) body.limit = limit;
      const data = await apiClient(
        `/segments/${segmentId}/execute?organizationId=${orgId}`,
        { method: "POST", body: JSON.stringify(body) },
      );
      setResult(data as SegmentExecuteResponse);
      return data as SegmentExecuteResponse;
    } catch {
      return null;
    } finally {
      setExecuting(false);
    }
  };

  const clearResult = () => setResult(null);

  return { executing, result, execute, clearResult };
};

export const useSegmentExecutions = (orgId: string, segmentId: number | null) => {
  const { apiClient } = useApiClient();
  const [executions, setExecutions] = useState<SegmentExecutionResponse[]>([]);
  const [loading, setLoading] = useState(false);

  const fetch = () => {
    if (!segmentId || !orgId) return;
    setLoading(true);
    apiClient(`/segments/${segmentId}/executions?organizationId=${orgId}`)
      .then((data: SegmentExecutionResponse[]) => setExecutions(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  return { executions, loading, fetchExecutions: fetch };
};
