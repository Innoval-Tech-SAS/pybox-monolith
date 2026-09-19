import type { WhatsAppTemplateCategory } from "@/types/templates/whatsapp-template-types";

export interface WhatsAppTemplateFormState {
  language: string;
  category: WhatsAppTemplateCategory;
  headerText: string;
  bodyText: string;
  footerText: string;
}
