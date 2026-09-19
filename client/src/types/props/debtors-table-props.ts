import type { PortfolioDebtor } from "@/types/companies/portfolio-debtor-types";
import type { SortOrder } from "@/ui/components/table/sort-icon";
import type { DebtorSortKey } from "@/companies/hooks/use-portfolio-debtors";

export interface DebtorsTableProps {
  portfolioId: string;
  debtors: PortfolioDebtor[];
  total: number;
  page: number;
  pages: number;
  search: string;
  pageSize: number;
  sortKey: DebtorSortKey;
  sortOrder: SortOrder;
  loading: boolean;
  onSearch: (value: string) => void;
  onPageSizeChange: (size: number) => void;
  onSort: (key: DebtorSortKey) => void;
  onPageChange: (page: number) => void;
}
