import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ModuleCard } from "../components/module-card";
import { useOrgModule } from "../hooks/use-org-module";
import { usePortfolios } from "../hooks/use-portfolios";
import { COMMUNICATIONS_MODULES } from "../constants/communications-modules";
import { filterModules } from "../utils/module-access";

export const CommunicationsHubPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId, orgName, orgs, loading: loadingOrgs, buildOrgPath } = useOrgModule();

  const { portfolios, loading: loadingPortfolios } = usePortfolios(orgId);
  const loading = loadingOrgs || loadingPortfolios;

  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";
  const isOrgVerified = orgs.find((o) => o.id === orgId)?.verificationStatus === "approved";

  const breadcrumbItems = [
    { label: "Mis Empresas", path: "/my-companies" },
    { label: orgName || "Empresa", path: buildOrgPath("/my-companies") },
    { label: "Mis Portafolios", path: buildOrgPath("/my-companies/portfolios") },
    { label: portfolioName, path: buildOrgPath("/my-companies/portfolios", { portfolio: portfolioId }) },
  ];

  return (
    <>
      <PageMeta title="Comunicaciones" description="Segmentos, plantillas y campañas de mensajería" />
      <ModuleBase pageTitle="Comunicaciones" breadcrumbItems={breadcrumbItems}>
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filterModules(COMMUNICATIONS_MODULES, orgId, isOrgVerified).map((mod) => (
              <ModuleCard key={mod.key} module={mod} orgId={orgId} portfolioId={portfolioId} />
            ))}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
