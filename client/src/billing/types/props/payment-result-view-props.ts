import React from "react";

export interface PaymentResultViewProps {
  /** Estado del pago: PaymentResultStatus, o el `bold-tx-status` crudo del redirect de Bold. */
  status: string;
  reference?: string | null;
  /** Acciones (botones) que se renderizan debajo del mensaje. */
  children?: React.ReactNode;
}
