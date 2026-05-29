import type { ReactNode } from "react";

export type RepresentativeMode = "self" | "select" | "create";

export interface OrgSummary {
  id: string;
  name: string;
  description?: string;
  country?: string;
  fiscalDocumentType?: string;
  fiscalDocumentNumber?: string;
  verificationStatus?: string;
}

export interface OrganizationDetail {
  id: string;
  name: string;
  description: string | null;
  country: string | null;
  fiscalDocumentType: string | null;
  fiscalDocumentNumber: string | null;
  fiscalDocumentFile: string | null;
  mercantileDocumentType: string | null;
  mercantileDocumentFile: string | null;
  representativeDocumentFile: string | null;
  verificationStatus: string | null;
  createdAt: string;
  updatedAt: string | null;
}

export interface OrgModule {
  key: string;
  title: string;
  description: string;
  icon: ReactNode;
  gradient: string;
  path: string | null;
  requiredPermission?: string;
  adminOnly?: boolean;
  requiresVerification?: boolean;
}

export interface CreatePortfolioResult {
  total_rows: number;
  processed_rows: number;
  failed_rows: number;
  portfolio_id: string;
  errors: string[];
}
