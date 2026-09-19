import type { LucideIcon } from "lucide-react";

export type RepresentativeMode = "self" | "select" | "create";

/** Opción de sector servida por GET /organizations/sectors. El front no mantiene la lista. */
export interface EntitySectorOption {
  value: string;
  label: string;
}

export interface OrgSummary {
  id: string;
  name: string;
  sector?: string;
  description?: string;
  country?: string;
  fiscalDocumentType?: string;
  fiscalDocumentNumber?: string;
  verificationStatus?: string;
  logoUrl?: string | null;
}

export interface OrganizationDetail {
  id: string;
  name: string;
  sector: string;
  description: string | null;
  country: string | null;
  fiscalDocumentType: string | null;
  fiscalDocumentNumber: string | null;
  fiscalDocumentFile: string | null;
  mercantileDocumentType: string | null;
  mercantileDocumentFile: string | null;
  representativeDocumentFile: string | null;
  logoUrl: string | null;
  verificationStatus: string | null;
  createdAt: string;
  updatedAt: string | null;
}

export interface OrgModule {
  key: string;
  title: string;
  description: string;
  icon: LucideIcon;
  gradient: string;
  path: string | null;
  requiredPermission?: string;
  adminOnly?: boolean;
  requiresVerification?: boolean;
}

export interface CreatePortfolioResult {
  totalRows: number;
  processedRows: number;
  failedRows: number;
  portfolioId: string;
  errors: string[];
}
