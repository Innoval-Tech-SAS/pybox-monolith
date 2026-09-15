import type { TicketCategory, TicketOrg } from "@/types/support/support-types";

export interface StepDetailsProps {
  selectedCategory: TicketCategory | null;
  isGlobal: boolean;
  orgs: TicketOrg[];
  loadingOrgs: boolean;
  organizationId: string;
  onOrganizationIdChange: (id: string) => void;
  notes: string;
  onNotesChange: (notes: string) => void;
  attachments: File[];
  onAddFiles: (files: FileList | null) => void;
  onRemoveFile: (name: string) => void;
  submitting: boolean;
  onSubmit: (e: React.FormEvent) => void;
  onBack: () => void;
}
