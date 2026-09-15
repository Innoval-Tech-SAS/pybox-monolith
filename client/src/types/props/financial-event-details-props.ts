import type { FinancialCalendarEvent } from "@/credits/types/financial-calendar-types";

export interface FinancialEventDetailsProps {
  event: FinancialCalendarEvent;
  onClose: () => void;
  /** Se llama tras una solicitud exitosa (reprogramación / validación) para refrescar el calendario. */
  onActionDone?: () => void;
  /**
   * Cómo se nombra a la acreedora. El titular (USER/SELF) lee "Entidad"; la pantalla
   * de la organización, que comparte este modal, sigue leyendo "Empresa".
   */
  entityLabel?: string;
}
