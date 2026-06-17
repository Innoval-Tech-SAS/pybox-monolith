import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { Select } from "@/ui/components/inputs/select";
import { WizardForm } from "@/ui/components/wizard-form";
import { useApiClient } from "@/hooks/use-api-client";
import { TemplateEditor } from "../components/template-editor";
import { ChannelPicker } from "../components/channel-picker";
import { PlainTextTemplateDesigner } from "../components/plain-text-template-designer";
import { TemplatePreviewStep } from "../components/template-preview-step";
import {
  CHANNEL_CHAR_LIMITS,
  STATUS_OPTIONS,
  TEMPLATE_WIZARD_STEPS,
  UNAVAILABLE_CHANNELS,
} from "@/templates/constants/template-wizard-options";
import type { Template, TemplateStatus } from "@/types/templates/template-types";
import type { TemplateEditorFormState } from "@/templates/types/template-editor-form-state";

const EMPTY: TemplateEditorFormState = {
  name: "",
  channel: "EMAIL",
  status: "DRAFT",
  body: "",
  subject: "",
  senderName: "",
  senderEmail: "",
  replyTo: "",
};

export const TemplateEditorPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const navigate = useNavigate();
  const { apiClient } = useApiClient();
  const isEditing = !!id;

  const [form, setForm] = useState<TemplateEditorFormState>(EMPTY);
  const [loadingTemplate, setLoadingTemplate] = useState(isEditing);
  const [saving, setSaving] = useState(false);

  const backPath = `/my-companies/templates?org=${orgId}`;

  // En modo edición, cargar la plantilla existente
  useEffect(() => {
    if (!isEditing || !orgId) return;
    apiClient(`/templates/${id}?organizationId=${orgId}`, { method: "GET" })
      .then((t: Template) => {
        setForm({
          name: t.name,
          channel: t.channel,
          status: t.status,
          body: t.body,
          subject: t.subject ?? "",
          senderName: t.senderName ?? "",
          senderEmail: t.senderEmail ?? "",
          replyTo: t.replyTo ?? "",
        });
      })
      .catch(() => navigate(backPath))
      .finally(() => setLoadingTemplate(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const set = <K extends keyof TemplateEditorFormState>(key: K) =>
    (value: TemplateEditorFormState[K]) =>
      setForm((prev) => ({ ...prev, [key]: value }));

  const isEmail = form.channel === "EMAIL";
  const isUnavailable = UNAVAILABLE_CHANNELS.includes(form.channel);
  const charLimit = CHANNEL_CHAR_LIMITS[form.channel];
  const withinCharLimit = charLimit === undefined || form.body.length <= charLimit;

  const isDesignValid = !isUnavailable && form.body.trim() !== "" && withinCharLimit;

  const canAdvance = (step: number) => {
    if (step === 0) return true;
    if (step === 1) {
      if (!form.name.trim()) return false;
      if (isEmail) return !!form.subject.trim() && !!form.senderEmail.trim();
      return true;
    }
    if (step === 2) return isDesignValid;
    return false;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const payload = {
      name: form.name.trim(),
      channel: form.channel,
      status: form.status,
      body: form.body,
      subject: isEmail ? form.subject.trim() || null : null,
      senderName: form.senderName.trim() || null,
      senderEmail: isEmail ? form.senderEmail.trim() || null : null,
      replyTo: isEmail ? form.replyTo.trim() || null : null,
    };
    try {
      if (isEditing) {
        await apiClient(`/templates/${id}?organizationId=${orgId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        await apiClient(`/templates/?organizationId=${orgId}`, {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      navigate(backPath);
    } finally {
      setSaving(false);
    }
  };

  const pageTitle = isEditing ? "Editar plantilla" : "Nueva plantilla";

  if (loadingTemplate) {
    return (
      <ModuleBase pageTitle={pageTitle} breadcrumbItems={[]}>
        <div className="py-24">
          <Loader loaderText="Cargando plantilla..." />
        </div>
      </ModuleBase>
    );
  }

  return (
    <>
      <PageMeta title={pageTitle} description="Editor de plantillas" />
      <ModuleBase
        pageTitle={pageTitle}
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          { label: "Plantillas", path: backPath },
        ]}
      >
        <WizardForm
          steps={TEMPLATE_WIZARD_STEPS}
          canAdvance={canAdvance}
          canSubmit={isDesignValid}
          onSubmit={handleSubmit}
          loading={saving}
          submitLabel={isEditing ? "Guardar cambios" : "Crear plantilla"}
          loadingLabel={isEditing ? "Guardando…" : "Creando…"}
        >
          {(step) => (
            <>
              {step === 0 && (
                <Card>
                  <CardTitle>Canal de la plantilla</CardTitle>
                  <ChannelPicker
                    value={form.channel}
                    disabled={isEditing}
                    onChange={(channel) => set("channel")(channel)}
                  />
                </Card>
              )}

              {step === 1 && (
                <Card>
                  <CardTitle>Información de la plantilla</CardTitle>
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                    <div className="lg:col-span-2">
                      <Input
                        label="Nombre *"
                        id="tpl-name"
                        value={form.name}
                        onChange={(e) => set("name")(e.target.value)}
                        placeholder="Ej: Factura mensual"
                      />
                    </div>

                    <div>
                      <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                        Estado
                      </label>
                      <Select
                        options={STATUS_OPTIONS}
                        value={form.status}
                        onChange={(v) => set("status")(v as TemplateStatus)}
                      />
                    </div>

                    {isEmail && (
                      <>
                        <div className="sm:col-span-2 lg:col-span-2">
                          <Input
                            label="Asunto *"
                            id="tpl-subject"
                            value={form.subject}
                            onChange={(e) => set("subject")(e.target.value)}
                            placeholder="Ej: Tu factura {invoice} está lista"
                          />
                        </div>

                        <div>
                          <Input
                            label="Email remitente *"
                            id="tpl-sender-email"
                            type="email"
                            value={form.senderEmail}
                            onChange={(e) => set("senderEmail")(e.target.value)}
                            placeholder="info@empresa.com"
                          />
                        </div>

                        <div>
                          <Input
                            label="Nombre remitente"
                            id="tpl-sender-name"
                            value={form.senderName}
                            onChange={(e) => set("senderName")(e.target.value)}
                            placeholder="Empresa S.A."
                          />
                        </div>

                        <div>
                          <Input
                            label="Responder a"
                            id="tpl-reply-to"
                            type="email"
                            value={form.replyTo}
                            onChange={(e) => set("replyTo")(e.target.value)}
                            placeholder="soporte@empresa.com"
                          />
                        </div>
                      </>
                    )}
                  </div>
                </Card>
              )}

              {step === 2 && (
                <Card className="p-4! lg:p-5!">
                  <CardTitle>
                    {isEmail ? "Diseño del correo" : "Contenido del mensaje"}
                  </CardTitle>
                  {isUnavailable ? (
                    <div className="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-gray-300 py-16 text-center dark:border-gray-700">
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-300">
                        Esta funcionalidad está en desarrollo
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-500">
                        El diseño de plantillas para este canal aún no está disponible.
                      </p>
                    </div>
                  ) : isEmail ? (
                    <TemplateEditor
                      value={form.body}
                      onChange={set("body")}
                      channel="EMAIL"
                    />
                  ) : (
                    <PlainTextTemplateDesigner
                      value={form.body}
                      onChange={set("body")}
                      maxChars={charLimit}
                    />
                  )}
                </Card>
              )}

              {step === 3 && (
                <Card>
                  <CardTitle>Vista previa</CardTitle>
                  <TemplatePreviewStep
                    channel={form.channel}
                    name={form.name}
                    subject={form.subject}
                    body={form.body}
                  />
                </Card>
              )}
            </>
          )}
        </WizardForm>
      </ModuleBase>
    </>
  );
};
