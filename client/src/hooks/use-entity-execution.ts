import { useState } from "react";
import { useApiClient } from "./use-api-client";

type ExecutableKind = "segments" | "reports";

// Compartido por segments y reports: ambos exponen el mismo contrato
// POST /{kind}/{id}/execute y GET /{kind}/{id}/executions.
export const useEntityExecute = <TResult,>(kind: ExecutableKind, scopeId: string) => {
  const { apiClient } = useApiClient();
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<TResult | null>(null);
  const [jobAccepted, setJobAccepted] = useState(false);
  const paramName = kind === "segments" ? "portfolioId" : "organizationId";

  const execute = async (entityId: string, mode: "preview" | "audit", limit?: number) => {
    setExecuting(true);
    setResult(null);
    setJobAccepted(false);
    try {
      const body: Record<string, unknown> = { mode };
      if (limit) body.limit = limit;
      const data = await apiClient(`/${kind}/${entityId}/execute?${paramName}=${scopeId}`, {
        method: "POST",
        body: JSON.stringify(body),
      });
      // 202 audit accepted: el backend devuelve {message, reportId, mode} sin rows/columns
      if (mode === "audit" && data && "reportId" in (data as Record<string, unknown>)) {
        setJobAccepted(true);
        return null;
      }
      setResult(data as TResult);
      return data as TResult;
    } catch {
      return null;
    } finally {
      setExecuting(false);
    }
  };

  const clearResult = () => {
    setResult(null);
    setJobAccepted(false);
  };

  return { executing, result, jobAccepted, execute, clearResult };
};

export const useEntityExecutions = <TItem,>(
  kind: ExecutableKind,
  scopeId: string,
  entityId: string | null,
) => {
  const { apiClient } = useApiClient();
  const [executions, setExecutions] = useState<TItem[]>([]);
  const [loading, setLoading] = useState(false);
  const paramName = kind === "segments" ? "portfolioId" : "organizationId";

  const fetch = () => {
    if (!entityId || !scopeId) return;
    setLoading(true);
    apiClient(`/${kind}/${entityId}/executions?${paramName}=${scopeId}`)
      .then((data: TItem[]) => setExecutions(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  return { executions, loading, fetchExecutions: fetch };
};
