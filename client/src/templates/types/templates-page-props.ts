import type { Template, TemplatePreviewResponse } from "@/types/templates/template-types";

export interface PreviewModalProps {
  isOpen: boolean;
  template: Template | null;
  onClose: () => void;
  onPreview: (id: string, sub: Record<string, string>) => Promise<TemplatePreviewResponse | null>;
}

export interface SendModalProps {
  isOpen: boolean;
  template: Template | null;
  saving: boolean;
  onClose: () => void;
  onSend: (id: string, to: string, subject: string, sub: Record<string, string>) => Promise<void>;
}
