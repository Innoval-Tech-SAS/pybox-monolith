import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import esLocale from "@fullcalendar/core/locales/es";
import { Modal } from "@/ui/components/modal/modal";
import { useCampaignCalendar } from "@/campaigns/hooks/use-campaign-calendar";
import { CAMPAIGN_PERIODICITY_LABELS, CAMPAIGN_STATUS_META } from "@/campaigns/constants/campaign-calendar-meta";
import { formatCampaignDateTime, isCampaignScheduleValid } from "@/campaigns/utils/campaign-utils";
import { StepSchedule } from "./campaign-form/step-schedule";
import type { CampaignsCalendarProps } from "@/campaigns/types/campaigns-calendar-props";

export const CampaignsCalendar: React.FC<CampaignsCalendarProps> = ({ organizationId, isAdmin }) => {
  const {
    events,
    loading,
    error,
    refetch,
    isOpen,
    selected,
    form,
    loadingDetail,
    saving,
    canEdit,
    recurringPeriodicities,
    weekdays,
    handleDatesSet,
    handleClick,
    setField,
    handleSave,
    handleClose,
  } = useCampaignCalendar(organizationId, isAdmin);

  return (
    <>
      {error && (
        <div className="mb-3 flex items-center justify-between gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-2 dark:border-red-800 dark:bg-red-900/20">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button
            type="button"
            onClick={refetch}
            className="rounded-lg bg-red-100 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300"
          >
            Reintentar
          </button>
        </div>
      )}

      <div className="relative rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/3">
        {loading && (
          <div className="absolute right-4 top-4 z-10 text-xs text-gray-400 dark:text-gray-500">
            Cargando…
          </div>
        )}
        <div className="custom-calendar">
          <FullCalendar
            plugins={[dayGridPlugin]}
            initialView="dayGridMonth"
            locale={esLocale}
            headerToolbar={{
              left: "prev,next",
              center: "title",
              right: "dayGridMonth,dayGridWeek,dayGridDay",
            }}
            events={events}
            eventClick={handleClick}
            datesSet={handleDatesSet}
            dayMaxEvents={3}
            moreLinkClick="popover"
            height="auto"
            contentHeight="auto"
          />
        </div>
      </div>

      <Modal isOpen={isOpen} onClose={handleClose} className="max-w-150 p-6 lg:p-8">
        {selected && (
          <div className="flex max-h-[80vh] flex-col overflow-y-auto px-2 custom-scrollbar">
            <div>
              <h5 className="mb-2 font-semibold text-gray-800 modal-title text-theme-xl dark:text-white/90 lg:text-2xl">
                {selected.campaignName}
              </h5>
              <span
                className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${CAMPAIGN_STATUS_META[selected.status].chipClass}`}
              >
                {CAMPAIGN_STATUS_META[selected.status].label}
              </span>
            </div>

            {canEdit ? (
              loadingDetail || !form ? (
                <p className="mt-6 text-sm text-gray-500 dark:text-gray-400">Cargando programación…</p>
              ) : (
                <>
                  <div className="mt-6">
                    <StepSchedule
                      form={form}
                      recurringPeriodicities={recurringPeriodicities}
                      weekdays={weekdays}
                      set={setField}
                    />
                  </div>
                  <div className="mt-6 flex justify-end gap-3">
                    <button
                      onClick={handleClose}
                      type="button"
                      disabled={saving}
                      className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/3"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={handleSave}
                      type="button"
                      disabled={saving || !isCampaignScheduleValid(form)}
                      className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50"
                    >
                      {saving ? "Guardando…" : "Guardar cambios"}
                    </button>
                  </div>
                </>
              )
            ) : (
              <>
                <div className="mt-6 space-y-4">
                  <div>
                    <p className="mb-1 text-xs font-medium text-gray-500 dark:text-gray-400">Ejecución</p>
                    <p className="text-sm text-gray-800 dark:text-white/90">{formatCampaignDateTime(selected.occursAt)}</p>
                  </div>
                  <div>
                    <p className="mb-1 text-xs font-medium text-gray-500 dark:text-gray-400">Periodicidad</p>
                    <p className="text-sm text-gray-800 dark:text-white/90">
                      {selected.isImmediate
                        ? "Inmediata"
                        : selected.periodicity
                          ? CAMPAIGN_PERIODICITY_LABELS[selected.periodicity]
                          : "—"}
                    </p>
                  </div>
                </div>
                <div className="mt-6 flex justify-end">
                  <button
                    onClick={handleClose}
                    type="button"
                    className="flex justify-center rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/3"
                  >
                    Cerrar
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </Modal>
    </>
  );
};
