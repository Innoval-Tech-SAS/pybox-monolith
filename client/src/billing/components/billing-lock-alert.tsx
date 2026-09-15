import { Alert } from "@/ui/components/alert/alert";
import { LOCK_ALERT_VARIANT } from "../constants/billing-lock-alert-variant";
import type { BillingLockAlertProps } from "../types/props/billing-lock-alert-props";

export const BillingLockAlert: React.FC<BillingLockAlertProps> = ({ status }) => {
  if (status.lockStatus === "NINGUNO") return null;

  return (
    <Alert
      variant={LOCK_ALERT_VARIANT[status.lockStatus] ?? "info"}
      title={
        status.lockStatus === "BLOQUEADO"
          ? "Cuenta bloqueada"
          : status.lockStatus === "PAGO_REQUERIDO"
            ? "Pago requerido"
            : "Aviso de facturación"
      }
      message={status.message ?? "Hay una factura que requiere tu atención."}
    />
  );
};
