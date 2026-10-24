export interface MyStatement {
  id: string;
  debtorId: string;
  portfolioId: string;
  organizationId: string;
  organizationName: string;
  creditId: string | null;
  creditNumber: string | null;
  cutoffDate: string;
  documentId: string;
  createdAt: string;
}

export interface MyStatementListResponse {
  items: MyStatement[];
  total: number;
}
