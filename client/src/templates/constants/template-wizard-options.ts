import type { WizardStep } from "@/types/props/wizard-form-props";
import type { TemplateChannel, TemplateStatus } from "@/types/templates/template-types";

export type ChannelIconName = "mail" | "sms" | "whatsapp" | "call" | "call-ia";

export const CHANNEL_ICON_BY_NAME: Record<TemplateChannel, ChannelIconName> = {
  EMAIL: "mail",
  SMS: "sms",
  WHATSAPP: "whatsapp",
  CALL: "call",
  CALL_IA: "call-ia",
};

// Canales sin diseñador implementado en el wizard todavía.
export const UNAVAILABLE_CHANNELS: readonly TemplateChannel[] = ["CALL", "CALL_IA"];

export const STATUS_OPTIONS: { value: TemplateStatus; label: string }[] = [
  { value: "BORRADOR", label: "Borrador" },
  { value: "ACTIVA", label: "Activa" },
  { value: "INACTIVA", label: "Inactiva" },
];

export const TEMPLATE_WIZARD_STEPS: readonly WizardStep[] = [
  { title: "Canal", description: "Elige el canal de envío de la plantilla" },
  { title: "Información", description: "Datos generales de la plantilla" },
  { title: "Diseño", description: "Diseña el contenido de la plantilla" },
  { title: "Vista previa", description: "Revisa y guarda la plantilla" },
];

export const CHANNEL_CHAR_LIMITS: Partial<Record<TemplateChannel, number>> = {
  SMS: 160,
  WHATSAPP: 1024,
};
