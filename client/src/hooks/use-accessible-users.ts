import { useState, useEffect } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { UserSummary } from "@/types/users/user-types";

export const useAccessibleUsers = () => {
  const { apiClient } = useApiClient();
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient<UserSummary[]>("/users", { method: "GET" })
      .then((data) => { if (data) setUsers(data); })
      .catch(() => setUsers([]))
      .finally(() => setLoading(false));
  }, [apiClient]);

  return { users, loading };
};
