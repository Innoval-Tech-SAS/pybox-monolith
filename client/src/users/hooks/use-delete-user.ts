import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";

export const useDeleteUser = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const deleteUser = async (userId: number): Promise<boolean> => {
    setLoading(true);
    try {
      await apiClient(`/users/${userId}`, { method: "DELETE" });
      return true;
    } catch {
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { deleteUser, loading };
};
