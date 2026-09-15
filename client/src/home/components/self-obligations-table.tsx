import { Link } from "react-router";
import { ArrowRight } from "lucide-react";
import type { ObligationsTableProps } from "@/types/props/self-home-props";
import { getCreditTypeStyle } from "@/constants/credits/financial-calendar";
import { formatCreditCurrency, formatPaymentDate } from "@/credits/utils/financial-calendar-utils";
import { Loader } from "@/ui/components/loader/loader";

/** "Detalle de obligaciones": una fila por obligación, con su próxima cuota y estado. */
export const SelfObligationsTable: React.FC<ObligationsTableProps> = ({
  rows,
  creditTypeLabels,
  paymentStatusLabels,
  loading = false,
}) => (
  <section className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/3">
    <h2 className="px-5 pt-5 text-base font-semibold text-gray-800 dark:text-white/90">
      Detalle de obligaciones
    </h2>

    {loading ? (
      <div className="flex min-h-40 items-center justify-center">
        <Loader loaderText="Cargando obligaciones..." />
      </div>
    ) : rows.length === 0 ? (
      <p className="px-5 py-10 text-center text-sm text-gray-400 dark:text-gray-500">
        No tienes obligaciones registradas.
      </p>
    ) : (
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[640px] text-left">
          <thead>
            <tr className="border-y border-gray-100 text-xs text-gray-500 dark:border-gray-800 dark:text-gray-400">
              <th className="px-5 py-2.5 font-medium">Tipo de obligación</th>
              <th className="px-3 py-2.5 font-medium">Entidad</th>
              <th className="px-3 py-2.5 font-medium">Próxima cuota</th>
              <th className="px-3 py-2.5 font-medium">Valor cuota</th>
              <th className="px-5 py-2.5 font-medium">Estado</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.creditId}
                className="border-b border-gray-100 last:border-0 dark:border-gray-800"
              >
                <td className="px-5 py-3">
                  <div className="flex items-center gap-2.5">
                    <span
                      className={`size-2.5 shrink-0 rounded-full ${getCreditTypeStyle(row.creditType).dotClass}`}
                    />
                    <div className="min-w-0">
                      <p className="truncate text-sm text-gray-800 dark:text-white/90">
                        {creditTypeLabels[row.creditType] ?? row.creditType}
                      </p>
                      <p className="truncate text-xs text-gray-400 dark:text-gray-500">
                        #{row.creditNumber}
                      </p>
                    </div>
                  </div>
                </td>
                <td className="px-3 py-3 text-sm text-gray-600 dark:text-gray-300">
                  {row.entityName}
                </td>
                <td className="px-3 py-3 text-sm text-gray-600 dark:text-gray-300">
                  {formatPaymentDate(row.nextDueDate)}
                </td>
                <td className="px-3 py-3 text-sm font-medium text-gray-800 dark:text-white/90">
                  {formatCreditCurrency(row.installmentAmount, row.currencyCode)}
                </td>
                <td className="px-5 py-3">
                  {/* La mora manda sobre el estado de la cuota: una cuota "por vencer"
                      en un crédito en mora se lee como vencida. */}
                  {row.isOverdue ? (
                    <span className="inline-flex rounded-full bg-error-50 px-2.5 py-1 text-xs font-medium text-error-600 dark:bg-error-500/10 dark:text-error-400">
                      Vencido
                    </span>
                  ) : row.status ? (
                    <span className="inline-flex rounded-full bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700 dark:bg-brand-500/15 dark:text-brand-400">
                      {paymentStatusLabels[row.status] ?? row.status}
                    </span>
                  ) : (
                    <span className="inline-flex rounded-full bg-success-50 px-2.5 py-1 text-xs font-medium text-success-700 dark:bg-success-500/10 dark:text-success-400">
                      Al día
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )}

    <div className="px-5 py-4">
      <Link
        to="/my-credits"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
      >
        Ver todas mis obligaciones
        <ArrowRight size={15} />
      </Link>
    </div>
  </section>
);
