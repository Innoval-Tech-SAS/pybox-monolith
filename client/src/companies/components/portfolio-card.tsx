import { ArrowRight, Check, Copy, FolderOpen } from "lucide-react";
import { useState } from "react";
import type { Portfolio } from "@/types/companies/portfolio-types";

interface PortfolioCardProps {
  portfolio: Portfolio;
  onClick: () => void;
  colorGradient: string;
}

export const PortfolioCard: React.FC<PortfolioCardProps> = ({ portfolio, onClick, colorGradient }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(portfolio.id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={onClick}
      className="group w-full overflow-hidden rounded-3xl border-2 border-gray-200 bg-white shadow-lg text-left transition-all duration-300
        hover:border-indigo-400 hover:shadow-xl hover:scale-[1.02]
        dark:border-gray-700 dark:bg-gray-900 dark:hover:border-indigo-500
        animate-in fade-in-0 slide-in-from-bottom-4"
    >
      {/* Hero */}
      <div className={`relative h-32 overflow-hidden bg-linear-to-br ${colorGradient}`}>
        <div className="absolute inset-0 flex items-center justify-center">
          <FolderOpen size={72} className="text-white/20" />
        </div>

        <div className="absolute inset-0 bg-linear-to-t from-black/70 via-black/20 to-transparent" />

        <span
          className={`absolute top-3 left-3 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
            portfolio.isActive
              ? "bg-success-50 text-success-700 dark:bg-success-500/20 dark:text-success-400"
              : "bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400"
          }`}
        >
          {portfolio.isActive ? "Activo" : "Inactivo"}
        </span>

        <div className="absolute bottom-3 left-3 right-3 z-10">
          <h3 className="text-base font-bold text-white leading-tight line-clamp-2 drop-shadow-lg mb-1">
            {portfolio.name}
          </h3>
          {portfolio.country && (
            <span
              aria-hidden="true"
              className={`fi fi-${portfolio.country.toLowerCase()} block rounded-sm`}
              style={{ width: "1.5rem", height: "1rem" }}
            />
          )}
        </div>
      </div>

      {/* Body */}
      <div className="flex flex-col gap-4 p-5">
        <p className="text-sm leading-relaxed text-gray-500 line-clamp-2 dark:text-gray-400 min-h-10">
          {portfolio.description ?? "Sin descripción disponible"}
        </p>

        <div className={`relative overflow-hidden rounded-xl bg-linear-to-r ${colorGradient} p-3`}>
          <div className="relative z-10 flex items-start justify-between gap-2">
            <div className="min-w-0">
              <div className="text-white/80 text-xs font-medium mb-0.5">ID de Portafolio</div>
              <div className="text-white text-xs font-mono break-all leading-relaxed">
                {portfolio.id}
              </div>
            </div>
            <button
              onClick={handleCopy}
              title="Copiar ID"
              className="mt-0.5 shrink-0 rounded-md p-1.5 text-white/70 transition hover:bg-white/20 hover:text-white"
            >
              {copied ? <Check size={14} /> : <Copy size={14} />}
            </button>
          </div>
          <div className="absolute -right-4 -bottom-4 opacity-10">
            <FolderOpen size={56} className="text-white" />
          </div>
        </div>

        <div className="flex items-center text-indigo-600 dark:text-indigo-400 font-semibold text-sm group-hover:translate-x-1 transition-transform">
          <span>Gestionar portafolio</span>
          <ArrowRight size={16} className="ml-1.5" />
        </div>
      </div>
    </button>
  );
};
