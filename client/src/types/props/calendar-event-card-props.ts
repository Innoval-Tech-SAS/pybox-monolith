import type { FinancialCalendarEvent } from "@/credits/types/financial-calendar-types";

export interface CalendarEventCardProps {
  event: FinancialCalendarEvent;
  /** Etiqueta legible del tipo de crédito, servida por GET /credits/types. */
  creditTypeLabel: string;
}
