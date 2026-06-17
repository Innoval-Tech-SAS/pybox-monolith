import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { UserPermissionEntry, UserPermissionList } from "@/types/users/permission-types";

export const useUserPermissions = (orgId: string, userId: string) => {
  const { apiClient } = useApiClient();
  const [permissions, setPermissions] = useState<UserPermissionEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPermissions = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiClient<UserPermissionList>(
        `/organizations/${orgId}/members/${userId}/permissions`
      );
      setPermissions(data.permissions);
    } catch {
      setPermissions([]);
    } finally {
      setLoading(false);
    }
  }, [orgId, userId]);

  useEffect(() => { fetchPermissions(); }, [fetchPermissions]);

  const assignPermission = async (name: string, effect: "GRANT" | "REVOKE"): Promise<boolean> => {
    try {
      await apiClient(`/organizations/${orgId}/members/${userId}/permissions`, {
        method: "PUT",
        body: JSON.stringify({ name, effect }),
      });
      await fetchPermissions();
      return true;
    } catch {
      return false;
    }
  };

  const removePermission = async (name: string): Promise<boolean> => {
    try {
      await apiClient(`/organizations/${orgId}/members/${userId}/permissions/${name}`, {
        method: "DELETE",
      });
      await fetchPermissions();
      return true;
    } catch {
      return false;
    }
  };

  return { permissions, loading, assignPermission, removePermission, refetch: fetchPermissions };
};
