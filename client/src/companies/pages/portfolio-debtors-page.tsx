import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { DebtorsTable } from "../components/debtors-table";
import { usePortfolioDebtors } from "../hooks/use-portfolio-debtors";
import { useMyCompanies } from "../hooks/use-my-companies";
import { usePortfolios } from "../hooks/use-portfolios";

export const PortfolioDebtorsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";

  const { debtors, total, page, pages, search, setSearch, loading, goToPage } =
    usePortfolioDebtors(portfolioId);
  const { orgs } = useMyCompanies();
  const { portfolios } = usePortfolios(orgId);
  const orgName = orgs.find((o) => o.id === orgId)?.name ?? "Empresa";
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  return (
    <>
      <PageMeta title="Clientes" description="Clientes del portafolio" />
      <ModuleBase
        pageTitle="Clientes"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: orgName, path: `/my-companies?org=${orgId}` }] : []),
          { label: "Mis Portafolios", path: `/my-companies/portfolios?org=${orgId}` },
          ...(portfolioId
            ? [{ label: portfolioName, path: `/my-companies/portfolios?org=${orgId}&portfolio=${portfolioId}` }]
            : []),
        ]}
      >
        <DebtorsTable
          orgId={orgId}
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
