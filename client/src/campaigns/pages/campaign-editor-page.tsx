import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { Select } from "@/ui/components/inputs/select";
import { Switch } from "@/ui/components/switch";
import { useApiClient } from "@/hooks/use-api-client";
import { useSegments } from "@/segments/hooks/use-segments";
import { useTemplates } from "@/templates/hooks/use-templates";
import { useChannels } from "../hooks/use-channels";
import { useCampaignPeriodicities } from "../hooks/use-campaign-periodicities";
import { useCampaignWeekdays } from "../hooks/use-campaign-weekdays";
import type { Campaign } from "@/types/campaigns/campaign-types";
import type {
  CampaignEditorFormState,
  CampaignFrequency,
  RecurringPeriodicity,
} from "@/campaigns/types/campaign-editor-form-state";

const EMPTY: CampaignEditorFormState = {
  name: "",
  description: "",
  channelId: "",
  segmentId: "",
  templateId: "",
  message: "",
  subject: "",
  fallback: true,
  timezone: "UTC",
  frequency: "immediate",
  recurringPeriodicity: "weekly",
  scheduledAt: "",
  timeToSend: "",
  daysOfWeek: [],
};

export const CampaignEditorPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const navigate = useNavigate();
  const { apiClient } = useApiClient();
  const isEditing = !!id;

  const { segments } = useSegments(orgId);
  const { items: templates } = useTemplates(orgId);
  const { channels } = useChannels();
  const { periodicities } = useCampaignPeriodicities(orgId);
  const { weekdays } = useCampaignWeekdays(orgId);
  const recurringPeriodicities = periodicities.filter(
    (p) => p.value === "daily" || p.value === "weekly" || p.value === "monthly",
  );

  const [form, setForm] = useState<CampaignEditorFormState>(EMPTY);
  const [loadingCampaign, setLoadingCampaign] = useState(isEditing);
  const [saving, setSaving] = useState(false);

  const backPath = `/my-companies/campaigns?org=${orgId}`;

  const selectedChannel = channels.find((c) => c.id === form.channelId);
  const channelName = selectedChannel?.name;

  // Plantillas: solo EMAIL/SMS existen hoy; WHATSAPP/CALL no tiene plantillas
  // compatibles todavía (se envía el mensaje libre).
  const compatibleTemplates = templates.filter((t) => t.channel === channelName);

  useEffect(() => {
    if (form.templateId && !compatibleTemplates.some((t) => t.id === form.templateId)) {
      setForm((prev) => ({ ...prev, templateId: "" }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.channelId, templates]);

  useEffect(() => {
    if (!isEditing && !form.channelId && channels.length > 0) {
      setForm((prev) => ({ ...prev, channelId: channels[0].id }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [channels]);

  useEffect(() => {
    if (!isEditing || !orgId) return;
    apiClient(`/campaigns/${id}?organizationId=${orgId}`, { method: "GET" })
      .then((c: Campaign) => {
        const frequency: CampaignFrequency = c.isImmediate
          ? "immediate"
          : c.periodicity === "once"
            ? "once"
            : "periodic";
        const recurringPeriodicity: RecurringPeriodicity =
          c.periodicity === "daily" || c.periodicity === "weekly" || c.periodicity === "monthly"
            ? c.periodicity
            : "weekly";
        setForm({
          name: c.name,
          description: c.description ?? "",
          channelId: c.channelId,
          segmentId: c.segmentId ?? "",
          templateId: c.templateId ?? "",
          message: c.message,
          subject: c.subject ?? "",
          fallback: c.fallback,
          timezone: c.timezone,
          frequency,
          recurringPeriodicity,
          scheduledAt: c.scheduledAt ? c.scheduledAt.slice(0, 16) : "",
          timeToSend: c.timeToSend ? c.timeToSend.slice(0, 5) : "",
          daysOfWeek: c.daysOfWeek ?? [],
        });
      })
      .catch(() => navigate(backPath))
      .finally(() => setLoadingCampaign(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const set = <K extends keyof CampaignEditorFormState>(key: K) =>
    (value: CampaignEditorFormState[K]) =>
      setForm((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    const isImmediate = form.frequency === "immediate";
    const periodicity =
      form.frequency === "immediate"
        ? "immediate"
        : form.frequency === "once"
          ? "once"
          : form.recurringPeriodicity;
    const showsSubject = channelName === "EMAIL";

    const payload = {
      name: form.name.trim(),
      description: form.description.trim() || null,
      channelId: form.channelId,
      segmentId: form.segmentId || null,
      templateId: form.templateId || null,
      message: form.message,
      subject: showsSubject ? form.subject.trim() || null : null,
      fallback: form.fallback,
      timezone: form.timezone.trim() || "UTC",
      isImmediate,
      periodicity,
      scheduledAt:
        form.frequency === "once" && form.scheduledAt
          ? new Date(form.scheduledAt).toISOString()
          : null,
      timeToSend: form.frequency === "periodic" && form.timeToSend ? `${form.timeToSend}:00` : null,
      daysOfWeek:
        form.frequency === "periodic" && form.recurringPeriodicity === "weekly" && form.daysOfWeek.length > 0
          ? form.daysOfWeek
          : null,
    };

    try {
      if (isEditing) {
        await apiClient(`/campaigns/${id}?organizationId=${orgId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        await apiClient(`/campaigns/?organizationId=${orgId}`, {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      navigate(backPath);
    } finally {
      setSaving(false);
    }
  };

  const showsSubject = channelName === "EMAIL";
  const pageTitle = isEditing ? "Editar campaña" : "Nueva campaña";

  if (loadingCampaign) {
    return (
      <ModuleBase pageTitle={pageTitle} breadcrumbItems={[]}>
        <div className="py-24">
          <Loader loaderText="Cargando campaña..." />
        </div>
      </ModuleBase>
    );
  }

  return (
    <>
      <PageMeta title={pageTitle} description="Editor de campañas de SMS y correo" />
      <ModuleBase
        pageTitle={pageTitle}
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          { label: "Campañas", path: backPath },
        ]}
      >
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <Card>
            <CardTitle>Configuración</CardTitle>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <Input
                  label="Nombre *"
                  id="cmp-name"
                  value={form.name}
                  onChange={(e) => set("name")(e.target.value)}
                  placeholder="Ej: Recuperación preventiva"
                />
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                  Canal
                </label>
                <Select
                  options={channels.map((c) => ({ value: c.id, label: c.label }))}
                  value={form.channelId}
                  onChange={(v) => set("channelId")(v)}
                />
              </div>

              <div className="sm:col-span-2 lg:col-span-3">
                <Input
                  label="Descripción"
                  id="cmp-description"
                  value={form.description}
                  onChange={(e) => set("description")(e.target.value)}
                  placeholder="Una breve descripción"
                />
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                  Segmento de destinatarios
                </label>
                <Select
                  options={segments.map((s) => ({ value: String(s.id), label: s.name }))}
                  value={form.segmentId}
                  onChange={(v) => set("segmentId")(v)}
                  placeholder="Selecciona un segmento"
                />
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                  Plantilla
                </label>
                <Select
                  options={compatibleTemplates.map((t) => ({ value: t.id, label: t.name }))}
                  value={form.templateId}
                  onChange={(v) => set("templateId")(v)}
                  placeholder="Ninguna (usar mensaje manual)"
                  disabled={compatibleTemplates.length === 0}
                />
                {compatibleTemplates.length === 0 && (
                  <p className="mt-1.5 text-xs text-gray-400 dark:text-gray-500">
                    No hay plantillas para este canal.
                  </p>
                )}
              </div>

              <div>
                <Input
                  label="Zona horaria"
                  id="cmp-timezone"
                  value={form.timezone}
                  onChange={(e) => set("timezone")(e.target.value)}
                  placeholder="UTC"
                />
              </div>

              {showsSubject && (
                <div className="sm:col-span-2 lg:col-span-2">
                  <Input
                    label="Asunto"
                    id="cmp-subject"
                    value={form.subject}
                    onChange={(e) => set("subject")(e.target.value)}
                    placeholder="Ej: Tu factura {invoice} está lista"
                  />
                </div>
              )}

              <div className="flex items-end pb-2.5">
                <Switch
                  checked={form.fallback}
                  onChange={set("fallback")}
                  label="Usar canal de respaldo si falla el envío"
                />
              </div>

              <div className="sm:col-span-2 lg:col-span-3">
                <label htmlFor="cmp-message" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                  Mensaje *
                </label>
                <textarea
                  id="cmp-message"
                  rows={5}
                  value={form.message}
                  onChange={(e) => set("message")(e.target.value)}
                  placeholder="Contenido del mensaje. Usa {variable} para datos del destinatario."
                  className="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
                />
              </div>
            </div>
          </Card>

          <Card>
            <CardTitle>Programación</CardTitle>
            <div className="flex flex-col gap-4">
              <div className="flex flex-wrap gap-2">
                {([
                  { value: "immediate", label: "Envío inmediato" },
                  { value: "once", label: "Envío único" },
                  { value: "periodic", label: "Envío recurrente" },
                ] as const).map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => set("frequency")(opt.value)}
                    className={`rounded-lg px-4 py-2.5 text-sm font-medium ${
                      form.frequency === opt.value
                        ? "bg-brand-500 text-white"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>

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
                <div className="flex flex-wrap gap-4">
                  <div className="w-full max-w-xs">
                    <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                      Tipo de recurrencia
                    </label>
                    <Select
                      options={recurringPeriodicities.map((p) => ({ value: p.value, label: p.label }))}
                      value={form.recurringPeriodicity}
                      onChange={(v) => set("recurringPeriodicity")(v as RecurringPeriodicity)}
                    />
                  </div>
                  <div className="w-full max-w-xs">
                    <Input
                      label="Hora de envío"
                      id="cmp-time-to-send"
                      type="time"
                      value={form.timeToSend}
                      onChange={(e) => set("timeToSend")(e.target.value)}
                    />
                  </div>

                  {form.recurringPeriodicity === "weekly" && (
                    <div className="w-full">
                      <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
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
                              className={`h-9 w-12 rounded-lg text-xs font-medium disabled:cursor-not-allowed disabled:opacity-40 ${
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
            </div>
          </Card>

          <div className="flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={() => navigate(backPath)}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving || !form.name.trim() || !form.message.trim()}
              className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
            >
              {saving
                ? isEditing ? "Guardando…" : "Creando…"
                : isEditing ? "Guardar cambios" : "Crear campaña"}
            </button>
          </div>
        </form>
      </ModuleBase>
    </>
  );
};
