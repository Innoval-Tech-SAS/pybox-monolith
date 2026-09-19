import type { CreditTypeOption } from "@/credits/types/credit-types";

export interface CalendarLegendProps {
  /** Tipos servidos por GET /credits/types; el front no declara la lista. */
  creditTypes: CreditTypeOption[];
}
