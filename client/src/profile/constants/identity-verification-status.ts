import type { IdentityVerificationStatus } from "@/types/auth/user";

export const IDENTITY_VERIFICATION_CONFIG: Record<IdentityVerificationStatus, { label: string; classes: string }> = {
  APROBADO: { label: "Verificada", classes: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400" },
  PENDIENTE: { label: "En revisión", classes: "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400" },
  DENEGADO: { label: "Rechazada", classes: "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400" },
  NO_ENVIADO: { label: "Sin enviar", classes: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400" },
};
