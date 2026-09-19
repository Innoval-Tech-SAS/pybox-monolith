import type { WhatsAppTemplateFormState } from "@/templates/types/whatsapp-template-form-state";

export interface StepWhatsAppInfoProps {
  name: string;
  whatsappForm: WhatsAppTemplateFormState;
  onNameChange: (value: string) => void;
  onWhatsAppChange: <K extends keyof WhatsAppTemplateFormState>(
    key: K,
  ) => (value: WhatsAppTemplateFormState[K]) => void;
}
