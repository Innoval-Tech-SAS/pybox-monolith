import { Phone } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import type { ContactGridProps } from "@/companies/types/contact-grid-props";

export const ContactGrid: React.FC<ContactGridProps> = ({ methods }) =>
  methods.length > 0 ? (
    <div className="grid gap-2 sm:grid-cols-2">
      {methods.map((c) => (
        <div key={c.id} className="rounded-lg bg-gray-50 p-3 dark:bg-white/5">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
            {c.contactType}
          </p>
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{c.contactValue}</p>
        </div>
      ))}
    </div>
  ) : (
    <EmptyState icon={Phone} title="Sin métodos de contacto registrados" className="py-2" />
  );
