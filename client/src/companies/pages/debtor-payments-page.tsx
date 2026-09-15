import { useSearchParams } from "react-router";
import { CalendarDays } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Calendar } from "@/ui/components/calendar/calendar";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { usePortfolios } from "../hooks/use-portfolios";
import { useDebtorPayments } from "../hooks/use-debtor-payments";
import type { CreditWithPayments } from "@/credits/types/credit-types";

export const DebtorPaymentsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const debtorId = searchParams.get("clientId");
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId } = useOrgModule();
  const { debtor } = useBreadcrumb();

  const { credits, loading, error, refetch } = useDebtorPayments(debtorId, portfolioId);
  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const calendarCredits: CreditWithPayments[] = credits.map(({ credit, installments }) => ({
    id: credit.id,
    creditNumber: credit.creditNumber,
    creditType: credit.creditType,
    disbursedDate: credit.disbursedDate,
    totalCreditBalance: credit.totalCreditBalance,
    overduePrincipalBalance: credit.overduePrincipalBalance,
    daysOverdueAtCutoff: credit.daysOverdueAtCutoff,
    role: "TITULAR",
    organizationName: "",
    currencyCode: credit.currencyCode,
    payments: installments.map((i) => ({
      id: i.id,
      limitPayDate: i.limitPayDate,
      paymentDate: i.paymentDate,
      paymentAmount: i.paymentAmount,
      installmentNumber: i.installmentNumber,
      principalPayment: i.principalPayment,
      totalInterestAmount: i.totalInterestAmount,
      otherCharges: i.otherCharges,
      status: i.paymentDate ? "PAGADO" : "PENDIENTE",
    })),
    paymentMethods: [],
    isActive: true,
    settlementRequested: false,
  }));

  return (
    <>
      <PageMeta title="Pagos del cliente" description="Calendario de pagos del cliente" />
      <ModuleBase
        pageTitle="Pagos del cliente"
        pageIcon={CalendarDays}
        breadcrumbItems={debtor({ portfolioId, portfolioName, debtorId, includeDetail: true })}
      >
        <Calendar credits={calendarCredits} loading={loading} error={error} onRetry={refetch} />
      </ModuleBase>
    </>
  );
};
