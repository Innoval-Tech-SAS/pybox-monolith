import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { UserSummary } from "@/types/users/user-types";

export const useUsers = (orgId?: string, includeDeleted = false) => {
  const { apiClient } = useApiClient();
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (orgId) params.set("org_id", orgId);
    if (includeDeleted) params.set("includeDeleted", "true");
    const query = params.toString();
    apiClient<UserSummary[]>(`/users${query ? `?${query}` : ""}`, { method: "GET" })
      .then((data) => setUsers(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [orgId, includeDeleted, apiClient]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return { users, setUsers, loading, refetch: fetchUsers };
};
