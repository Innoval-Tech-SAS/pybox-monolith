import { Card, CardTitle } from "@/ui/components/card";
import { WhatsAppMessagePreview } from "@/templates/components/whatsapp-message-preview";
import { extractNamedVariables, toVariableToken } from "@/templates/utils/whatsapp-template-components";
import {
  WHATSAPP_CATEGORY_LABELS,
  WHATSAPP_LANGUAGE_OPTIONS,
} from "@/templates/constants/whatsapp-template-options";
import type { StepWhatsAppPreviewProps } from "@/templates/types/step-whatsapp-preview-props";

export const StepWhatsAppPreview: React.FC<StepWhatsAppPreviewProps> = ({
  name,
  whatsappForm,
  variables,
}) => {
  const usedVariables = extractNamedVariables(whatsappForm.bodyText);
  const languageLabel =
    WHATSAPP_LANGUAGE_OPTIONS.find((o) => o.value === whatsappForm.language)?.label ?? whatsappForm.language;

  return (
    <Card className="flex h-full flex-col">
      <CardTitle>Vista previa</CardTitle>
      <div className="flex h-full flex-col gap-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Plantilla</p>
            <p className="truncate text-sm font-semibold text-gray-800 dark:text-white/90">
              {name || "(sin nombre)"}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Idioma</p>
            <p className="text-sm font-semibold text-gray-800 dark:text-white/90">{languageLabel}</p>
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Categoría</p>
            <p className="text-sm font-semibold text-gray-800 dark:text-white/90">
              {WHATSAPP_CATEGORY_LABELS[whatsappForm.category]}
            </p>
          </div>
        </div>

        {usedVariables.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Variables detectadas
            </p>
            <div className="flex flex-wrap gap-1.5">
              {usedVariables.map((key) => (
                <span
                  key={key}
                  className="rounded-md bg-brand-50 px-2 py-0.5 font-mono text-xs text-brand-600 dark:bg-brand-500/10 dark:text-brand-400"
                >
                  {toVariableToken(key)}
                </span>
              ))}
            </div>
          </div>
        )}

        <WhatsAppMessagePreview
          header={whatsappForm.headerText}
          body={whatsappForm.bodyText}
          footer={whatsappForm.footerText}
          variables={variables}
        />

        <div className="rounded-lg border border-blue-light-200 bg-blue-light-50 px-3 py-2 text-xs text-blue-light-700 dark:border-blue-light-500/20 dark:bg-blue-light-500/15 dark:text-blue-light-500">
          Al crearla se envía a Meta para su revisión. Mientras no esté aprobada, Meta rechazará los envíos
          que la usen; consulta el resultado con «Refrescar estado» en el listado.
        </div>
      </div>
    </Card>
  );
};
