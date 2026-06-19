import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { WizardForm } from "@/ui/components/wizard-form";
import { useApiClient } from "@/hooks/use-api-client";
import { useCountries } from "@/hooks/use-countries";
import { useSegmentOptions } from "@/segments/hooks/use-segment-options";
import { useTemplateOptions } from "@/templates/hooks/use-template-options";
import { useTemplateVariables } from "@/templates/hooks/use-template-variables";
import { useChannels } from "../hooks/use-channels";
import { useCampaignPeriodicities } from "../hooks/use-campaign-periodicities";
import { useCampaignWeekdays } from "../hooks/use-campaign-weekdays";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { usePortfolios } from "@/companies/hooks/use-portfolios";
import { CAMPAIGN_WIZARD_STEPS } from "../constants/campaign-wizard-options";
import { StepDetails } from "../components/campaign-form/step-details";
import { StepMessage } from "../components/campaign-form/step-message";
import { StepSchedule } from "../components/campaign-form/step-schedule";
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
  dayOfMonth: null,
};

export const CampaignEditorPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId, orgName, buildOrgPath } = useOrgModule();
  const navigate = useNavigate();
  const { apiClient } = useApiClient();
  const isEditing = !!id;

  const { portfolios } = usePortfolios(orgId);
  const portfolio = portfolios.find((p) => p.id === portfolioId);
  const portfolioName = portfolio?.name ?? "Portafolio";
  const { countries } = useCountries();
  const portfolioTimezone = countries.find((c) => c.code === portfolio?.country)?.timezone ?? "UTC";

  const { segments } = useSegmentOptions(orgId);
  const { templates } = useTemplateOptions(orgId);
  const { variables } = useTemplateVariables(orgId);
  const { channels } = useChannels();
  const { periodicities } = useCampaignPeriodicities(orgId);
  const { weekdays } = useCampaignWeekdays(orgId);
  const recurringPeriodicities = periodicities.filter(
    (p) => p.value === "daily" || p.value === "weekly" || p.value === "monthly",
  );

  const [form, setForm] = useState<CampaignEditorFormState>(EMPTY);
  const [loadingCampaign, setLoadingCampaign] = useState(isEditing);
  const [saving, setSaving] = useState(false);

  const backPath = buildOrgPath("/my-companies/campaigns", { portfolio: portfolioId });

  // La campaña usa la zona horaria del país del portfolio donde se crea;
  // no se le pide al usuario.
  useEffect(() => {
    if (!isEditing) setForm((prev) => ({ ...prev, timezone: portfolioTimezone }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isEditing, portfolioTimezone]);

  const selectedChannel = channels.find((c) => c.id === form.channelId);
  const channelName = selectedChannel?.name;

  // Plantillas: solo EMAIL/SMS existen hoy; WHATSAPP/CALL no tiene plantillas
  // compatibles todavía (se envía el mensaje libre).
  const compatibleTemplates = templates.filter((t) => t.channel === channelName);
  const selectedTemplate = templates.find((t) => t.id === form.templateId) ?? null;
  const showsSubject = channelName === "EMAIL";

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

  // El mensaje siempre refleja el contenido de la plantilla elegida: no se
  // pide manualmente cuando hay una plantilla seleccionada.
  useEffect(() => {
    if (!form.templateId) return;
    const tpl = templates.find((t) => t.id === form.templateId);
    if (!tpl) return;
    setForm((prev) => ({
      ...prev,
      message: tpl.body,
      subject: prev.subject || (tpl.subject ?? ""),
    }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.templateId, templates]);

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
          dayOfMonth: c.dayOfMonth ?? null,
        });
      })
      .catch(() => navigate(backPath))
      .finally(() => setLoadingCampaign(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const set = <K extends keyof CampaignEditorFormState>(key: K) =>
    (value: CampaignEditorFormState[K]) =>
      setForm((prev) => ({ ...prev, [key]: value }));

  const detailsValid = form.name.trim() !== "" && !!form.channelId;
  const messageValid = !!selectedTemplate;
  const scheduleValid =
    form.frequency === "immediate"
      ? true
      : form.frequency === "once"
        ? !!form.scheduledAt
        : !!form.recurringPeriodicity &&
          !!form.timeToSend &&
          (form.recurringPeriodicity !== "weekly" || form.daysOfWeek.length > 0) &&
          (form.recurringPeriodicity !== "monthly" || !!form.dayOfMonth);

  const canSubmit = detailsValid && messageValid && scheduleValid;

  const canAdvance = (step: number) => {
    if (step === 0) return detailsValid;
    if (step === 1) return messageValid;
    return true;
  };

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
      dayOfMonth:
        form.frequency === "periodic" && form.recurringPeriodicity === "monthly" ? form.dayOfMonth : null,
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
          { label: orgName || "Empresa", path: buildOrgPath("/my-companies") },
          ...(portfolioId
            ? [
                { label: "Mis Portafolios", path: buildOrgPath("/my-companies/portfolios") },
                { label: portfolioName, path: buildOrgPath("/my-companies/portfolios", { portfolio: portfolioId }) },
                { label: "Comunicaciones", path: buildOrgPath("/my-companies/portfolios/communications", { portfolio: portfolioId }) },
              ]
            : []),
          { label: "Campañas", path: backPath },
        ]}
      >
        <WizardForm
          steps={CAMPAIGN_WIZARD_STEPS}
          orientation="vertical"
          canAdvance={canAdvance}
          canSubmit={canSubmit}
          onSubmit={handleSubmit}
          loading={saving}
          submitLabel={isEditing ? "Guardar cambios" : "Crear campaña"}
          loadingLabel={isEditing ? "Guardando…" : "Creando…"}
        >
          {(step) => (
            <>
              {step === 0 && <StepDetails form={form} channels={channels} set={set} />}

              {step === 1 && (
                <StepMessage
                  form={form}
                  segments={segments}
                  compatibleTemplates={compatibleTemplates}
                  selectedTemplate={selectedTemplate}
                  showsSubject={showsSubject}
                  variables={variables}
                  set={set}
                />
              )}

              {step === 2 && (
                <StepSchedule
                  form={form}
                  recurringPeriodicities={recurringPeriodicities}
                  weekdays={weekdays}
                  set={set}
                />
              )}
            </>
          )}
        </WizardForm>
      </ModuleBase>
    </>
  );
};
