import type { PortfolioDebtor } from "@/types/companies/portfolio-debtor-types";

export interface DebtorsTableProps {
  orgId: string;
  portfolioId: string;
  debtors: PortfolioDebtor[];
  total: number;
  page: number;
  pages: number;
  search: string;
  loading: boolean;
  onSearch: (value: string) => void;
  onPageChange: (page: number) => void;
}
