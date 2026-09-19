import { useState, useEffect } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { UserSummary } from "@/types/users/user-types";

export const useAccessibleUsers = () => {
  const { apiClient } = useApiClient();
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient("/users", { method: "GET" })
      .then((data: UserSummary[]) => { if (data) setUsers(data); })
      .catch(() => setUsers([]))
      .finally(() => setLoading(false));
  }, []);

  return { users, loading };
};
