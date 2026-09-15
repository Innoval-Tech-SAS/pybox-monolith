import type { TicketCategory } from "@/types/support/support-types";

export interface StepCategoryProps {
  categories: TicketCategory[];
  loading: boolean;
  selectedCategory: TicketCategory | null;
  onSelectCategory: (category: TicketCategory) => void;
  canGoNext: boolean;
  onNext: () => void;
  onCancel: () => void;
}
