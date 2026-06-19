import { useMemo } from "react";
import { useSearchParams } from "react-router";
import type { ChildrenProps } from "@/types/props/provider-props";
import { useMyCompanies } from "@/companies/hooks/use-my-companies";
import { OrgModuleContext } from "../org-module-context";

export const OrgModuleProvider: React.FC<ChildrenProps> = ({ children }) => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const { orgs, loading } = useMyCompanies();

  const orgName = useMemo(
    () => orgs.find((o) => o.id === orgId)?.name ?? "",
    [orgs, orgId],
  );

  const buildOrgPath = useMemo(
    () => (path: string, extraParams?: Record<string, string>) => {
      const params = new URLSearchParams();
      if (orgId) params.set("org", orgId);
      if (extraParams) {
        for (const [key, value] of Object.entries(extraParams)) {
          if (value) params.set(key, value);
        }
      }
      const qs = params.toString();
      return qs ? `${path}?${qs}` : path;
    },
    [orgId],
  );

  return (
    <OrgModuleContext.Provider value={{ orgId, orgName, orgs, loading, buildOrgPath }}>
      {children}
    </OrgModuleContext.Provider>
  );
};
