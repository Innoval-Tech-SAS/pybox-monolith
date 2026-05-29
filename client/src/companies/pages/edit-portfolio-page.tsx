import { useLocation, useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { EditPortfolioForm } from "../components/edit-portfolio-form";
import type { CsvUploadMode } from "../hooks/use-upload-portfolio-csv";

export const EditPortfolioPage: React.FC = () => {
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";

  const mode: CsvUploadMode = location.pathname.endsWith("/update") ? "update" : "append";
  const title = mode === "update" ? "Actualizar clientes" : "Subir nuevos clientes";

  return (
    <>
      <PageMeta title={title} description="Carga masiva de clientes en el portafolio" />
      <ModuleBase
        pageTitle={title}
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: "Empresa", path: `/my-companies?org=${orgId}` }] : []),
          { label: "Portafolios", path: `/my-companies/portfolios?org=${orgId}` },
          ...(portfolioId ? [{ label: "Portafolio", path: `/my-companies/portfolios?org=${orgId}&portfolio=${portfolioId}` }] : []),
        ]}
      >
        <EditPortfolioForm mode={mode} />
      </ModuleBase>
    </>
  );
};
