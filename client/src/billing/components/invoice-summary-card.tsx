import { RefreshCw } from "lucide-react";
import { InvoiceStatusBadge } from "./invoice-status-badge";
import { formatCop, formatPeriod, formatUsd } from "../utils/format-currency";
import type { AdminInvoice } from "@/types/billing/billing-types";
import type { InvoiceSummaryCardProps } from "../types/props/invoice-summary-card-props";

export const InvoiceSummaryCard: React.FC<InvoiceSummaryCardProps> = ({
  invoice,
  isAdminMode,
  syncing,
  onSync,
}) => {
  const organizationName = (invoice as AdminInvoice).organizationName;

  return (
    <div className="rounded-xl border border-gray-200 p-5 dark:border-gray-800">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          {organizationName && (
            <p className="text-xs uppercase tracking-wide text-gray-400">{organizationName}</p>
          )}
          <p className="text-lg font-semibold text-gray-800 dark:text-white/90">
            {formatPeriod(invoice.periodYear, invoice.periodMonth)}
          </p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white/90">{formatCop(invoice.totalAmount)}</p>
          <p className="text-xs text-gray-400">
            Subtotal {formatUsd(invoice.subtotalBaseAmount)} · TRM {invoice.exchangeRate} · Impuesto{" "}
            {formatCop(invoice.taxAmount)}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <InvoiceStatusBadge status={invoice.status} />
          {!isAdminMode && (
            <button
              type="button"
              onClick={onSync}
              disabled={syncing}
              title="Actualizar estado"
              className="rounded-lg border border-gray-200 p-2 text-gray-500 hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-white/5"
            >
              <RefreshCw size={16} className={syncing ? "animate-spin" : ""} />
            </button>
          )}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        <div>
          <p className="text-xs text-gray-400">Emitida</p>
          <p className="text-gray-700 dark:text-gray-300">
            {invoice.issuedAt ? new Date(invoice.issuedAt).toLocaleDateString("es-CO") : "—"}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400">Vence</p>
          <p className="text-gray-700 dark:text-gray-300">
            {invoice.dueAt ? new Date(invoice.dueAt).toLocaleDateString("es-CO") : "—"}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400">Bloqueo</p>
          <p className="text-gray-700 dark:text-gray-300">
            {invoice.blockAt ? new Date(invoice.blockAt).toLocaleDateString("es-CO") : "—"}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400">Pagada</p>
          <p className="text-gray-700 dark:text-gray-300">
            {invoice.paidAt ? new Date(invoice.paidAt).toLocaleDateString("es-CO") : "—"}
          </p>
        </div>
      </div>
    </div>
  );
};
