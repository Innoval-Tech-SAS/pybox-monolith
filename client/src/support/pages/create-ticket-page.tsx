import { useState } from "react";
import { useNavigate } from "react-router";
import {
  Bug,
  Sparkles,
  LockKeyhole,
  HelpCircle,
  FileCheck,
  MoreHorizontal,
  Tag,
  FileText,
  CheckCircle,
  Image,
  Paperclip,
  X,
  type LucideIcon,
} from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { getSession } from "@/auth/utils/auth-session-utils";
import { Scope } from "@/types/auth/role";
import { useTicketCategories } from "@/support/hooks/use-ticket-categories";
import { useTicketOrgs } from "@/support/hooks/use-ticket-orgs";
import { useCreateTicket } from "@/support/hooks/use-create-ticket";
import { useUploadTicketAttachments } from "@/support/hooks/use-upload-ticket-attachments";
import type { TicketCategory } from "@/types/support/support-types";

const ALLOWED_TYPES = [".doc", ".jpg", ".jpeg", ".png"];
const IMAGE_EXTS = new Set([".jpg", ".jpeg", ".png"]);

const FileIcon: React.FC<{ name: string }> = ({ name }) => {
  const ext = name.slice(name.lastIndexOf(".")).toLowerCase();
  return IMAGE_EXTS.has(ext) ? (
    <Image size={14} className="text-brand-500" />
  ) : (
    <FileText size={14} className="text-gray-500 dark:text-gray-400" />
  );
};

const ICON_MAP: Record<string, LucideIcon> = {
  "bug": Bug,
  "sparkles": Sparkles,
  "lock-keyhole": LockKeyhole,
  "help-circle": HelpCircle,
  "file-check": FileCheck,
  "more-horizontal": MoreHorizontal,
};

const INPUT_BASE =
  "w-full rounded-lg border appearance-none px-4 py-2.5 text-sm shadow-theme-xs placeholder:text-gray-400 focus:outline-hidden focus:ring-3 bg-transparent text-gray-800 border-gray-300 focus:border-brand-300 focus:ring-brand-500/20 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:border-gray-700 dark:focus:border-brand-800";

interface StepDef {
  label: string;
  description: string;
  icon: React.ReactNode;
}

const StepSidebar: React.FC<{ steps: StepDef[]; current: number }> = ({ steps, current }) => (
  <div className="flex flex-col gap-0">
    {steps.map((s, i) => {
      const n = i + 1;
      const done = n < current;
      const active = n === current;
      return (
        <div key={n} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div
              className={`flex size-9 shrink-0 items-center justify-center rounded-full border-2 text-sm font-semibold transition-all ${
                done
                  ? "border-brand-500 bg-brand-500 text-white"
                  : active
                    ? "border-brand-500 bg-white text-brand-600 dark:bg-gray-900"
                    : "border-gray-200 bg-white text-gray-400 dark:border-gray-700 dark:bg-gray-900"
              }`}
            >
              {done ? <CheckCircle size={16} /> : s.icon}
            </div>
            {i < steps.length - 1 && (
              <div
                className={`my-1 min-h-10 w-px flex-1 transition-colors ${
                  done ? "bg-brand-500" : "bg-gray-200 dark:bg-gray-700"
                }`}
              />
            )}
          </div>
          <div className="pb-8">
            <p
              className={`text-sm font-semibold leading-9 ${
                active
                  ? "text-gray-800 dark:text-white/90"
                  : done
                    ? "text-brand-600 dark:text-brand-400"
                    : "text-gray-400 dark:text-gray-600"
              }`}
            >
              {s.label}
            </p>
            <p
              className={`-mt-1 text-xs ${
                active || done
                  ? "text-gray-500 dark:text-gray-400"
                  : "text-gray-300 dark:text-gray-700"
              }`}
            >
              {s.description}
            </p>
          </div>
        </div>
      );
    })}
  </div>
);

interface CategoryCardProps {
  category: TicketCategory;
  selected: boolean;
  onSelect: () => void;
}

