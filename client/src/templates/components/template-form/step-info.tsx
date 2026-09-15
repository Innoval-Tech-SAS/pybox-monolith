import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
import { STATUS_OPTIONS } from "@/templates/constants/template-wizard-options";
import type { TemplateStatus } from "@/types/templates/template-types";
import type { StepInfoProps } from "@/templates/types/step-info-props";

export const StepInfo: React.FC<StepInfoProps> = ({ form, isEmail, set }) => (
  <Card className="flex h-full flex-col">
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
);
