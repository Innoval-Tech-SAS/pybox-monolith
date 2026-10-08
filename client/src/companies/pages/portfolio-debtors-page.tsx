import { useSearchParams } from "react-router";
import { Users } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { DebtorsTable } from "../components/debtors-table";
import { usePortfolioDebtors } from "../hooks/use-portfolio-debtors";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { usePortfolios } from "../hooks/use-portfolios";

export const PortfolioDebtorsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId } = useOrgModule();
  const { build } = useBreadcrumb();

  const {
    debtors, total, page, pages,
    search, setSearch,
    pageSize, setPageSize,
    sortKey, sortOrder, handleSort,
    loading, goToPage,
  } = usePortfolioDebtors(portfolioId);
  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  return (
    <>
      <PageMeta title="Clientes" description="Clientes del portafolio" />
      <ModuleBase
        pageTitle="Clientes"
        pageIcon={Users}
        breadcrumbItems={build({ portfolio: { id: portfolioId, name: portfolioName } })}
      >
        <DebtorsTable
          portfolioId={portfolioId}
          debtors={debtors}
          total={total}
          page={page}
          pages={pages}
          search={search}
          pageSize={pageSize}
          sortKey={sortKey}
          sortOrder={sortOrder}
          loading={loading}
          onSearch={setSearch}
          onPageSizeChange={setPageSize}
          onSort={handleSort}
          onPageChange={goToPage}
        />
      </ModuleBase>
    </>
  );
};
