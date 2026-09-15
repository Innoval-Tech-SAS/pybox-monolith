import type { OrgModule } from "@/types/companies/company-types";

export interface ModuleCardProps {
  module: OrgModule;
  orgId: string;
  portfolioId?: string;
  id?: string;
}
