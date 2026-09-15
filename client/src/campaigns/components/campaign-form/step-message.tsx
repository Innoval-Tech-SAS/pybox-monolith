import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
import { Switch } from "@/ui/components/switch";
import { TemplatePreviewStep } from "@/templates/components/template-preview-step";
import type { StepMessageProps } from "@/campaigns/types/step-message-props";

export const StepMessage: React.FC<StepMessageProps> = ({
  form,
  segments,
  compatibleTemplates,
  selectedTemplate,
  showsSubject,
  variables,
  set,
}) => (
  <div className="flex h-full flex-col gap-5">
    <Card>
      <CardTitle>Destinatarios y plantilla</CardTitle>
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
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
            Plantilla *
          </label>
          <Select
            options={compatibleTemplates.map((t) => ({ value: t.id, label: t.name }))}
            value={form.templateId}
            onChange={(v) => set("templateId")(v)}
            placeholder="Selecciona una plantilla"
            disabled={compatibleTemplates.length === 0}
          />
          {compatibleTemplates.length === 0 && (
            <p className="mt-1.5 text-xs text-gray-400 dark:text-gray-500">
              No hay plantillas para este canal.
            </p>
          )}
        </div>

        {showsSubject && !selectedTemplate && (
          <div className="sm:col-span-2">
            <Input
              label="Asunto"
              id="cmp-subject"
              value={form.subject}
              onChange={(e) => set("subject")(e.target.value)}
              placeholder="Ej: Tu factura {invoice} está lista"
            />
          </div>
        )}

        <div className="sm:col-span-2">
          <Switch
            checked={form.fallback}
            onChange={set("fallback")}
            label="Usar canal de respaldo si falla el envío"
          />
        </div>
      </div>
    </Card>

    <Card className="flex min-h-0 flex-1 flex-col">
      {selectedTemplate ? (
        <>
          <TemplatePreviewStep
            channel={selectedTemplate.channel}
            name={selectedTemplate.name}
            subject={selectedTemplate.subject ?? undefined}
            body={selectedTemplate.body}
            variables={variables}
          />
        </>
      ) : (
        <>
          <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-gray-200 p-8 dark:border-gray-700">
            <p className="text-sm text-gray-400 dark:text-gray-500">
              Selecciona una plantilla para ver la vista previa del mensaje.
            </p>
          </div>
        </>
      )}
    </Card>
  </div>
);
