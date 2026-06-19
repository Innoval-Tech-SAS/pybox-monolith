import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { CreatePortfolioForm } from "../components/create-portfolio-form";
import { useOrgModule } from "../hooks/use-org-module";

export const CreatePortfolioPage: React.FC = () => {
  const { orgId, orgName, buildOrgPath } = useOrgModule();

  return (
    <>
      <PageMeta title="Crear portafolio" description="Carga un nuevo portafolio de clientes" />
      <ModuleBase
        pageTitle="Crear portafolio"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: orgName || "Empresa", path: buildOrgPath("/my-companies") }] : []),
        ]}
      >
        <CreatePortfolioForm />
      </ModuleBase>
    </>
  );
};
