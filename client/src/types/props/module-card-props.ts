import type { OrgModule } from "@/types/companies/company-types";

export interface ModuleCardProps {
  module: OrgModule;
  orgId: string;
  id?: string;
}
