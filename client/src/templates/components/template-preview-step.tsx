import { applyTemplatePreview, extractVariables } from "@/templates/utils/template-variables";
import type { TemplateVariableOption } from "@/templates/types/template-variable-option";
import type { TemplateChannel } from "@/types/templates/template-types";

interface TemplatePreviewStepProps {
  channel: TemplateChannel;
  name: string;
  subject?: string;
  body: string;
  variables: TemplateVariableOption[];
}

export const TemplatePreviewStep: React.FC<TemplatePreviewStepProps> = ({ channel, name, subject, body, variables }) => {
  const detectedVariables = extractVariables((body || "") + " " + (subject || ""));
  const isEmail = channel === "EMAIL";
  const renderedBody = isEmail ? body : applyTemplatePreview(body || "", variables);

  return (
    <div className="flex h-full flex-col gap-4">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Plantilla</p>
        <p className="text-sm font-semibold text-gray-800 dark:text-white/90">{name || "(sin nombre)"}</p>
      </div>

      {detectedVariables.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
            Variables detectadas
          </p>
          <div className="flex flex-wrap gap-1.5">
            {detectedVariables.map((v) => (
              <span
                key={v}
                className="rounded bg-blue-100 px-1.5 py-0.5 font-mono text-xs text-blue-700 dark:bg-blue-900/40 dark:text-blue-300"
              >
                {`{${v}}`}
              </span>
            ))}
          </div>
        </div>
      )}

      {isEmail ? (
        <div className="rounded-xl border border-gray-200 dark:border-gray-700">
          {subject && (
            <div className="border-b border-gray-200 px-4 py-2.5 dark:border-gray-700">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Asunto: </span>
              <span className="text-sm text-gray-800 dark:text-white/90">{subject}</span>
            </div>
          )}
          <iframe
            srcDoc={body}
            title="Vista previa"
            className="h-96 w-full rounded-b-xl"
            sandbox="allow-same-origin"
          />
        </div>
      ) : (
        <div className="flex min-h-56 flex-1 items-start rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900">
          {renderedBody ? (
            <div className="max-w-[85%] rounded-2xl rounded-bl-none bg-brand-500 p-4 text-white shadow-md">
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{renderedBody}</p>
            </div>
          ) : (
            <p className="m-auto text-sm text-gray-400">(sin contenido)</p>
          )}
        </div>
      )}
    </div>
  );
};
