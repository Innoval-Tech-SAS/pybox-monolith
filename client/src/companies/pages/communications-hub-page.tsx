import { useSearchParams } from "react-router";
import { Send } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ModuleCard } from "../components/module-card";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { usePortfolios } from "../hooks/use-portfolios";
import { COMMUNICATIONS_MODULES } from "../constants/communications-modules";
import { filterModules } from "../utils/module-access";
import { useCommunicationsTour } from "../hooks/use-communications-tour";

export const CommunicationsHubPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId, orgs, loading: loadingOrgs } = useOrgModule();
  const { build } = useBreadcrumb();

  const { portfolios, loading: loadingPortfolios } = usePortfolios(orgId);
  const loading = loadingOrgs || loadingPortfolios;

  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";
  const isOrgVerified = orgs.find((o) => o.id === orgId)?.verificationStatus === "APROBADO";

  const visibleModules = filterModules(COMMUNICATIONS_MODULES, orgId, isOrgVerified);

  useCommunicationsTour(!loading, visibleModules.map((mod) => mod.key));

  const breadcrumbItems = build({ portfolio: { id: portfolioId, name: portfolioName } });

  return (
    <>
      <PageMeta title="Comunicaciones" description="Segmentos, plantillas y campañas de mensajería" />
      <ModuleBase pageTitle="Comunicaciones" pageIcon={Send} breadcrumbItems={breadcrumbItems}>
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {visibleModules.map((mod) => (
              <ModuleCard
                key={mod.key}
                id={`tour-comm-module-${mod.key}`}
                module={mod}
                orgId={orgId}
                portfolioId={portfolioId}
              />
            ))}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
