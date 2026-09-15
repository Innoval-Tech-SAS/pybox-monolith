import { ArrowRight, Building2 } from "lucide-react";
import type { OrgCardProps } from "@/types/props/org-card-props";
import { resolveFileUrl } from "@/companies/utils/resolve-doc-file-url";

export const OrgCard: React.FC<OrgCardProps> = ({ org, onClick }) => {
  const logoUrl = resolveFileUrl(org.logoUrl);

  return (
  <button
    onClick={() => onClick(org.id)}
    className="group w-full text-left cursor-pointer overflow-hidden rounded-2xl border border-gray-200 bg-white transition-colors duration-200 min-h-56 flex flex-col gap-5 p-5 sm:p-6 hover:border-brand-300 dark:border-gray-800 dark:bg-white/3 dark:hover:border-brand-700"
  >
    <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl bg-brand-50 dark:bg-brand-500/10">
      {logoUrl ? (
        <img src={logoUrl} alt="" className="size-full object-contain" />
      ) : (
        <Building2 size={24} className="text-brand-600 dark:text-brand-400" />
      )}
    </div>

    <div className="flex-1">
      <span className="mb-2 block text-lg font-semibold leading-tight text-gray-800 line-clamp-2 dark:text-white/90">
        {org.name}
      </span>
      {org.description && (
        <p className="text-sm leading-relaxed text-gray-500 line-clamp-3 dark:text-gray-400">
          {org.description}
        </p>
      )}
      {org.fiscalDocumentNumber && (
        <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
          {org.fiscalDocumentType} · {org.fiscalDocumentNumber}
        </p>
      )}
      {org.country && (
        <span
          aria-hidden="true"
          className={`fi fi-${org.country.toLowerCase()} mt-2 block h-4 w-6 rounded-sm`}
        />
      )}
    </div>

    <div className="mt-auto flex items-center justify-between">
      <span className="text-sm font-medium text-brand-600 dark:text-brand-400">
        Ver detalles
      </span>
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-50 transition-all duration-200 group-hover:translate-x-1 group-hover:bg-brand-100 dark:bg-brand-500/10 dark:group-hover:bg-brand-500/20">
        <ArrowRight size={18} className="text-brand-600 dark:text-brand-400" />
      </div>
    </div>
  </button>
  );
};
