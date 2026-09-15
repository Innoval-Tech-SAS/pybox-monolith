import type { WizardStep } from "@/types/props/wizard-form-props";

export const BULK_SEND_WIZARD_STEPS: readonly WizardStep[] = [
  { title: "Destino", description: "Portafolio y canal de envío" },
  { title: "Mensaje", description: "Contenido a enviar a los destinatarios" },
  { title: "Archivo", description: "Sube el archivo con los destinatarios" },
  { title: "Confirmar", description: "Revisa el envío antes de confirmarlo" },
];
