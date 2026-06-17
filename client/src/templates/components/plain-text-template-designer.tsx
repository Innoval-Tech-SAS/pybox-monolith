import { extractVariables } from "@/templates/utils/template-variables";

interface PlainTextTemplateDesignerProps {
  value: string;
  onChange: (value: string) => void;
  maxChars?: number;
}

export const PlainTextTemplateDesigner: React.FC<PlainTextTemplateDesignerProps> = ({
  value,
  onChange,
  maxChars,
}) => {
  const charsRemaining = maxChars !== undefined ? maxChars - value.length : null;
  const variables = extractVariables(value);

  return (
    <div className="space-y-3">
      <textarea
        className="h-48 w-full resize-none rounded-lg border border-gray-300 bg-transparent p-4 font-mono text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
        placeholder="Escribe el mensaje aquí... Usa {variable} para insertar variables dinámicas."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />

      <div className="flex items-center justify-between text-xs">
        <div className="flex flex-wrap gap-1.5">
          {variables.map((v) => (
            <span
              key={v}
              className="rounded bg-blue-100 px-1.5 py-0.5 font-mono text-blue-700 dark:bg-blue-900/40 dark:text-blue-300"
            >
              {`{${v}}`}
            </span>
          ))}
        </div>

        {charsRemaining !== null && (
          <span className={charsRemaining < 0 ? "text-error-500" : "text-gray-500"}>
            {charsRemaining}/{maxChars}
          </span>
        )}
      </div>
    </div>
  );
};
