import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { Select } from "@/ui/components/inputs/select";
import { useApiClient } from "@/hooks/use-api-client";
import { TemplateEditor } from "../components/template-editor";
import type {
  Template,
  TemplateChannel,
  TemplateStatus,
} from "@/types/templates/template-types";
import type { TemplateEditorFormState } from "@/templates/types/template-editor-form-state";

const STATUS_OPTIONS = [
  { value: "DRAFT", label: "Borrador" },
  { value: "ACTIVE", label: "Activa" },
  { value: "INACTIVE", label: "Inactiva" },
];

const CHANNEL_OPTIONS = [
  { value: "EMAIL", label: "Email" },
  { value: "SMS", label: "SMS" },
];

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const isEmail = form.channel === "EMAIL";
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

  const isEmail = form.channel === "EMAIL";
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
      <PageMeta title={pageTitle} description="Editor de plantillas de correo" />
      <ModuleBase
        pageTitle={pageTitle}
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          { label: "Plantillas", path: backPath },
        ]}
      >
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          {/* Campos de configuración */}
          <Card>
            <CardTitle>Configuración</CardTitle>
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
                  Canal
                </label>
                <Select
                  options={CHANNEL_OPTIONS}
                  value={form.channel}
                  onChange={(v) => set("channel")(v as TemplateChannel)}
                  disabled={isEditing}
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
                      label="Email remitente"
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

          {/* Editor visual */}
          <Card className="p-4! lg:p-5!">
            <CardTitle>
              {isEmail ? "Diseño del correo" : "Contenido del mensaje"}
            </CardTitle>
            <TemplateEditor
              value={form.body}
              onChange={set("body")}
              channel={form.channel}
            />
          </Card>

          {/* Acciones */}
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
              disabled={saving || !form.name.trim() || !form.body.trim()}
              className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
            >
              {saving
                ? isEditing ? "Guardando…" : "Creando…"
                : isEditing ? "Guardar cambios" : "Crear plantilla"}
            </button>
          </div>
        </form>
      </ModuleBase>
    </>
  );
};
