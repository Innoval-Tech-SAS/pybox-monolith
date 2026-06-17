import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ModuleCard } from "../components/module-card";
import { useMyCompanies } from "../hooks/use-my-companies";
import { usePortfolios } from "../hooks/use-portfolios";
import { COMMUNICATIONS_MODULES } from "../constants/communications-modules";
import { filterModules } from "../utils/module-access";

export const CommunicationsHubPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";

  const { orgs, loading: loadingOrgs } = useMyCompanies();
  const { portfolios, loading: loadingPortfolios } = usePortfolios(orgId);
  const loading = loadingOrgs || loadingPortfolios;

  const orgName = orgs.find((o) => o.id === orgId)?.name ?? "Empresa";
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";
  const isOrgVerified = orgs.find((o) => o.id === orgId)?.verificationStatus === "approved";

  const breadcrumbItems = [
    { label: "Mis Empresas", path: "/my-companies" },
    { label: orgName, path: `/my-companies?org=${orgId}` },
    { label: "Mis Portafolios", path: `/my-companies/portfolios?org=${orgId}` },
    { label: portfolioName, path: `/my-companies/portfolios?org=${orgId}&portfolio=${portfolioId}` },
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
