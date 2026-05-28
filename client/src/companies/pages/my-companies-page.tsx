import { Building2 } from "lucide-react";
import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { OrgCard } from "../components/org-card";
import { CreateOrgCard } from "../components/create-org-card";
import { ModuleCard } from "../components/module-card";
import { useMyCompanies } from "../hooks/use-my-companies";
import { useOrgTour } from "../hooks/use-org-tour";
import { ORG_MODULES } from "../constants/org-modules";
import { filterModules } from "../utils/module-access";

export const MyCompaniesPage: React.FC = () => {
  const { orgs, loading } = useMyCompanies();
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedId = searchParams.get("org");
  const selectedOrg = orgs.find((o) => o.id === selectedId);
  const isOrgView = !!selectedId;

  useOrgTour(isOrgView && !loading);

  return (
    <>
      <PageMeta
        title={selectedOrg?.name ?? "Mis Empresas"}
        description="Gestión de empresas"
      />
      <ModuleBase
        pageTitle={selectedOrg?.name ?? "Mis Empresas"}
        breadcrumbItems={isOrgView ? [{ label: "Mis Empresas", path: "/my-companies" }] : []}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : isOrgView ? (
          <div className="flex flex-col gap-6">
            <div id="tour-modules-grid" className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {filterModules(ORG_MODULES, selectedId).map((mod) => (
                <ModuleCard
                  key={mod.key}
                  module={mod}
                  orgId={selectedId}
                  id={`tour-module-${mod.key}`}
                />
              ))}
            </div>
          </div>
        ) : orgs.length === 0 ? (
          <EmptyState icon={Building2} title="No tienes empresas registradas" className="py-20" />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <CreateOrgCard />
            {orgs.map((org) => (
              <OrgCard
                key={org.id}
                org={org}
                onClick={(id) => setSearchParams({ org: id })}
              />
            ))}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
