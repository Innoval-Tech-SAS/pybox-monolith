import type { CreditWithPayments } from "@/credits/types/credit-types";

export interface CalendarProps {
  credits: CreditWithPayments[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  /**
   * Cómo nombra el modal de detalle a la acreedora. Se propaga tal cual: el home del
   * titular pasa "Entidad", la pantalla de la organización usa el valor por defecto.
   */
  entityLabel?: string;
}
