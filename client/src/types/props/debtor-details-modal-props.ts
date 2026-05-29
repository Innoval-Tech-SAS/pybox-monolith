import type { PortfolioDebtor } from "@/types/companies/portfolio-debtor-types";

export interface DebtorDetailsModalProps {
  debtor: PortfolioDebtor | null;
  portfolioId: string;
  onClose: () => void;
}
