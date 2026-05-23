import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "./use-api-client";
import { OnboardingStatus } from "@/types/onboarding/onboarding-types";

export const useOnboardingStatus = () => {
  const { apiClient } = useApiClient();
  const [status, setStatus] = useState<OnboardingStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    try {
      const data: OnboardingStatus = await apiClient("/onboarding/status");
      setStatus(data);
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  return { status, loading, refetch: fetchStatus };
};
