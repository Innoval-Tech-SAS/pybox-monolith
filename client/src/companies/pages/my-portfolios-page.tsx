import { useSearchParams } from "react-router";
import { Briefcase, FolderOpen } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ModuleCard } from "../components/module-card";
import { PortfolioCard } from "../components/portfolio-card";
import { CreatePortfolioCard } from "../components/create-portfolio-card";
import { usePortfolios } from "../hooks/use-portfolios";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { PORTFOLIO_MODULES } from "../constants/portfolio-modules";
import { filterModules } from "../utils/module-access";
import { usePortfoliosListTour } from "../hooks/use-portfolios-list-tour";
import { usePortfolioModulesTour } from "../hooks/use-portfolio-modules-tour";

export const MyPortfoliosPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId, orgs } = useOrgModule();
  const { build } = useBreadcrumb();
  const { portfolios, loading } = usePortfolios(orgId);
  const org = orgs.find((o) => o.id === orgId);
  const isOrgVerified = org?.verificationStatus === "APROBADO";

  const selectedPortfolio = portfolios.find((p) => p.id === portfolioId);
  const isPortfolioView = !!portfolioId && !!selectedPortfolio;

  const visiblePortfolioModules = isPortfolioView ? filterModules(PORTFOLIO_MODULES, orgId, isOrgVerified) : [];

  usePortfoliosListTour(!loading && !isPortfolioView);
  usePortfolioModulesTour(!loading && isPortfolioView, visiblePortfolioModules.map((mod) => mod.key));

  const pageTitle = isPortfolioView ? (selectedPortfolio.name ?? "Portafolio") : "Mis Portafolios";

  const breadcrumbItems = build();

  return (
    <>
      <PageMeta title={pageTitle} description="Portafolios de la empresa" />
      <ModuleBase
        pageTitle={pageTitle}
        pageIcon={isPortfolioView ? Briefcase : FolderOpen}
        breadcrumbItems={breadcrumbItems}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : isPortfolioView ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {visiblePortfolioModules.map((mod) => (
              <ModuleCard key={mod.key} id={`tour-pf-module-${mod.key}`} module={mod} orgId={orgId} portfolioId={portfolioId} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <CreatePortfolioCard id="tour-create-portfolio" />
            {portfolios.map((p) => (
              <PortfolioCard
                key={p.id}
                portfolio={p}
                onClick={() => setSearchParams({ org: orgId, portfolio: p.id })}
              />
            ))}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
