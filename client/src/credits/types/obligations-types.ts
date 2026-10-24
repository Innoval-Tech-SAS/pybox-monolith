/** Resumen del mes en curso, derivado de los créditos del titular. */
export interface ObligationsSummary {
  /** Suma de las cuotas con vencimiento en el mes. */
  monthTotal: number;
  /** Suma de las cuotas del mes que todavía no se pagaron. */
  dueTotal: number;
  /** Saldo de capital en mora acumulado. */
  overdueTotal: number;
  /** Entidades distintas entre las que se reparten las obligaciones. */
  entityCount: number;
  currencyCode: string;
  /** Mes y año en texto, p. ej. "mayo de 2024". */
  periodLabel: string;
}

/** Fila de la tabla "Detalle de obligaciones". */
export interface ObligationRow {
  creditId: string;
  creditNumber: string;
  /** Código del tipo de crédito; la etiqueta la sirve GET /credits/types. */
  creditType: string;
  entityName: string;
  currencyCode: string;
  nextDueDate: string | null;
  installmentAmount: number;
  /** Código de estado del pago (enum PaymentStatus) o null si no hay cuota pendiente. */
  status: string | null;
  isOverdue: boolean;
}
