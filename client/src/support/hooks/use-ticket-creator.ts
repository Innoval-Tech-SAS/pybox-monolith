import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { UserDetail } from "@/types/users/user-types";

export const useTicketCreator = (userId: number | undefined) => {
  const { apiClient } = useApiClient();
  const [creator, setCreator] = useState<UserDetail | null>(null);

  const fetchCreator = useCallback(() => {
    if (!userId) return;
    apiClient(`/users/${userId}`, { method: "GET" })
      .then((data: UserDetail) => setCreator(data))
      .catch(() => setCreator(null));
  }, [apiClient, userId]);

  useEffect(() => {
    fetchCreator();
  }, [fetchCreator]);

  return { creator };
};
