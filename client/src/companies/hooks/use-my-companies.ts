import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { OrgSummary } from "@/types/companies/company-types";

export const useMyCompanies = () => {
  const { apiClient } = useApiClient();
  const [orgs, setOrgs] = useState<OrgSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient("/organizations/", { method: "GET" })
      .then((data: OrgSummary[]) => setOrgs(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return { orgs, loading };
};