const CategoryCard: React.FC<CategoryCardProps> = ({ category, selected, onSelect }) => {
  const Icon = ICON_MAP[category.icon] ?? HelpCircle;
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`flex items-start gap-3 rounded-xl border p-4 text-left transition-all ${
        selected
          ? "border-brand-500 bg-brand-50 dark:border-brand-400 dark:bg-brand-500/10"
          : "border-gray-200 bg-white hover:border-brand-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-white/3 dark:hover:border-brand-600 dark:hover:bg-white/5"
      }`}
    >
      <div
        className={`mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg ${
          selected
            ? "bg-brand-100 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400"
            : "bg-gray-100 text-gray-500 dark:bg-white/5 dark:text-gray-400"
        }`}
      >
        <Icon size={17} />
      </div>
      <div>
        <p
          className={`text-sm font-semibold ${
            selected ? "text-brand-700 dark:text-brand-300" : "text-gray-800 dark:text-white/90"
          }`}
        >
          {category.label}
        </p>
        <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{category.description}</p>
      </div>
    </button>
  );
};

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
      return ALLOWED_TYPES.includes(ext);
    });
    setAttachments((prev) => {
      const existing = new Set(prev.map((f) => f.name));
      return [...prev, ...valid.filter((f) => !existing.has(f.name))];
    });
  };

  const removeFile = (name: string) =>
    setAttachments((prev) => prev.filter((f) => f.name !== name));

  const stepDefs: StepDef[] = [
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
      caseType: selectedCategory.caseType,
      notes: notes.trim(),
    });
    if (ticket) {
      await uploadAttachments(ticket.ticketNumber, attachments);
      navigate(`/cs/tickets/${ticket.ticketNumber}`);
    }
  };

  const SelectedCategoryIcon = selectedCategory ? (ICON_MAP[selectedCategory.icon] ?? HelpCircle) : null;

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">¿En qué podemos ayudarte?</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Selecciona la categoría que mejor describe tu situación.
        </p>
      </div>

      {loadingCats ? (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-20 animate-pulse rounded-xl bg-gray-100 dark:bg-white/5" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
          {categories.map((cat) => (
            <CategoryCard
              key={cat.label}
              category={cat}
              selected={selectedCategory?.label === cat.label}
              onSelect={() => setSelectedCategory(cat)}
            />
          ))}
        </div>
      )}

      <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
        <button
          type="button"
          onClick={() => navigate("/cs/tickets")}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3"
        >
          Cancelar
        </button>
        <button
          type="button"
          disabled={!selectedCategory}
          onClick={() => setStep(2)}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:opacity-50"
        >
          Continuar
        </button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">Detalles del ticket</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Completa la información de tu solicitud.
        </p>
      </div>

      {selectedCategory && SelectedCategoryIcon && (
        <div className="flex items-center gap-3 rounded-xl border border-brand-200 bg-brand-50 px-4 py-3 dark:border-brand-500/30 dark:bg-brand-500/10">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-brand-100 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400">
            <SelectedCategoryIcon size={15} />
          </div>
          <div>
            <p className="text-xs text-brand-500 dark:text-brand-400">Categoría seleccionada</p>
            <p className="text-sm font-semibold text-brand-700 dark:text-brand-300">{selectedCategory.label}</p>
          </div>
        </div>
      )}

      {!isGlobal ? (
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Entidad <span className="text-error-500">*</span>
          </label>
          {loadingOrgs ? (
            <div className="h-10 animate-pulse rounded-lg bg-gray-100 dark:bg-white/5" />
          ) : (
            <select
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              required
              className={INPUT_BASE}
            >
              <option value="">Seleccionar entidad...</option>
              {orgs.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </select>
          )}
        </div>
      ) : orgs.length > 0 ? (
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Entidad <span className="font-normal text-gray-400">(opcional)</span>
          </label>
          {loadingOrgs ? (
            <div className="h-10 animate-pulse rounded-lg bg-gray-100 dark:bg-white/5" />
          ) : (
            <select
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              className={INPUT_BASE}
            >
              <option value="">Sin entidad específica</option>
              {orgs.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </select>
          )}
        </div>
      ) : null}

      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Descripción <span className="text-error-500">*</span>
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Describe el problema con el mayor detalle posible: pasos para reproducirlo, mensajes de error, capturas de pantalla relevantes..."
          rows={5}
          className={`${INPUT_BASE} resize-none`}
        />
      </div>

      {/* File attachments */}
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Adjuntos{" "}
          <span className="font-normal text-gray-400">(opcional · .doc, .jpg, .png)</span>
        </label>
        <label
          className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-gray-300 px-4 py-5 transition-colors hover:border-brand-400 hover:bg-brand-50 dark:border-gray-700 dark:hover:border-brand-500 dark:hover:bg-brand-500/10"
        >
          <Paperclip size={22} className="text-gray-400" />
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Arrastra aquí o <span className="font-medium text-brand-500">selecciona archivos</span>
          </p>
          <input
            type="file"
            multiple
            accept=".doc,.jpg,.jpeg,.png"
            className="hidden"
            onChange={(e) => addFiles(e.target.files)}
          />
        </label>
        {attachments.length > 0 && (
          <ul className="mt-2 flex flex-col gap-1.5">
            {attachments.map((f) => (
              <li
                key={f.name}
                className="flex items-center gap-2 rounded-lg border border-gray-100 bg-gray-50 px-3 py-2 dark:border-gray-800 dark:bg-white/3"
              >
                <FileIcon name={f.name} />
                <span className="min-w-0 flex-1 truncate text-sm text-gray-700 dark:text-gray-300">
                  {f.name}
                </span>
                <button
                  type="button"
                  onClick={() => removeFile(f.name)}
                  className="text-gray-400 hover:text-error-500"
                >
                  <X size={14} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
        <button
          type="button"
          onClick={() => setStep(1)}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3"
        >
          Atrás
        </button>
        <button
          type="submit"
          disabled={(!isGlobal && !organizationId) || !notes.trim() || submitting}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:opacity-50"
        >
          {submitting ? "Creando..." : "Crear ticket"}
        </button>
      </div>
    </form>
  );

  return (
    <ModuleBase
      pageTitle="Nuevo ticket"
      breadcrumbItems={[{ label: "Customer Service", path: "/cs/tickets" }]}
    >
      <div className="flex gap-10">
        <aside className="hidden w-52 shrink-0 pt-1 lg:block">
          <StepSidebar steps={stepDefs} current={step} />
        </aside>
        <div className="hidden w-px self-stretch bg-gray-100 dark:bg-white/5 lg:block" />
        <div className="min-w-0 flex-1">
          {step === 1 ? renderStep1() : renderStep2()}
        </div>
      </div>
    </ModuleBase>
  );
};
