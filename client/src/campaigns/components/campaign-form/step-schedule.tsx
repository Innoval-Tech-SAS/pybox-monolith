import { Zap, CalendarClock, Repeat } from "lucide-react";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { Select } from "@/ui/components/inputs/select";
import { SCHEDULE_FREQUENCY_OPTIONS } from "@/campaigns/constants/campaign-wizard-options";
import type { StepScheduleProps } from "@/campaigns/types/step-schedule-props";
import type { CampaignFrequency, RecurringPeriodicity } from "@/campaigns/types/campaign-editor-form-state";

const FREQUENCY_ICONS: Record<CampaignFrequency, typeof Zap> = {
  immediate: Zap,
  once: CalendarClock,
  periodic: Repeat,
};

export const StepSchedule: React.FC<StepScheduleProps> = ({ form, recurringPeriodicities, weekdays, set }) => (
  <div className="flex h-full flex-col gap-5">
    <Card>
      <CardTitle>¿Cuándo se envía?</CardTitle>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {SCHEDULE_FREQUENCY_OPTIONS.map((opt) => {
          const Icon = FREQUENCY_ICONS[opt.value];
          const active = form.frequency === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => set("frequency")(opt.value)}
              className={`flex flex-col items-start gap-2 rounded-xl border p-4 text-left transition ${
                active
                  ? "border-brand-500 bg-brand-50 dark:border-brand-500 dark:bg-brand-500/10"
                  : "border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600"
              }`}
            >
              <span
                className={`flex h-9 w-9 items-center justify-center rounded-lg ${
                  active
                    ? "bg-brand-500 text-white"
                    : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                }`}
              >
                <Icon size={18} />
              </span>
              <span
                className={`text-sm font-semibold ${
                  active ? "text-brand-700 dark:text-brand-300" : "text-gray-800 dark:text-white/90"
                }`}
              >
                {opt.label}
              </span>
              <span className="text-xs text-gray-400 dark:text-gray-500">{opt.helper}</span>
            </button>
          );
        })}
      </div>
    </Card>

    {form.frequency !== "immediate" && (
      <Card>
        <CardTitle>{form.frequency === "once" ? "Fecha de envío" : "Frecuencia de envío"}</CardTitle>

        {form.frequency === "once" && (
          <div className="max-w-xs">
            <Input
              label="Fecha y hora de envío"
              id="cmp-scheduled-at"
              type="datetime-local"
              value={form.scheduledAt}
              onChange={(e) => set("scheduledAt")(e.target.value)}
            />
          </div>
        )}

        {form.frequency === "periodic" && (
          <div className="flex flex-col gap-5">
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                  Tipo de recurrencia
                </label>
                <Select
                  options={recurringPeriodicities.map((p) => ({ value: p.value, label: p.label }))}
                  value={form.recurringPeriodicity}
                  onChange={(v) => set("recurringPeriodicity")(v as RecurringPeriodicity)}
                />
              </div>
              <Input
                label="Hora de envío"
                id="cmp-time-to-send"
                type="time"
                value={form.timeToSend}
                onChange={(e) => set("timeToSend")(e.target.value)}
              />
            </div>

            {form.recurringPeriodicity === "weekly" && (
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-400">
                  Días de la semana
                </label>
                <div className="flex flex-wrap gap-2">
                  {weekdays.map((day) => {
                    const checked = form.daysOfWeek.includes(day.value);
                    return (
                      <button
                        key={day.value}
                        type="button"
                        disabled={!day.active}
                        title={day.active ? undefined : "No disponible"}
                        onClick={() =>
                          set("daysOfWeek")(
                            checked
                              ? form.daysOfWeek.filter((d) => d !== day.value)
                              : [...form.daysOfWeek, day.value].sort(),
                          )
                        }
                        className={`h-10 w-12 rounded-lg text-xs font-medium transition disabled:cursor-not-allowed disabled:opacity-40 ${
                          checked
                            ? "bg-brand-500 text-white"
                            : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300"
                        }`}
                      >
                        {day.label.slice(0, 3)}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </Card>
    )}
  </div>
);
