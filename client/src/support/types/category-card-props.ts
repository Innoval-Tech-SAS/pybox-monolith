import type { TicketCategory } from "@/types/support/support-types";

export interface CategoryCardProps {
  category: TicketCategory;
  selected: boolean;
  onSelect: () => void;
}
