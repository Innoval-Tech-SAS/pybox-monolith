import { CalendarDays, CreditCard, TriangleAlert } from "lucide-react";
import type { ObligationsSummaryCardsProps } from "@/types/props/self-home-props";
import { formatCreditCurrency } from "@/credits/utils/financial-calendar-utils";

const capitalize = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

/** Fila de KPIs: total del mes, cuotas por vencer y mora, al mismo nivel que el resto de dashboards del app. */
export const SelfObligationsSummary: React.FC<ObligationsSummaryCardsProps> = ({
  summary,
  loading = false,
}) => {
  const money = (amount: number) => formatCreditCurrency(amount, summary.currencyCode);
  const skeleton = "inline-block h-8 w-32 animate-pulse rounded bg-gray-100 dark:bg-gray-800";

  return (
    <section className="grid gap-4 sm:grid-cols-3">
      <div className="rounded-2xl border border-brand-200 bg-white p-5 dark:border-brand-500/30 dark:bg-white/3">
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-50 text-brand-500 dark:bg-brand-500/15 dark:text-brand-400">
            <CreditCard size={18} />
          </span>
          <span className="text-theme-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
            Total obligaciones
          </span>
        </div>
        {loading ? (
          <span className={`mt-3 ${skeleton}`} />
        ) : (
          <p className="mt-3 text-title-md font-extralight text-brand-500 dark:text-brand-400">
            {money(summary.monthTotal)}
          </p>
        )}
        <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
          Este mes · {summary.entityCount} {summary.entityCount === 1 ? "entidad" : "entidades"}
        </p>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/3">
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400">
            <CalendarDays size={18} />
          </span>
          <span className="text-theme-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
            Cuotas por vencer
          </span>
        </div>
        {loading ? (
          <span className={`mt-3 ${skeleton}`} />
        ) : (
          <p className="mt-3 text-title-md font-extralight text-gray-800 dark:text-white/90">
            {money(summary.dueTotal)}
          </p>
        )}
        <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
          {capitalize(summary.periodLabel)}
        </p>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/3">
        <div className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400">
            <TriangleAlert size={18} />
          </span>
          <span className="text-theme-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
            Total en mora
          </span>
        </div>
        {loading ? (
          <span className={`mt-3 ${skeleton}`} />
        ) : (
          <p
            className={`mt-3 text-title-md font-extralight ${summary.overdueTotal > 0 ? "text-error-600 dark:text-error-400" : "text-gray-800 dark:text-white/90"}`}
          >
            {money(summary.overdueTotal)}
          </p>
        )}
        <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
          {summary.overdueTotal > 0 ? "Requiere atención" : "Sin saldo vencido"}
        </p>
      </div>
    </section>
  );
};
