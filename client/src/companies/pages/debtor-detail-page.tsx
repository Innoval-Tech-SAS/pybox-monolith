import { useNavigate, useSearchParams } from "react-router";
import { CalendarDays, FileStack, FolderOpen, Gavel, History, MapPin, CreditCard, User } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { SectionCard } from "@/companies/components/section-card";
import { CodebtorCard } from "@/companies/components/codebtor-card";
import { ContactGrid } from "@/companies/components/contact-grid";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { usePortfolios } from "../hooks/use-portfolios";
import { useDebtorRelatedContacts, useDebtorCredits } from "../hooks/use-debtor-detail";
import { DEBTOR_TYPE_COLOR, DEBTOR_TYPE_LABEL } from "@/constants/companies/debtors-table";
import { useCreditTypes } from "@/credits/hooks/use-credit-types";
import { CURRENCY_LOCALE } from "@/constants/companies/currency-locale";
import type { DebtorAddress, DebtorCredit } from "@/types/companies/portfolio-debtor-types";

const AddressGrid: React.FC<{ addresses: DebtorAddress[] }> = ({ addresses }) =>
  addresses.length > 0 ? (
    <div className="grid gap-2 sm:grid-cols-2">
      {addresses.map((a) => (
        <div key={a.id} className="rounded-lg bg-gray-50 p-3 dark:bg-white/5">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{a.address}</p>
          <p className="mt-1 text-xs text-gray-400">
            {a.city}, {a.state}, {a.country}
          </p>
          <p className="mt-0.5 text-xs text-gray-400 capitalize">{a.addressType.toLowerCase()}</p>
        </div>
      ))}
    </div>
  ) : (
    <EmptyState icon={MapPin} title="Sin direcciones registradas" className="py-2" />
  );

