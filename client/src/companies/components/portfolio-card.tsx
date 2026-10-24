import { ArrowRight, Check, Copy, FolderOpen } from "lucide-react";
import { useState } from "react";
import type { PortfolioCardProps } from "@/types/props/portfolio-card-props";

export const PortfolioCard: React.FC<PortfolioCardProps> = ({ portfolio, onClick }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(portfolio.id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      type="button"
      onClick={onClick}
      className="group relative w-full overflow-hidden rounded-2xl border border-gray-200 bg-white text-left transition-colors duration-200
        hover:border-brand-300
        dark:border-gray-800 dark:bg-gray-900 dark:hover:border-brand-700"
    >
      {/* Status dot */}
      <span
        className={`absolute top-3 right-3 z-20 h-2.5 w-2.5 rounded-full ring-2 ring-white dark:ring-gray-900 ${
          portfolio.isActive ? "bg-success-500" : "bg-gray-400"
        }`}
      />

      {/* Hero */}
      <div className="relative h-24 overflow-hidden bg-linear-to-br from-brand-500 to-brand-600">
        <div className="absolute inset-0 flex items-center justify-center">
          <FolderOpen size={56} className="text-white/20" />
        </div>

        <div className="absolute inset-0 bg-linear-to-t from-black/70 via-black/20 to-transparent" />

        <div className="absolute bottom-3 left-3 right-3 z-10">
          <h3 className="text-base font-bold text-white leading-tight line-clamp-2 drop-shadow-lg mb-1">
            {portfolio.name}
          </h3>
          {portfolio.country && (
            <span
              aria-hidden="true"
              className={`fi fi-${portfolio.country.toLowerCase()} block h-4 w-6 rounded-sm`}
            />
          )}
        </div>
      </div>

      {/* Body */}
      <div className="flex flex-col gap-3 p-4">
        <p className="text-sm leading-relaxed text-gray-500 line-clamp-2 dark:text-gray-400 min-h-10">
          {portfolio.description ?? "Sin descripción disponible"}
        </p>

        <div className="relative overflow-hidden rounded-xl bg-linear-to-r from-brand-500 to-brand-600 p-3">
          <div className="relative z-10 flex items-start justify-between gap-2">
            <div className="min-w-0">
              <div className="text-white/80 text-xs font-medium mb-0.5">ID de Portafolio</div>
              <div className="text-white text-xs font-mono break-all leading-relaxed">
                {portfolio.id}
              </div>
            </div>
            <button
              type="button"
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

        <div className="flex items-center text-brand-600 dark:text-brand-400 font-semibold text-sm group-hover:translate-x-1 transition-transform">
          <span>Gestionar portafolio</span>
          <ArrowRight size={16} className="ml-1.5" />
        </div>
      </div>
    </button>
  );
};
