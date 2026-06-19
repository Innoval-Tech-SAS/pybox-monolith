import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { DebtorsTable } from "../components/debtors-table";
import { usePortfolioDebtors } from "../hooks/use-portfolio-debtors";
import { useOrgModule } from "../hooks/use-org-module";
import { usePortfolios } from "../hooks/use-portfolios";

export const PortfolioDebtorsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId, orgName, buildOrgPath } = useOrgModule();

  const { debtors, total, page, pages, search, setSearch, loading, goToPage } =
    usePortfolioDebtors(portfolioId);
  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  return (
    <>
      <PageMeta title="Clientes" description="Clientes del portafolio" />
      <ModuleBase
        pageTitle="Clientes"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: orgName || "Empresa", path: buildOrgPath("/my-companies") }] : []),
          { label: "Mis Portafolios", path: buildOrgPath("/my-companies/portfolios") },
          ...(portfolioId
            ? [{ label: portfolioName, path: buildOrgPath("/my-companies/portfolios", { portfolio: portfolioId }) }]
            : []),
        ]}
      >
        <DebtorsTable
          portfolioId={portfolioId}
          debtors={debtors}
          total={total}
          page={page}
          pages={pages}
          search={search}
          loading={loading}
          onSearch={setSearch}
          onPageChange={goToPage}
        />
      </ModuleBase>
    </>
  );
};
