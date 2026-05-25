import { useMemo, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import esLocale from "@fullcalendar/core/locales/es";
import type { EventClickArg, EventInput } from "@fullcalendar/core";
import type { CreditWithPayments, PaymentSummary } from "@/credits/types/credit-types";
import type { FinancialCalendarEvent, FinancialPaymentStatus } from "@/credits/types/financial-calendar-types";
import type { CalendarProps } from "@/types/props/calendar-props";
import { STATUS_META } from "@/constants/credits/financial-calendar";

const toValidDate = (value: string | null): Date | null => {
  if (!value) return null;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
};

const toDateOnlyIso = (d: Date): string => {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
};

const isPastDue = (limitPayDate: string): boolean => {
  const limit = toValidDate(limitPayDate);
  if (!limit) return false;
  const now = new Date();
  const endOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);
  return limit.getTime() < endOfToday.getTime();
};

const getExpected = (p: PaymentSummary): number =>
  p.principalPayment + p.totalInterestAmount + p.otherCharges;

const isPartial = (p: PaymentSummary): boolean => {
  const expected = getExpected(p);
  return expected > 0 && p.paymentAmount > 0 && p.paymentAmount < expected;
};

const formatDate = (value: string | null): string => {
  if (!value) return "Sin fecha";
  const d = toValidDate(value);
  if (!d) return "Sin fecha";
  return d.toLocaleDateString("es-CO", { year: "numeric", month: "short", day: "numeric" });
};

const formatCurrency = (amount: number, code: string): string => {
  const currency = code || "COP";
  try {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency,
      maximumFractionDigits: 2,
    }).format(amount);
  } catch {
    return `${currency} ${amount.toLocaleString("es-CO")}`;
  }
};

const buildEvents = (credits: CreditWithPayments[]): EventInput[] => {
  const events: EventInput[] = [];

  credits.forEach((credit) => {
    const candidates = credit.payments
      .filter((p) => !p.paymentDate)
      .map((p) => ({ p, d: toValidDate(p.limitPayDate) }))
      .filter((x) => !!x.d)
      .sort((a, b) => a.d!.getTime() - b.d!.getTime());

    const next = candidates[0];
    if (next?.d) {
      const status: FinancialPaymentStatus = isPastDue(next.p.limitPayDate) ? "overdue" : "onTime";
      const meta = STATUS_META[status];
      events.push({
        id: `upcoming-${credit.id}-${next.p.id}`,
        title: `${credit.creditNumber} · ${meta.label}`,
        date: toDateOnlyIso(next.d),
        color: meta.eventColor,
        textColor: meta.eventTextColor,
        extendedProps: { type: "upcoming", status, credit, payment: next.p } as FinancialCalendarEvent,
      });
    }

    credit.payments
      .filter((p) => !!p.paymentDate)
      .forEach((p) => {
        const paidDate = toValidDate(p.paymentDate);
        if (!paidDate) return;
        const status: FinancialPaymentStatus = isPartial(p) ? "partialPaid" : "totalPaid";
        const meta = STATUS_META[status];
        events.push({
          id: `history-${credit.id}-${p.id}`,
          title: `${credit.creditNumber} · ${meta.label}`,
          date: toDateOnlyIso(paidDate),
          color: meta.eventColor,
          textColor: meta.eventTextColor,
          extendedProps: { type: "history", status, credit, payment: p } as FinancialCalendarEvent,
        });
      });
  });

  return events;
};

export const Calendar: React.FC<CalendarProps> = ({
  credits,
  loading = false,
  error = null,
  onRetry,
}) => {
  const [selected, setSelected] = useState<FinancialCalendarEvent | null>(null);
  const events = useMemo(() => buildEvents(credits), [credits]);

  const handleClick = (info: EventClickArg) => {
    setSelected(info.event.extendedProps as FinancialCalendarEvent);
  };

  if (loading) {
    return (
      <div className="flex min-h-72 items-center justify-center rounded-lg border border-gray-200 bg-white p-8 dark:border-gray-800 dark:bg-gray-900">
        <p className="text-sm text-gray-500 dark:text-gray-400">Cargando calendario financiero...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col gap-3 rounded-lg border border-red-200 bg-white p-6 dark:border-red-800 dark:bg-gray-900">
        <p className="text-sm font-semibold text-red-700 dark:text-red-400">
          No se pudo cargar el calendario financiero
        </p>
        <p className="text-sm text-red-600 dark:text-red-500">{error}</p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="self-start rounded-lg bg-red-100 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300"
          >
            Reintentar
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-theme-xs dark:border-gray-800 dark:bg-gray-900">
        <div className="p-4 sm:p-6">
          <FullCalendar
            plugins={[dayGridPlugin]}
            initialView="dayGridMonth"
            locale={esLocale}
            headerToolbar={{ left: "prev,next", center: "title", right: "" }}
            events={events}
            eventClick={handleClick}
            dayMaxEvents={3}
            moreLinkClick="popover"
            height="auto"
            contentHeight="auto"
          />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900">
          <p className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">Leyenda</p>
          {(Object.entries(STATUS_META) as [FinancialPaymentStatus, typeof STATUS_META[FinancialPaymentStatus]][]).map(
            ([, meta]) => (
              <div key={meta.label} className="mb-2 flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <span className={`size-2.5 rounded-full ${meta.dotClass}`} />
                {meta.label}
              </div>
            ),
          )}
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900">
          <p className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">Detalle del evento</p>
          {!selected ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Selecciona un evento en el calendario para ver el detalle.
            </p>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center justify-between gap-3">
                <p className="text-base font-semibold text-gray-800 dark:text-white/90">
                  {selected.credit.creditNumber}
                </p>
                <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_META[selected.status].chipClass}`}>
                  {STATUS_META[selected.status].label}
                </span>
              </div>
              {selected.credit.organizationName && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {selected.credit.organizationName}
                </p>
              )}
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Cuota #{selected.payment.installmentNumber ?? selected.payment.id}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Fecha límite: {formatDate(selected.payment.limitPayDate)}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Fecha de pago: {formatDate(selected.payment.paymentDate)}
              </p>
              <p className="text-sm font-medium text-gray-800 dark:text-white/90">
                Valor: {formatCurrency(selected.payment.paymentAmount, selected.credit.currencyCode)}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
