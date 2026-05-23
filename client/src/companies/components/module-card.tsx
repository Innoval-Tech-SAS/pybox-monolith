import { ArrowRight } from "lucide-react";
import { OrgModule } from "../constants/org-modules";

interface ModuleCardProps {
  module: OrgModule;
  orgId: string;
  id?: string;
}

export const ModuleCard: React.FC<ModuleCardProps> = ({ module, id }) => (
  <button
    id={id}
    disabled={!module.path}
    className="group w-full cursor-pointer overflow-hidden rounded-3xl border border-gray-200 bg-white/80 backdrop-blur-md shadow-lg text-left transition-all duration-200 min-h-56 flex flex-col gap-5 p-5 sm:p-6
      hover:scale-[1.02] hover:shadow-xl
      disabled:cursor-default disabled:opacity-60 disabled:hover:scale-100 disabled:hover:shadow-lg
      dark:border-gray-700 dark:bg-white/3"
  >
    <div className={`flex h-12 w-12 items-center justify-center rounded-2xl shadow-lg transition-shadow duration-200 group-hover:shadow-xl bg-linear-to-r ${module.gradient}`}>
      {module.icon}
    </div>

    <div className="flex-1">
      <span className="mb-2 block text-lg font-semibold leading-tight text-gray-800 line-clamp-2 dark:text-white/90">
        {module.title}
      </span>
      <p className="text-sm leading-relaxed text-gray-500 line-clamp-3 dark:text-gray-400">
        {module.description}
      </p>
    </div>

    <div className="mt-auto flex items-center justify-between">
      <span className="text-sm font-medium text-brand-600 dark:text-brand-400">
        {module.path ? "Ir al módulo" : "Próximamente"}
      </span>
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-50 transition-all duration-200 group-hover:translate-x-1 group-hover:bg-brand-100 dark:bg-brand-500/10 dark:group-hover:bg-brand-500/20">
        <ArrowRight size={18} className="text-brand-600 dark:text-brand-400" />
      </div>
    </div>
  </button>
);
