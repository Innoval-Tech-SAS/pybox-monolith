import type { ReactNode } from "react";

export type RepresentativeMode = "self" | "select" | "create";

export interface OrgSummary {
  id: string;
  name: string;
  description?: string;
  country?: string;
  fiscalDocumentType?: string;
  fiscalDocumentNumber?: string;
}

export interface OrgModule {
  key: string;
  title: string;
  description: string;
  icon: ReactNode;
  gradient: string;
  path: string | null;
}

export interface CreatePortfolioResult {
  total_rows: number;
  processed_rows: number;
  failed_rows: number;
  portfolio_id: string;
  errors: string[];
}
