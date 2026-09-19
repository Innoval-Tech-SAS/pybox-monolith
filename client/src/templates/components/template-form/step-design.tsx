import { Card, CardTitle } from "@/ui/components/card";
import { TemplateEditor } from "@/templates/components/template-editor";
import { PlainTextTemplateDesigner } from "@/templates/components/plain-text-template-designer";
import type { StepDesignProps } from "@/templates/types/step-design-props";

export const StepDesign: React.FC<StepDesignProps> = ({
  isEmail,
  isUnavailable,
  body,
  design,
  onBodyChange,
  onDesignChange,
  charLimit,
  variables,
  loadingVariables,
}) => (
  <Card className="flex h-full flex-col p-4! lg:p-5!">
    <CardTitle>{isEmail ? "Diseño del correo" : "Contenido del mensaje"}</CardTitle>
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
        value={body}
        design={design}
        onChange={onDesignChange}
        variables={variables}
        loadingVariables={loadingVariables}
      />
    ) : (
      <div className="min-h-0 flex-1">
        <PlainTextTemplateDesigner
          value={body}
          onChange={onBodyChange}
          maxChars={charLimit}
          variables={variables}
          loadingVariables={loadingVariables}
        />
      </div>
    )}
  </Card>
);
