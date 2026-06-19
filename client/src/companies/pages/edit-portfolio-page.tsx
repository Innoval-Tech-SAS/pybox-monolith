import { useLocation, useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { EditPortfolioForm } from "../components/edit-portfolio-form";
import { useOrgModule } from "../hooks/use-org-module";
import { usePortfolios } from "../hooks/use-portfolios";
import type { CsvUploadMode } from "../hooks/use-upload-portfolio-csv";

export const EditPortfolioPage: React.FC = () => {
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";

  const { orgId, orgName, buildOrgPath } = useOrgModule();
  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const mode: CsvUploadMode = location.pathname.endsWith("/update") ? "update" : "append";
  const title = mode === "update" ? "Actualizar clientes" : "Subir nuevos clientes";

  return (
    <>
      <PageMeta title={title} description="Carga masiva de clientes en el portafolio" />
      <ModuleBase
        pageTitle={title}
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: orgName || "Empresa", path: buildOrgPath("/my-companies") }] : []),
          { label: "Portafolios", path: buildOrgPath("/my-companies/portfolios") },
          ...(portfolioId ? [{ label: portfolioName, path: buildOrgPath("/my-companies/portfolios", { portfolio: portfolioId }) }] : []),
        ]}
      >
        <EditPortfolioForm mode={mode} />
      </ModuleBase>
    </>
  );
};
