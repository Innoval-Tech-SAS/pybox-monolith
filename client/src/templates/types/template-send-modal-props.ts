import type { Template } from "@/types/templates/template-types";

export interface TemplateSendModalProps {
  isOpen: boolean;
  template: Template | null;
  saving: boolean;
  onClose: () => void;
  /** Devuelve `true` si el envío tuvo éxito -- el modal solo se cierra en ese caso. */
  onSend: (id: string, to: string, subject: string, sub: Record<string, string>) => Promise<boolean>;
}
