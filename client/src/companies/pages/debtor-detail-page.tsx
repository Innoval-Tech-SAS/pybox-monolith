import { useParams, useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { useMyCompanies } from "../hooks/use-my-companies";
import { usePortfolios } from "../hooks/use-portfolios";
import { useDebtorRelatedContacts, useDebtorCredits } from "../hooks/use-debtor-detail";
import { DEBTOR_TYPE_COLOR } from "@/constants/companies/debtors-table";
import type { DebtorContactMethod, DebtorAddress, DebtorDetail, DebtorCredit } from "@/types/companies/portfolio-debtor-types";

const SectionCard: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
    <h4 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
      {title}
    </h4>
    {children}
  </div>
);

const ContactGrid: React.FC<{ methods: DebtorContactMethod[] }> = ({ methods }) =>
  methods.length > 0 ? (
    <div className="grid gap-2 sm:grid-cols-2">
      {methods.map((c) => (
        <div key={c.id} className="rounded-lg bg-gray-50 p-3 dark:bg-white/5">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
            {c.contactType}
          </p>
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{c.contactValue}</p>
        </div>
      ))}
    </div>
  ) : (
    <p className="text-sm text-gray-400">Sin métodos de contacto registrados.</p>
  );

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
    <p className="text-sm text-gray-400">Sin direcciones registradas.</p>
  );

const CreditList: React.FC<{ credits: DebtorCredit[] }> = ({ credits }) =>
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
              <p className="mt-0.5 text-xs text-gray-500">{c.creditType}</p>
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
                {c.totalCreditBalance.toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 })}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Capital mora</p>
              <p className={`mt-0.5 text-sm font-medium ${c.overduePrincipalBalance > 0 ? "text-error-600 dark:text-error-400" : "text-gray-700 dark:text-gray-300"}`}>
                {c.overduePrincipalBalance.toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 })}
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
    <p className="text-sm text-gray-400">Sin créditos en este portafolio.</p>
  );

const CodebtorCard: React.FC<{ codebtor: DebtorDetail }> = ({ codebtor }) => (
  <div className="rounded-xl border border-gray-100 p-4 dark:border-gray-800">
    <div className="mb-3 flex items-center justify-between gap-3">
      <div>
        <p className="text-sm font-semibold text-gray-800 dark:text-white/90">{codebtor.fullName}</p>
        <p className="mt-0.5 text-xs text-gray-400">
          {codebtor.documentType} · {codebtor.documentNumber}
        </p>
      </div>
      <span className="shrink-0 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-500 dark:bg-white/5 dark:text-gray-400">
        {codebtor.contactMethods.length} contacto{codebtor.contactMethods.length !== 1 ? "s" : ""}
      </span>
    </div>
    <ContactGrid methods={codebtor.contactMethods} />
  </div>
);

export const DebtorDetailPage: React.FC = () => {
  const { debtorId } = useParams<{ debtorId: string }>();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";

  const parsedDebtorId = Number(debtorId);

  const { data: contacts, loading: loadingContacts } = useDebtorRelatedContacts(
    Number.isFinite(parsedDebtorId) ? parsedDebtorId : null,
    portfolioId,
  );
  const { credits, loading: loadingCredits } = useDebtorCredits(
    Number.isFinite(parsedDebtorId) ? parsedDebtorId : null,
    portfolioId,
  );

  const { orgs } = useMyCompanies();
  const { portfolios } = usePortfolios(orgId);
  const orgName = orgs.find((o) => o.id === orgId)?.name ?? "Empresa";
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";
  const debtor = contacts?.debtor;

  const loading = loadingContacts || loadingCredits;

  return (
    <>
      <PageMeta
        title={debtor?.fullName ?? "Detalle de cliente"}
        description="Detalle del cliente en el portafolio"
      />
      <ModuleBase
        pageTitle={debtor?.fullName ?? "Detalle de cliente"}
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: orgName, path: `/my-companies?org=${orgId}` }] : []),
          { label: "Mis Portafolios", path: `/my-companies/portfolios?org=${orgId}` },
          ...(portfolioId
            ? [{ label: portfolioName, path: `/my-companies/portfolios?org=${orgId}&portfolio=${portfolioId}` }]
            : []),
          { label: "Clientes", path: `/my-companies/portfolios/debtors?org=${orgId}&portfolio=${portfolioId}` },
        ]}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : !contacts ? (
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
                    {debtor.debtorType}
                  </Badge>
                </div>
                <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
                  {debtor.documentType} · {debtor.documentNumber}
                </p>
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
              <CreditList credits={credits} />
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
