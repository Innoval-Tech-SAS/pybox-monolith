import { useCallback } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { OrgSummary } from "@/types/companies/company-types";

export const useMyCompanies = () => {
  const { apiClient } = useApiClient();

  const fetchOrgs = useCallback(
    () => apiClient("/organizations/", { method: "GET" }) as Promise<OrgSummary[]>,
    [apiClient],
  );

  const { data: orgs, loading, error, refetch } = useAsyncResource<OrgSummary[]>(fetchOrgs, []);

  return { orgs, loading, error, refetch };
};
