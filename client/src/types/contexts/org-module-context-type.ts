import type { OrgSummary } from "@/types/companies/company-types";

export interface OrgModuleContextType {
  orgId: string;
  orgName: string;
  orgs: OrgSummary[];
  loading: boolean;
  buildOrgPath: (path: string, extraParams?: Record<string, string>) => string;
}
