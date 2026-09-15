import { useState } from "react";
import { useNavigate } from "react-router";
import { Tag, FileText } from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { StepSidebar } from "@/ui/components/wizard/step-sidebar";
import { getSession } from "@/auth/utils/auth-session-utils";
import { Scope } from "@/types/auth/role";
import { useTicketCategories } from "@/support/hooks/use-ticket-categories";
import { useTicketOrgs } from "@/support/hooks/use-ticket-orgs";
import { useCreateTicket } from "@/support/hooks/use-create-ticket";
import { useUploadTicketAttachments } from "@/support/hooks/use-upload-ticket-attachments";
import { StepCategory } from "@/support/components/create-ticket/step-category";
import { StepDetails } from "@/support/components/create-ticket/step-details";
import { ALLOWED_ATTACHMENT_TYPES } from "@/support/constants/ticket-attachment-types";
import type { TicketCategory } from "@/types/support/support-types";
import type { CreateTicketStepDef } from "@/support/types/create-ticket-step-def";

export const CreateTicketPage: React.FC = () => {
  const navigate = useNavigate();
  const session = getSession();
  const isGlobal = session?.scope === Scope.GLOBAL;

  const { categories, loading: loadingCats } = useTicketCategories();
  const { orgs, loading: loadingOrgs } = useTicketOrgs();
  const { createTicket, loading: submitting } = useCreateTicket();
  const { uploadAttachments } = useUploadTicketAttachments();

  const [step, setStep] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState<TicketCategory | null>(null);
  const [organizationId, setOrganizationId] = useState("");
  const [notes, setNotes] = useState("");
  const [attachments, setAttachments] = useState<File[]>([]);

  const addFiles = (files: FileList | null) => {
    if (!files) return;
    const valid = Array.from(files).filter((f) => {
      const ext = f.name.slice(f.name.lastIndexOf(".")).toLowerCase();
      return ALLOWED_ATTACHMENT_TYPES.includes(ext);
    });
    setAttachments((prev) => {
      const existing = new Set(prev.map((f) => f.name));
      return [...prev, ...valid.filter((f) => !existing.has(f.name))];
    });
  };

  const removeFile = (name: string) =>
    setAttachments((prev) => prev.filter((f) => f.name !== name));

  const stepDefs: CreateTicketStepDef[] = [
    { label: "Categoría", description: "Tipo de solicitud", icon: <Tag size={14} /> },
    { label: "Detalles", description: "Entidad y descripción", icon: <FileText size={14} /> },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCategory) return;
    if (!isGlobal && !organizationId) return;
    const ticket = await createTicket({
      organizationId: organizationId || undefined,
      title: selectedCategory.label,
      topic: selectedCategory.topic,
      notes: notes.trim(),
    });
    if (ticket) {
      await uploadAttachments(ticket.ticketNumber, attachments);
      navigate(`/cs/tickets/${ticket.ticketNumber}`);
    }
  };

  return (
    <ModuleBase
      pageTitle="Nuevo ticket"
      breadcrumbItems={[{ label: "Tickets", path: "/cs/tickets" }]}
    >
      <div className="flex gap-10">
        <aside className="hidden w-52 shrink-0 pt-1 lg:block">
          <StepSidebar steps={stepDefs} current={step} />
        </aside>
        <div className="hidden w-px self-stretch bg-gray-100 dark:bg-white/5 lg:block" />
        <div className="min-w-0 flex-1">
          {step === 1 ? (
            <StepCategory
              categories={categories}
              loading={loadingCats}
              selectedCategory={selectedCategory}
              onSelectCategory={setSelectedCategory}
              canGoNext={!!selectedCategory}
              onNext={() => setStep(2)}
              onCancel={() => navigate("/cs/tickets")}
            />
          ) : (
            <StepDetails
              selectedCategory={selectedCategory}
              isGlobal={isGlobal}
              orgs={orgs}
              loadingOrgs={loadingOrgs}
              organizationId={organizationId}
              onOrganizationIdChange={setOrganizationId}
              notes={notes}
              onNotesChange={setNotes}
              attachments={attachments}
              onAddFiles={addFiles}
              onRemoveFile={removeFile}
              submitting={submitting}
              onSubmit={handleSubmit}
              onBack={() => setStep(1)}
            />
          )}
        </div>
      </div>
    </ModuleBase>
  );
};
