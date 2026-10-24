import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { UserDetail } from "@/types/users/user-types";

export const useUser = (userId: string | undefined) => {
  const { apiClient } = useApiClient();
  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    setNotFound(false);
    apiClient<UserDetail>(`/users/${userId}`, { method: "GET" })
      .then((data) => setUser(data))
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [userId, apiClient]);

  return { user, loading, notFound };
};
