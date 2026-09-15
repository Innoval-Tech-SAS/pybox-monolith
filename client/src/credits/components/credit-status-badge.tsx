import { Badge } from "@/ui/components/badge";
import { CREDIT_STATUS_COLORS, CREDIT_STATUS_LABELS, resolveCreditStatus } from "@/credits/constants/credit-status";
import type { CreditStatusBadgeProps } from "@/credits/types/props/credit-status-badge-props";

export const CreditStatusBadge: React.FC<CreditStatusBadgeProps> = ({ isActive, settlementRequested, size = "sm" }) => {
  const status = resolveCreditStatus(isActive, settlementRequested);
  return (
    <Badge color={CREDIT_STATUS_COLORS[status]} variant="light" size={size}>
      {CREDIT_STATUS_LABELS[status]}
    </Badge>
  );
};
