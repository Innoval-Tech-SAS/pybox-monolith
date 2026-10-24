import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";

export const useRestoreUser = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const restoreUser = async (userId: string): Promise<boolean> => {
    setLoading(true);
    try {
      await apiClient(`/users/${userId}/restore`, { method: "POST" });
      return true;
    } catch {
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { restoreUser, loading };
};
