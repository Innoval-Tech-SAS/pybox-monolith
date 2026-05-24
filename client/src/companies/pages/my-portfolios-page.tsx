import { FolderOpen, Plus } from "lucide-react";
import { useSearchParams, useNavigate } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ModuleCard } from "../components/module-card";
import { PortfolioCard } from "../components/portfolio-card";
import { usePortfolios } from "../hooks/use-portfolios";
import { PORTFOLIO_MODULES } from "../constants/portfolio-modules";

const CARD_GRADIENTS = [
  "from-indigo-500 to-purple-600",
  "from-emerald-500 to-teal-600",
  "from-orange-500 to-red-600",
  "from-sky-500 to-blue-600",
  "from-pink-500 to-rose-600",
  "from-violet-500 to-fuchsia-600",
];

export const MyPortfoliosPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { portfolios, loading } = usePortfolios(orgId);

  const selectedPortfolio = portfolios.find((p) => p.id === portfolioId);
  const isPortfolioView = !!portfolioId && !!selectedPortfolio;

  const pageTitle = isPortfolioView ? (selectedPortfolio.name ?? "Portafolio") : "Mis Portafolios";

  const breadcrumbItems = [
    { label: "Mis Empresas", path: "/my-companies" },
    ...(orgId ? [{ label: "Empresa", path: `/my-companies?org=${orgId}` }] : []),
    ...(isPortfolioView ? [{ label: "Mis Portafolios", path: `/my-companies/portfolios?org=${orgId}` }] : []),
  ];

  return (
    <>
      <PageMeta title={pageTitle} description="Portafolios de la organización" />
      <ModuleBase pageTitle={pageTitle} breadcrumbItems={breadcrumbItems}>
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : isPortfolioView ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {PORTFOLIO_MODULES.map((mod) => (
              <ModuleCard key={mod.key} module={mod} orgId={orgId} />
            ))}
          </div>
        ) : portfolios.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-4 py-24 text-gray-400">
            <FolderOpen size={48} strokeWidth={1.5} />
            <p className="text-sm">No hay portafolios registrados</p>
            {orgId && (
              <button
                onClick={() => navigate(`/my-companies/add-portfolio?org=${orgId}`)}
                className="inline-flex items-center gap-2 rounded-xl bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600"
              >
                <Plus size={15} />
                Crear primer portafolio
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                onClick={() => navigate(`/my-companies/add-portfolio?org=${orgId}`)}
                className="inline-flex items-center gap-2 rounded-xl bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600"
              >
                <Plus size={15} />
                Nuevo portafolio
              </button>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {portfolios.map((p, i) => (
                <PortfolioCard
                  key={p.id}
                  portfolio={p}
                  colorGradient={CARD_GRADIENTS[i % CARD_GRADIENTS.length]}
                  onClick={() => setSearchParams({ org: orgId, portfolio: p.id })}
                />
              ))}
            </div>
          </div>
        )}
      </ModuleBase>
    </>
  );
};
