import { Link } from "react-router";
import { CreditCard } from "lucide-react";
import { useMyCredits } from "@/credits/hooks/use-my-credits";
import { formatCreditCurrency } from "@/credits/utils/financial-calendar-utils";
import { ModuleBase } from "@/ui/components/common/module-base";
import { CreditStatusBadge } from "@/credits/components/credit-status-badge";
import { IdentityVerificationNotice } from "@/credits/components/identity-verification-notice";
import { Button } from "@/ui/components/button/button";
import EmptyState from "@/ui/components/common/empty-state";

export const MyCreditsPage: React.FC = () => {
  const { credits, loading, error, identityPending, refetch } = useMyCredits();

  return (
    <ModuleBase pageTitle="Mis Obligaciones" pageIcon={CreditCard} showBack>
      {loading && <p className="text-sm text-gray-500 dark:text-gray-400">Cargando tus obligaciones...</p>}

      {!loading && identityPending && <IdentityVerificationNotice />}

      {!loading && !identityPending && error && (
        <div className="flex flex-col items-start gap-3">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <Button type="button" size="sm" variant="outline" onClick={refetch}>
            Reintentar
          </Button>
        </div>
      )}

      {!loading && !identityPending && !error && credits.length === 0 && (
        <EmptyState icon={CreditCard} title="No tienes obligaciones registradas" className="py-20" />
      )}

      {!loading && !identityPending && !error && credits.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {credits.map((credit) => {
            return (
              <Link
                key={credit.id}
                to={`/my-credits/${credit.id}`}
                className="flex flex-col gap-3 rounded-2xl border border-gray-200 bg-white p-5 transition hover:border-brand-300 hover:shadow-sm dark:border-gray-800 dark:bg-white/3 dark:hover:border-brand-700"
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="font-semibold text-gray-800 dark:text-white/90">{credit.creditNumber}</span>
                  <CreditStatusBadge isActive={credit.isActive} settlementRequested={credit.settlementRequested} />
                </div>
                {credit.organizationName && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">{credit.organizationName}</p>
                )}
                <div>
                  <p className="mb-1 text-xs font-medium text-gray-500 dark:text-gray-400">Saldo total</p>
                  <p className="text-lg font-semibold text-gray-800 dark:text-white/90">
                    {formatCreditCurrency(credit.totalCreditBalance, credit.currencyCode)}
                  </p>
                </div>
                <span className="text-xs text-gray-400 dark:text-gray-500">{credit.role}</span>
              </Link>
            );
          })}
        </div>
      )}
    </ModuleBase>
  );
};
