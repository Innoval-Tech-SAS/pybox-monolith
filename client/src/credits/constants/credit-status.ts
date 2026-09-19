import type { BadgeColor } from "@/types/props/badge-props";

/** Estado derivado del crédito: no viene como enum del backend, se calcula a partir de
 * `isActive` + `settlementRequested` (ver CreditWithPayments en credits/types/credit-types.ts). */
export type CreditStatus = "ACTIVE" | "SETTLEMENT_REQUESTED" | "INACTIVE";

export const resolveCreditStatus = (isActive: boolean, settlementRequested: boolean): CreditStatus => {
  if (!isActive) return "INACTIVE";
  if (settlementRequested) return "SETTLEMENT_REQUESTED";
  return "ACTIVE";
};

export const CREDIT_STATUS_LABELS: Record<CreditStatus, string> = {
  ACTIVE: "Activo",
  SETTLEMENT_REQUESTED: "Baja en revisión",
  INACTIVE: "Dado de baja",
};

export const CREDIT_STATUS_COLORS: Record<CreditStatus, BadgeColor> = {
  ACTIVE: "success",
  SETTLEMENT_REQUESTED: "warning",
  INACTIVE: "light",
};
