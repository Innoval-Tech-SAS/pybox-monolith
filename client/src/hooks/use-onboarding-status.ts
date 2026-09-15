import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "./use-api-client";
import { OnboardingStatus } from "@/types/onboarding/onboarding-types";

export const useOnboardingStatus = () => {
  const { apiClient } = useApiClient();
  const [status, setStatus] = useState<OnboardingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    try {
      const data: OnboardingStatus = await apiClient("/onboarding/status");
      setStatus(data);
      setError(false);
    } catch {
      // Fail-safe: si no se pudo confirmar el estado de onboarding, `status` se
      // limpia y `error` queda en true. OnboardingGuard debe bloquear el acceso
      // (fail-closed) en vez de interpretar `status === null` como "sin pasos
      // pendientes" — apiClient ya mostró el toast con el detalle del error.
      setStatus(null);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  useEffect(() => {
    if (!sessionStorage.getItem("user")) {
      setLoading(false);
      return;
    }
    fetchStatus();
  }, [fetchStatus]);

  return { status, loading, error, refetch: fetchStatus };
};
