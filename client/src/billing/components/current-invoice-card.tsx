import { InvoiceStatusBadge } from "./invoice-status-badge";
import { Button } from "@/ui/components/button/button";
import { formatCop, formatPeriod } from "../utils/format-currency";
import type { CurrentInvoiceCardProps } from "../types/props/current-invoice-card-props";

export const CurrentInvoiceCard: React.FC<CurrentInvoiceCardProps> = ({ invoice, onViewDetail }) => (
  <div className="rounded-xl border border-gray-200 p-5 dark:border-gray-800">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p className="text-xs uppercase tracking-wide text-gray-400">Factura vigente</p>
        <p className="text-lg font-semibold text-gray-800 dark:text-white/90">
          {formatPeriod(invoice.periodYear, invoice.periodMonth)}
        </p>
        <p className="text-2xl font-bold text-gray-800 dark:text-white/90">{formatCop(invoice.totalAmount)}</p>
      </div>
      <div className="flex items-center gap-3">
        <InvoiceStatusBadge status={invoice.status} />
        <Button type="button" size="sm" onClick={onViewDetail}>
          Ver detalle
        </Button>
      </div>
    </div>
  </div>
);
