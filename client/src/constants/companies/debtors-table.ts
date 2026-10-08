import type { BadgeColor } from "@/types/props/badge-props";

export const DEBTOR_TYPE_COLOR: Record<string, BadgeColor> = {
  TITULAR: "primary",
  CO_DEUDOR: "light",
};

/** Etiqueta de display para el valor del enum DebtorType (valor snake_case en español). */
export const DEBTOR_TYPE_LABEL: Record<string, string> = {
  TITULAR: "Titular",
  CO_DEUDOR: "Co-deudor",
};
