import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { UpdateUserPayload, UserDetail } from "@/types/users/user-types";

export const useUpdateUser = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateUser = async (userId: string, data: UpdateUserPayload): Promise<UserDetail | null> => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient(`/users/${userId}`, { method: "PATCH", body: JSON.stringify(data) });
      return result as UserDetail;
    } catch {
      setError("Error al actualizar el usuario.");
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { updateUser, loading, error };
};
