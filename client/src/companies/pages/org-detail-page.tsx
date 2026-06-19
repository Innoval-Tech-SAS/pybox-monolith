import { useNavigate } from "react-router";
import { ArrowLeft } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ModuleCard } from "../components/module-card";
import { useOrgModule } from "../hooks/use-org-module";
import { ORG_MODULES } from "../constants/org-modules";
import { filterModules } from "../utils/module-access";

export const OrgDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { orgId, orgName, loading } = useOrgModule();

  return (
    <>
      <PageMeta title={orgName || "Empresa"} description="Módulos de la organización" />
      <ModuleBase
        pageTitle={orgName || "Empresa"}
        breadcrumbItems={[{ label: "Mis Empresas", path: "/my-companies" }]}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : (
          <div className="flex flex-col gap-6">
            <button
              onClick={() => navigate("/my-companies")}
              className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 w-fit"
            >
              <ArrowLeft size={16} />
              Volver a Mis Empresas
            </button>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {filterModules(ORG_MODULES, orgId).map((mod) => (
                <ModuleCard key={mod.key} module={mod} orgId={orgId} />
              ))}
            </div>
          </div>
        )}
      </ModuleBase>
    </>
  );
};
