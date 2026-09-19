export const ORG_VERIFICATION_STYLES: Record<
  string,
  { label: string; classes: string }
> = {
  pending: {
    label: "Verificación pendiente",
    classes:
      "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400",
  },
  approved: {
    label: "Verificada",
    classes:
      "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  },
  denied: {
    label: "Verificación denegada",
    classes:
      "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400",
  },
};
