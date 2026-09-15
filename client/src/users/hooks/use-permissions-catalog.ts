import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { PermissionCatalogEntry } from "@/types/users/permission-types";

export const usePermissionsCatalog = () => {
  const { apiClient } = useApiClient();
  const [catalog, setCatalog] = useState<PermissionCatalogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    apiClient<PermissionCatalogEntry[]>("/permissions")
      .then(setCatalog)
      .catch(() => setCatalog([]))
      .finally(() => setLoading(false));
  }, []);

  return { catalog, loading };
};
