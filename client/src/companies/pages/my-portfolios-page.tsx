import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ModuleCard } from "../components/module-card";
import { PortfolioCard } from "../components/portfolio-card";
import { CreatePortfolioCard } from "../components/create-portfolio-card";
import { usePortfolios } from "../hooks/use-portfolios";
import { PORTFOLIO_MODULES } from "../constants/portfolio-modules";
import { usePortfoliosListTour } from "../hooks/use-portfolios-list-tour";
import { usePortfolioModulesTour } from "../hooks/use-portfolio-modules-tour";

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
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { portfolios, loading } = usePortfolios(orgId);

  const selectedPortfolio = portfolios.find((p) => p.id === portfolioId);
  const isPortfolioView = !!portfolioId && !!selectedPortfolio;

  usePortfoliosListTour(!loading && !isPortfolioView);
  usePortfolioModulesTour(!loading && isPortfolioView);

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
              <ModuleCard key={mod.key} id={`tour-pf-module-${mod.key}`} module={mod} orgId={orgId} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <CreatePortfolioCard id="tour-create-portfolio" />
            {portfolios.map((p, i) => (
              <PortfolioCard
                key={p.id}
                portfolio={p}
                colorGradient={CARD_GRADIENTS[i % CARD_GRADIENTS.length]}
                onClick={() => setSearchParams({ org: orgId, portfolio: p.id })}
              />
            ))}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
