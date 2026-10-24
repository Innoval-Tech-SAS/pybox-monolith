import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { ManagedUserCreate, ManagedUserResponse } from "@/types/users/managed-user-types";

export const useCreateOrgMember = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createOrgMember = async (orgId: string, payload: ManagedUserCreate): Promise<ManagedUserResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      return await apiClient(`/organizations/${orgId}/members`, {
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

  return { createOrgMember, loading, error };
};
