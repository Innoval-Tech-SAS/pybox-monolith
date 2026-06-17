import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { UserDetail } from "@/types/users/user-types";

export const useTicketAssignee = (userId: string | undefined) => {
  const { apiClient } = useApiClient();
  const [assignee, setAssignee] = useState<UserDetail | null>(null);

  const fetchAssignee = useCallback(() => {
    if (!userId) return;
    apiClient(`/users/${userId}`, { method: "GET" })
      .then((data: UserDetail) => setAssignee(data))
      .catch(() => setAssignee(null));
  }, [apiClient, userId]);

  useEffect(() => {
    fetchAssignee();
  }, [fetchAssignee]);

  return { assignee };
};
