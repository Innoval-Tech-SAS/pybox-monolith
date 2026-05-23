import type { OrgSummary } from "@/types/companies/company-types";

export interface OrgCardProps {
  org: OrgSummary;
  onClick: (id: string) => void;
}
