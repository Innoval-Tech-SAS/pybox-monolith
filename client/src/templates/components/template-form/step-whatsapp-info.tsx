import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
import {
  WHATSAPP_CATEGORY_OPTIONS,
  WHATSAPP_LANGUAGE_OPTIONS,
} from "@/templates/constants/whatsapp-template-options";
import type { WhatsAppTemplateCategory } from "@/types/templates/whatsapp-template-types";
import type { StepWhatsAppInfoProps } from "@/templates/types/step-whatsapp-info-props";

export const StepWhatsAppInfo: React.FC<StepWhatsAppInfoProps> = ({
  name,
  whatsappForm,
  onNameChange,
  onWhatsAppChange,
}) => (
  <Card className="flex h-full flex-col">
    <CardTitle>Información de la plantilla</CardTitle>
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
      <div className="sm:col-span-2">
        <Input
          label="Nombre *"
          id="tpl-name"
          value={name}
          onChange={(e) => onNameChange(e.target.value)}
          placeholder="Ej: Recordatorio de pago"
          hint="Meta solo admite minúsculas, números y guion bajo; los demás caracteres se reemplazan por «_»."
        />
      </div>

      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
          Idioma *
        </label>
        <Select
          options={WHATSAPP_LANGUAGE_OPTIONS}
          value={whatsappForm.language}
          onChange={onWhatsAppChange("language")}
        />
      </div>

      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
          Categoría *
        </label>
        <Select
          options={WHATSAPP_CATEGORY_OPTIONS}
          value={whatsappForm.category}
          onChange={(v) => onWhatsAppChange("category")(v as WhatsAppTemplateCategory)}
        />
      </div>
    </div>
  </Card>
);
