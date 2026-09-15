import type { Portfolio } from "@/types/companies/portfolio-types";

export interface PortfolioCardProps {
  portfolio: Portfolio;
  onClick: () => void;
}
