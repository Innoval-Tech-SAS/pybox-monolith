import { ContactGrid } from "@/companies/components/contact-grid";
import type { CodebtorCardProps } from "@/companies/types/codebtor-card-props";

export const CodebtorCard: React.FC<CodebtorCardProps> = ({ codebtor }) => (
  <div className="rounded-xl border border-gray-100 p-4 dark:border-gray-800">
    <div className="mb-3 flex items-center justify-between gap-3">
      <div>
        <p className="text-sm font-semibold text-gray-800 dark:text-white/90">{codebtor.fullName}</p>
        <p className="mt-0.5 text-xs text-gray-400">
          {codebtor.documentType} · {codebtor.documentNumber}
        </p>
      </div>
      <span className="shrink-0 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-500 dark:bg-white/5 dark:text-gray-400">
        {codebtor.contactMethods.length} contacto{codebtor.contactMethods.length !== 1 ? "s" : ""}
      </span>
    </div>
    <ContactGrid methods={codebtor.contactMethods} />
  </div>
);
