import { ArrowRight, Building2 } from "lucide-react";
import { useNavigate } from "react-router";

export const CreateOrgCard: React.FC = () => {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate("/my-companies/create")}
      className="group w-full cursor-pointer overflow-hidden rounded-3xl border border-gray-200 bg-white/80 backdrop-blur-md shadow-lg text-left transition-all duration-200 min-h-56 flex flex-col gap-5 p-5 sm:p-6 hover:scale-[1.01] hover:shadow-xl dark:border-gray-700 dark:bg-white/3"
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-linear-to-r from-brand-500 to-brand-600 shadow-lg transition-shadow duration-200 group-hover:shadow-xl">
        <Building2 size={24} className="text-white" />
      </div>

      <div className="flex-1">
        <span className="mb-2 block text-lg font-semibold leading-tight text-gray-800 line-clamp-2 dark:text-white/90">
          Crear nueva empresa
        </span>
        <p className="text-sm leading-relaxed text-gray-500 line-clamp-3 dark:text-gray-400">
          Registra y configura una nueva organización.
        </p>
      </div>

      <div className="mt-auto flex items-center justify-between">
        <span className="text-sm font-medium text-brand-600 dark:text-brand-400">
          Crear
        </span>
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-50 transition-all duration-200 group-hover:translate-x-1 group-hover:bg-brand-100 dark:bg-brand-500/10 dark:group-hover:bg-brand-500/20">
          <ArrowRight size={18} className="text-brand-600 dark:text-brand-400" />
        </div>
      </div>
    </button>
  );
};