const CreditList: React.FC<{
  credits: DebtorCredit[];
  /** Etiquetas servidas por GET /credits/types; las resuelve la página, no este componente. */
  creditTypeLabels: Record<string, string>;
}> = ({ credits, creditTypeLabels }) =>
  credits.length > 0 ? (
    <div className="space-y-3">
      {credits.map((c) => (
        <div
          key={c.id}
          className="rounded-xl border border-gray-100 p-4 dark:border-gray-800"
        >
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-gray-800 dark:text-white/90">
                #{c.creditNumber}
              </p>
              <p className="mt-0.5 text-xs text-gray-500">{creditTypeLabels[c.creditType] ?? c.creditType}</p>
            </div>
            {c.daysOverdueAtCutoff > 0 && (
              <span className="rounded-full bg-error-50 px-2.5 py-0.5 text-xs font-medium text-error-600 dark:bg-error-500/10 dark:text-error-400">
                {c.daysOverdueAtCutoff} días mora
              </span>
            )}
          </div>
          <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div>
              <p className="text-xs text-gray-400">Saldo total</p>
              <p className="mt-0.5 text-sm font-medium text-gray-700 dark:text-gray-300">
                {c.totalCreditBalance.toLocaleString(CURRENCY_LOCALE[c.currencyCode] ?? "es-CO", { style: "currency", currency: c.currencyCode, maximumFractionDigits: 0 })}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Capital mora</p>
              <p className={`mt-0.5 text-sm font-medium ${c.overduePrincipalBalance > 0 ? "text-error-600 dark:text-error-400" : "text-gray-700 dark:text-gray-300"}`}>
                {c.overduePrincipalBalance.toLocaleString(CURRENCY_LOCALE[c.currencyCode] ?? "es-CO", { style: "currency", currency: c.currencyCode, maximumFractionDigits: 0 })}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Cuotas mora</p>
              <p className="mt-0.5 text-sm font-medium text-gray-700 dark:text-gray-300">
                {c.overdueInstallments}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Cuotas pendientes</p>
              <p className="mt-0.5 text-sm font-medium text-gray-700 dark:text-gray-300">
                {c.pendingInstallments}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  ) : (
    <EmptyState icon={CreditCard} title="Sin créditos en este portafolio" className="py-2" />
  );

export const DebtorDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const debtorId = searchParams.get("clientId");
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId, buildOrgPath } = useOrgModule();
  const { debtor: debtorCrumb } = useBreadcrumb();

  const { data: contacts, loading: loadingContacts } = useDebtorRelatedContacts(debtorId, portfolioId);
  const { credits, loading: loadingCredits } = useDebtorCredits(debtorId, portfolioId);
  const { labels: creditTypeLabels } = useCreditTypes();

  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";
  const debtor = contacts?.debtor;

  const loading = loadingContacts || loadingCredits;

  const actionButtonClass =
    "inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300";

  return (
    <>
      <PageMeta
        title={debtor?.fullName ?? "Detalle de cliente"}
        description="Detalle del cliente en el portafolio"
      />
      <ModuleBase
        pageTitle={debtor?.fullName ?? "Detalle de cliente"}
        pageIcon={User}
        breadcrumbItems={debtorCrumb({ portfolioId, portfolioName, debtorId })}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : !contacts || !debtor ? (
          <div className="rounded-xl border border-error-200 bg-error-50 p-5 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
            No se pudieron cargar los datos del cliente.
          </div>
        ) : (
          <div className="space-y-5">
            {/* Header info */}
            <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand-50 dark:bg-brand-500/10">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-brand-600 dark:text-brand-400">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
                </svg>
              </div>
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="text-lg font-semibold text-gray-800 dark:text-white/90">
                    {debtor.fullName}
                  </h2>
                  <Badge variant="light" color={DEBTOR_TYPE_COLOR[debtor.debtorType] ?? "light"} size="sm">
                    {DEBTOR_TYPE_LABEL[debtor.debtorType] ?? debtor.debtorType}
                  </Badge>
                </div>
                <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
                  {debtor.documentType} · {debtor.documentNumber}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <button
                  type="button"
                  className={actionButtonClass}
                  onClick={() => navigate(buildOrgPath("/my-companies/portfolios/debtors/payments", { portfolio: portfolioId, clientId: debtorId ?? "" }))}
                >
                  <CalendarDays size={12} />
                  Pagos
                </button>
                <button
                  type="button"
                  className={actionButtonClass}
                  onClick={() => navigate(buildOrgPath("/my-companies/portfolios/debtors/history", { portfolio: portfolioId, clientId: debtorId ?? "" }))}
                >
                  <History size={12} />
                  Historial
                </button>
                <button
                  type="button"
                  className={actionButtonClass}
                  onClick={() => navigate(buildOrgPath("/my-companies/portfolios/debtors/documents", { portfolio: portfolioId, clientId: debtorId ?? "" }))}
                >
                  <FolderOpen size={12} />
                  Archivos
                </button>
                <button
                  type="button"
                  className={actionButtonClass}
                  onClick={() => navigate(buildOrgPath("/my-companies/portfolios/debtors/statements", { portfolio: portfolioId, clientId: debtorId ?? "" }))}
                >
                  <FileStack size={12} />
                  Extractos
                </button>
                <button
                  type="button"
                  className={actionButtonClass}
                  onClick={() => navigate(buildOrgPath("/my-companies/portfolios/debtors/judicial", { portfolio: portfolioId, clientId: debtorId ?? "" }))}
                >
                  <Gavel size={12} />
                  Judicial
                </button>
              </div>
            </div>

            {/* Contacts + Addresses */}
            <div className="grid gap-5 lg:grid-cols-2">
              <SectionCard title="Métodos de contacto">
                <ContactGrid methods={debtor.contactMethods} />
              </SectionCard>
              <SectionCard title="Direcciones">
                <AddressGrid addresses={debtor.addresses} />
              </SectionCard>
            </div>

            {/* Credits */}
            <SectionCard title={`Créditos (${credits.length})`}>
              <CreditList credits={credits} creditTypeLabels={creditTypeLabels} />
            </SectionCard>

            {/* Codebtors */}
            {contacts.codebtors.length > 0 && (
              <SectionCard title={`Codeudores relacionados (${contacts.codebtors.length})`}>
                <div className="space-y-3">
                  {contacts.codebtors.map((co) => (
                    <CodebtorCard key={co.id} codebtor={co} />
                  ))}
                </div>
              </SectionCard>
            )}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
