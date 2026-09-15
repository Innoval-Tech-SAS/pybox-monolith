import type { CalendarEventCardProps } from "@/types/props/calendar-event-card-props";
import { getCreditTypeStyle } from "@/constants/credits/financial-calendar";
import { formatCreditCurrency, getEventAmount } from "@/credits/utils/financial-calendar-utils";

/**
 * Tarjeta de una obligación dentro de una celda del calendario: tipo, monto y entidad.
 * Reemplaza el pill de texto que FullCalendar pinta por defecto, vía `eventContent`.
 */
export const CalendarEventCard: React.FC<CalendarEventCardProps> = ({
  event,
  creditTypeLabel,
}) => {
  const { credit } = event;
  const style = getCreditTypeStyle(credit.creditType);
  const amount = formatCreditCurrency(getEventAmount(event), credit.currencyCode);
  const isPaid = event.type === "history";

  return (
    <div
      className={`w-full cursor-pointer overflow-hidden rounded-lg border px-2 py-1.5 text-left ${style.cardClass} ${isPaid ? "opacity-60" : ""}`}
      title={`${creditTypeLabel} · ${amount} · ${credit.organizationName}`}
    >
      <p className="truncate text-[11px] font-semibold leading-tight text-gray-800 dark:text-white/90">
        {creditTypeLabel}
      </p>
      <p className="truncate text-[11px] font-semibold leading-tight text-gray-900 dark:text-white">
        {amount}
      </p>
      <p className="truncate text-[10px] leading-tight text-gray-500 dark:text-gray-400">
        {credit.organizationName}
      </p>
    </div>
  );
};
