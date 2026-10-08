import type { BadgeColor } from "@/types/props/badge-props";

export const DOCUMENT_CATEGORY_COLOR: Record<string, BadgeColor> = {
  IDENTIDAD: "info",
  COMPROBANTE_PAGO: "success",
  CONTRATO: "primary",
  OTRO: "light",
  FISCAL: "warning",
  MERCANTIL: "warning",
  REPRESENTANTE_LEGAL: "info",
};
