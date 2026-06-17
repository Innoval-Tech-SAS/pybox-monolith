import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { CreatePortfolioForm } from "../components/create-portfolio-form";
import { useMyCompanies } from "../hooks/use-my-companies";

export const CreatePortfolioPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org");

  const { orgs } = useMyCompanies();
  const orgName = orgs.find((o) => o.id === orgId)?.name ?? "Empresa";

  return (
    <>
      <PageMeta title="Crear portafolio" description="Carga un nuevo portafolio de clientes" />
      <ModuleBase
        pageTitle="Crear portafolio"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: orgName, path: `/my-companies?org=${orgId}` }] : []),
        ]}
      >
        <CreatePortfolioForm />
      </ModuleBase>
    </>
  );
};
