import { ArrowRight } from "lucide-react";
import { useNavigate } from "react-router";
import type { ModuleCardProps } from "@/types/props/module-card-props";

export const ModuleCard: React.FC<ModuleCardProps> = ({ module, orgId, portfolioId, id }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (!module.path) return;
    const params = new URLSearchParams({ org: orgId });
    if (portfolioId) params.set("portfolio", portfolioId);
    navigate(`${module.path}?${params}`);
  };

  return (
  <button
    id={id}
    type="button"
    onClick={handleClick}
    disabled={!module.path}
    className="group w-full text-left cursor-pointer overflow-hidden rounded-2xl border border-gray-200 bg-white transition-colors duration-200 min-h-56 flex flex-col gap-5 p-5 sm:p-6
      hover:border-brand-300
      disabled:cursor-default disabled:opacity-60 disabled:hover:border-gray-200
      dark:border-gray-800 dark:bg-white/3 dark:hover:border-brand-700 dark:disabled:hover:border-gray-800"
  >
    <div className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-linear-to-r ${module.gradient}`}>
      <module.icon size={24} className="text-white" />
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
};
