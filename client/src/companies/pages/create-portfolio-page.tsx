import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { CreatePortfolioForm } from "../components/create-portfolio-form";

export const CreatePortfolioPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org");

  return (
    <>
      <PageMeta title="Crear portafolio" description="Carga un nuevo portafolio de clientes" />
      <ModuleBase
        pageTitle="Crear portafolio"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: "Empresa", path: `/my-companies?org=${orgId}` }] : []),
        ]}
      >
        <CreatePortfolioForm />
      </ModuleBase>
    </>
  );
};
