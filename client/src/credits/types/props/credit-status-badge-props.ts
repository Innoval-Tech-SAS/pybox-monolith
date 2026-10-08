import type { BadgeSize } from "@/types/props/badge-props";

export interface CreditStatusBadgeProps {
  isActive: boolean;
  settlementRequested: boolean;
  size?: BadgeSize;
}
