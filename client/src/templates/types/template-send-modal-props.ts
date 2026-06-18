import type { Template } from "@/types/templates/template-types";

export interface TemplateSendModalProps {
  isOpen: boolean;
  template: Template | null;
  saving: boolean;
  onClose: () => void;
  onSend: (id: string, to: string, subject: string, sub: Record<string, string>) => Promise<void>;
}
