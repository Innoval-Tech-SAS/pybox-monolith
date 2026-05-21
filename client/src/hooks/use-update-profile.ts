import { useState } from "react";
import { useApiClient } from "./use-api-client";
import { getAuthHeaders } from "@/utils/auth-headers";
import { UpdateProfileRequest } from "@/types/onboarding/onboarding-types";

export const useUpdateProfile = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateProfile = async (data: UpdateProfileRequest) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient("/onboarding/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify(data),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Error al actualizar el perfil";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updateProfile, loading, error, clearError: () => setError(null) };
};
