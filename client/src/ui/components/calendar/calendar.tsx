import { useEffect, useMemo, useRef, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import listPlugin from "@fullcalendar/list";
import esLocale from "@fullcalendar/core/locales/es";
import type { DayCellContentArg, EventClickArg, EventContentArg } from "@fullcalendar/core";
import type { FinancialCalendarEvent } from "@/credits/types/financial-calendar-types";
import type { CalendarProps } from "@/types/props/calendar-props";
import { buildFinancialCalendarEvents, toDateOnlyIso } from "@/credits/utils/financial-calendar-utils";
import { getCreditTypeStyle } from "@/constants/credits/financial-calendar";
import { useCreditTypes } from "@/credits/hooks/use-credit-types";
import { useSidebar } from "@/hooks/use-sidebar";
import { Modal } from "@/ui/components/modal/modal";
import { CalendarEventCard } from "@/ui/components/calendar/calendar-event-card";
import { CalendarLegend } from "@/ui/components/calendar/calendar-legend";
import { FinancialEventDetails } from "@/ui/components/calendar/financial-event-details";
import { useModal } from "@/hooks/use-modal";
import { Loader } from "@/ui/components/loader/loader";

export const Calendar: React.FC<CalendarProps> = ({
  credits,
  loading = false,
  error = null,
  onRetry,
  entityLabel,
}) => {
  const [selected, setSelected] = useState<FinancialCalendarEvent | null>(null);
  const { isOpen, openModal, closeModal } = useModal();
  const { types: creditTypes, labels: creditTypeLabels } = useCreditTypes();
  const events = useMemo(() => buildFinancialCalendarEvents(credits), [credits]);
  const { isMobile } = useSidebar();
  const calendarRef = useRef<FullCalendar>(null);

  // El grid mensual (7 columnas) necesita min-width: 718px (index.css) para que las
  // tarjetas de evento sean legibles — no entra en ningún celular en vertical. Por
  // debajo de `md` se cambia a una vista de lista (mismo mes, sin scroll horizontal).
  // `initialView` de FullCalendar solo aplica al primer montaje, así que un resize o
  // rotación de pantalla posterior necesita el cambio de vista imperativo vía la API.
  useEffect(() => {
    calendarRef.current?.getApi().changeView(isMobile ? "listMonth" : "dayGridMonth");
  }, [isMobile]);

  // Color del círculo del día: el del tipo de la primera obligación de esa fecha.
  // Se precalcula porque `dayCellContent` corre por celda en cada render.
  const accentByDate = useMemo(() => {
    const map = new Map<string, string>();
    events.forEach((event) => {
      const date = typeof event.date === "string" ? event.date : null;
      const credit = (event.extendedProps as FinancialCalendarEvent | undefined)?.credit;
      if (!date || !credit || map.has(date)) return;
      map.set(date, getCreditTypeStyle(credit.creditType).accent);
    });
    return map;
  }, [events]);

  const handleClick = (info: EventClickArg) => {
    setSelected(info.event.extendedProps as FinancialCalendarEvent);
    openModal();
  };

  const handleClose = () => {
    closeModal();
    setSelected(null);
  };

  const renderEvent = (arg: EventContentArg) => {
    const event = arg.event.extendedProps as FinancialCalendarEvent;
    // Defensivo: devolver null haría caer a FullCalendar en su render por defecto,
    // que el CSS del calendario financiero oculta — quedaría una tarjeta vacía.
    if (!event?.credit) {
      return <span className="px-2 text-[11px] text-gray-500">{arg.event.title}</span>;
    }
    return (
      <CalendarEventCard
        event={event}
        creditTypeLabel={creditTypeLabels[event.credit.creditType] ?? event.credit.creditType}
      />
    );
  };

  const renderDayCell = (arg: DayCellContentArg) => {
    const accent = accentByDate.get(toDateOnlyIso(arg.date));
    if (!accent) return <span className="fc-day-number">{arg.dayNumberText}</span>;
    return (
      <span
        className="fc-day-number fc-day-number--marked"
        style={{ backgroundColor: accent }}
      >
        {arg.dayNumberText}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex min-h-72 items-center justify-center rounded-2xl border border-gray-200 bg-white p-8 dark:border-gray-800 dark:bg-white/3">
        <Loader loaderText="Cargando calendario..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col gap-3 rounded-2xl border border-red-200 bg-white p-6 dark:border-red-800 dark:bg-white/3">
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
    <>
      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/3">
        {/* `financial-calendar` scopea los estilos del mockup: `custom-calendar` solo
            lo comparte con el calendario de campañas, que usa el render por defecto. */}
        <div className="custom-calendar financial-calendar">
          <FullCalendar
            ref={calendarRef}
            plugins={[dayGridPlugin, listPlugin]}
            initialView={isMobile ? "listMonth" : "dayGridMonth"}
            locale={esLocale}
            headerToolbar={{
              left: "prev,next",
              center: "title",
              right: "today",
            }}
            buttonText={{ today: "Hoy" }}
            events={events}
            displayEventTime={false}
            eventClick={handleClick}
            eventContent={renderEvent}
            dayCellContent={renderDayCell}
            dayMaxEvents={3}
            moreLinkClick="popover"
            moreLinkText={(n) => `+${n} más`}
            fixedWeekCount={false}
            height="auto"
            contentHeight="auto"
          />
        </div>
        <CalendarLegend creditTypes={creditTypes} />
      </div>

      <Modal isOpen={isOpen} onClose={handleClose} className="max-w-2xl mx-4 flex max-h-[90vh] flex-col p-6 lg:p-10">
        {selected && (
          <FinancialEventDetails
            event={selected}
            onClose={handleClose}
            onActionDone={onRetry}
            entityLabel={entityLabel}
          />
        )}
      </Modal>
    </>
  );
};
