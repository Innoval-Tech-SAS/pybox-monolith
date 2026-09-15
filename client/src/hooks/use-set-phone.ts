import { useState } from "react";
import { useApiClient } from "./use-api-client";

export const useSetPhone = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setPhone = async (phoneNumber: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient("/onboarding/phone", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phoneNumber }),
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error al guardar el teléfono";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { setPhone, loading, error };
};
