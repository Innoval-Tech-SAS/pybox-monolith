import type { OrgVerificationStatus } from "@/types/auth/user";

export const ORG_VERIFICATION_CONFIG: Record<OrgVerificationStatus, { label: string; classes: string }> = {
  APROBADO: { label: "Verificada", classes: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400" },
  PENDIENTE: { label: "Pendiente", classes: "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400" },
  DENEGADO: { label: "Rechazada", classes: "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400" },
};
