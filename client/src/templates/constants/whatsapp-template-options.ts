import type { SelectOption } from "@/types/props/select-props";
import type { BadgeColor } from "@/types/props/badge-props";
import type { WhatsAppTemplateCategory } from "@/types/templates/whatsapp-template-types";

// Límites de Meta para plantillas de texto.
export const WHATSAPP_BODY_MAX_CHARS = 1024;
export const WHATSAPP_HEADER_MAX_CHARS = 60;
export const WHATSAPP_FOOTER_MAX_CHARS = 60;

export const WHATSAPP_DEFAULT_LANGUAGE = "es";
export const WHATSAPP_DEFAULT_CATEGORY: WhatsAppTemplateCategory = "UTILITY";

// Códigos de idioma tal como los define Meta (no son locales BCP-47 libres).
export const WHATSAPP_LANGUAGE_OPTIONS: SelectOption[] = [
  { value: "es", label: "Español" },
  { value: "es_MX", label: "Español (México)" },
  { value: "es_AR", label: "Español (Argentina)" },
  { value: "es_ES", label: "Español (España)" },
  { value: "en_US", label: "Inglés (Estados Unidos)" },
  { value: "pt_BR", label: "Portugués (Brasil)" },
];

// AUTHENTICATION queda fuera: Meta la trata con un formato propio (OTP), sin cuerpo libre.
export const WHATSAPP_CATEGORY_OPTIONS: SelectOption[] = [
  { value: "UTILITY", label: "Utilidad (recordatorios, estados de cuenta, confirmaciones)" },
  { value: "MARKETING", label: "Marketing (promociones, ofertas)" },
];

export const WHATSAPP_CATEGORY_LABELS: Record<WhatsAppTemplateCategory, string> = {
  UTILITY: "Utilidad",
  MARKETING: "Marketing",
  AUTHENTICATION: "Autenticación",
};

export const WHATSAPP_META_STATUS_LABELS: Record<string, string> = {
  PENDING: "Pendiente en Meta",
  IN_APPEAL: "En apelación",
  APPROVED: "Aprobada",
  REJECTED: "Rechazada",
  PAUSED: "Pausada",
  DISABLED: "Deshabilitada",
};

export const WHATSAPP_META_STATUS_COLORS: Record<string, BadgeColor> = {
  PENDING: "warning",
  IN_APPEAL: "warning",
  APPROVED: "success",
  REJECTED: "error",
  PAUSED: "error",
  DISABLED: "error",
};
