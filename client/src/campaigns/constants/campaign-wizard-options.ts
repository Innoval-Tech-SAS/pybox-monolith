import type { WizardStep } from "@/types/props/wizard-form-props";

export const CAMPAIGN_WIZARD_STEPS: readonly WizardStep[] = [
  { title: "Detalles", description: "Nombre y descripción de la campaña" },
  { title: "Canal", description: "Por dónde se enviará la campaña" },
  { title: "Mensaje", description: "Destinatarios y contenido a enviar" },
  { title: "Programación", description: "Cuándo se enviará la campaña" },
];

export const SCHEDULE_FREQUENCY_OPTIONS = [
  {
    value: "INMEDIATO" as const,
    label: "Envío inmediato",
    helper: "Se envía apenas confirmes la campaña.",
  },
  {
    value: "UNA_VEZ" as const,
    label: "Envío único",
    helper: "Se envía una sola vez en la fecha que elijas.",
  },
  {
    value: "PERIODICO" as const,
    label: "Envío recurrente",
    helper: "Se repite automáticamente según la frecuencia.",
  },
];
