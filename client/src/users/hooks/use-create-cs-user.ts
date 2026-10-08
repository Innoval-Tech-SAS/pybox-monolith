import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { ManagedUserCreate, ManagedUserResponse } from "@/types/users/managed-user-types";

export const useCreateCsUser = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createCsUser = async (payload: ManagedUserCreate): Promise<ManagedUserResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      return await apiClient("/users/global", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al crear el usuario.";
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { createCsUser, loading, error };
};
