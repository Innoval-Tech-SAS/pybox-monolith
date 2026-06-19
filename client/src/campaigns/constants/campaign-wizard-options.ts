import type { WizardStep } from "@/types/props/wizard-form-props";

export const CAMPAIGN_WIZARD_STEPS: readonly WizardStep[] = [
  { title: "Detalles", description: "Nombre, descripción y canal de envío" },
  { title: "Mensaje", description: "Destinatarios y contenido a enviar" },
  { title: "Programación", description: "Cuándo se enviará la campaña" },
];

export const SCHEDULE_FREQUENCY_OPTIONS = [
  {
    value: "immediate" as const,
    label: "Envío inmediato",
    helper: "Se envía apenas confirmes la campaña.",
  },
  {
    value: "once" as const,
    label: "Envío único",
    helper: "Se envía una sola vez en la fecha que elijas.",
  },
  {
    value: "periodic" as const,
    label: "Envío recurrente",
    helper: "Se repite automáticamente según la frecuencia.",
  },
];
