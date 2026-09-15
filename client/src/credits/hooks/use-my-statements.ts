import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { ApiError } from "@/types/api-error";
import { getSession } from "@/auth/utils/auth-session-utils";
import type { MyStatement, MyStatementListResponse } from "@/credits/types/statement-types";

export const useMyStatements = () => {
  const { apiClient } = useApiClient();
  const [statements, setStatements] = useState<MyStatement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [identityPending, setIdentityPending] = useState(false);

  const fetch = async () => {
    setLoading(true);
    setError(null);
    setIdentityPending(false);

    if (getSession()?.identityVerificationStatus !== "APROBADO") {
      setIdentityPending(true);
      setLoading(false);
      return;
    }

    try {
      const data = await apiClient<MyStatementListResponse>(
        "/statements/my-statements",
        {},
        { silentStatuses: [403, 404] },
      );
      setStatements(data?.items ?? []);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setIdentityPending(true);
      } else if (err instanceof ApiError && err.status === 404) {
        // 404 = todavía no hay un deudor asociado a este documento: estado vacío
        // normal (no todos los usuarios SELF tienen obligaciones), no un error.
        setStatements([]);
      } else {
        setError(err instanceof Error ? err.message : "Error al cargar los extractos");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetch(); }, []);

  return { statements, loading, error, identityPending, refetch: fetch };
};
