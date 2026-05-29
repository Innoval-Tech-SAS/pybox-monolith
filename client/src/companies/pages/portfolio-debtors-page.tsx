import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { DebtorsTable } from "../components/debtors-table";
import { usePortfolioDebtors } from "../hooks/use-portfolio-debtors";

export const PortfolioDebtorsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";

  const { debtors, total, page, pages, search, setSearch, loading, goToPage } =
    usePortfolioDebtors(portfolioId);

  return (
    <>
      <PageMeta title="Clientes" description="Clientes del portafolio" />
      <ModuleBase
        pageTitle="Clientes"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: "Empresa", path: `/my-companies?org=${orgId}` }] : []),
          { label: "Portafolios", path: `/my-companies/portfolios?org=${orgId}` },
          ...(portfolioId
            ? [{ label: "Portafolio", path: `/my-companies/portfolios?org=${orgId}&portfolio=${portfolioId}` }]
            : []),
        ]}
      >
        <DebtorsTable
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
