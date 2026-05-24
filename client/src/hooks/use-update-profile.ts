import { useState } from "react";
import { useApiClient } from "./use-api-client";
import { UpdateProfileRequest } from "@/types/onboarding/onboarding-types";

export const useUpdateProfile = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  const updateProfile = async (data: UpdateProfileRequest) => {
    setLoading(true);
    try {
      await apiClient("/onboarding/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al guardar perfil");
    } finally {
      setLoading(false);
    }
  };

  return { updateProfile, loading, error, clearError };
};
