import type { CreditWithPayments } from "@/credits/types/credit-types";

export interface FinancialCalendarProps {
  credits: CreditWithPayments[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}
