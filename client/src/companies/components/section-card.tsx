import type { SectionCardProps } from "@/companies/types/section-card-props";

export const SectionCard: React.FC<SectionCardProps> = ({ title, children }) => (
  <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
    <h4 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
      {title}
    </h4>
    {children}
  </div>
);
