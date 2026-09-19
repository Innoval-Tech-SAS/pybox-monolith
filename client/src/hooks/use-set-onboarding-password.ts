import { useState } from "react";
import { useApiClient } from "./use-api-client";

export const useSetOnboardingPassword = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setPassword = async (newPassword: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient("/onboarding/set-password", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ newPassword }),
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error al guardar la contraseña";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { setPassword, loading, error };
};
