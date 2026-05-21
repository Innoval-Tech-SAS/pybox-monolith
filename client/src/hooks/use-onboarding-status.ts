import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "./use-api-client";
import { getAuthHeaders } from "@/utils/auth-headers";
import { OnboardingStatus } from "@/types/onboarding/onboarding-types";

export const useOnboardingStatus = () => {
  const { apiClient } = useApiClient();
  const [status, setStatus] = useState<OnboardingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data: OnboardingStatus = await apiClient("/onboarding/status", {
        headers: { ...getAuthHeaders() },
      });
      setStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al obtener el estado del onboarding");
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  useEffect(() => { fetch(); }, [fetch]);

  return { status, loading, error, refetch: fetch };
};
