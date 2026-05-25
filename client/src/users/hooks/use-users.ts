import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { UserSummary } from "@/types/users/user-types";

export const useUsers = (orgId?: string) => {
  const { apiClient } = useApiClient();
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = useCallback(() => {
    setLoading(true);
    const url = orgId ? `/users?org_id=${orgId}` : "/users";
    apiClient(url, { method: "GET" })
      .then((data: UserSummary[]) => setUsers(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [orgId]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return { users, setUsers, loading, refetch: fetchUsers };
};
