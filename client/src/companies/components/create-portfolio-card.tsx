import { ArrowRight, FolderPlus } from "lucide-react";
import { useNavigate } from "react-router";
import { useOrgModule } from "../hooks/use-org-module";

export const CreatePortfolioCard: React.FC<{ id?: string }> = ({ id }) => {
  const navigate = useNavigate();
  const { buildOrgPath } = useOrgModule();

  return (
    <button
      id={id}
      onClick={() => navigate(buildOrgPath("/my-companies/add-portfolio"))}
      className="group w-full flex flex-col overflow-hidden rounded-3xl border-2 border-dashed border-brand-300 bg-white shadow-lg text-left transition-all duration-300
        hover:border-brand-400 hover:shadow-xl hover:scale-[1.02]
        dark:border-brand-700 dark:bg-gray-900 dark:hover:border-brand-500"
    >
      <div className="relative h-24 overflow-hidden bg-linear-to-br from-brand-500 to-brand-600">
        <div className="absolute inset-0 flex items-center justify-center">
          <FolderPlus size={56} className="text-white/20" />
        </div>
        <div className="absolute inset-0 bg-linear-to-t from-black/60 via-black/10 to-transparent" />
        <div className="absolute bottom-3 left-3 right-3 z-10">
          <h3 className="text-base font-bold text-white leading-tight drop-shadow-lg">
            Crear portafolio
          </h3>
        </div>
      </div>

      <div className="flex flex-1 flex-col justify-between gap-3 p-4">
        <p className="text-sm leading-relaxed text-gray-500 dark:text-gray-400">
          Carga un nuevo portafolio de clientes desde un archivo CSV.
        </p>

        <div className="flex items-center text-brand-600 dark:text-brand-400 font-semibold text-sm group-hover:translate-x-1 transition-transform">
          <span>Crear nuevo</span>
          <ArrowRight size={16} className="ml-1.5" />
        </div>
      </div>
    </button>
  );
};
