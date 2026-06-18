import { useCallback, useRef, useState } from "react";
import { Plus, X } from "lucide-react";
import { applyTemplatePreview, extractVariables } from "@/templates/utils/template-variables";
import type { TemplateVariableOption } from "@/templates/types/template-variable-option";

interface PlainTextTemplateDesignerProps {
  value: string;
  onChange: (value: string) => void;
  maxChars?: number;
  variables: TemplateVariableOption[];
  loadingVariables?: boolean;
}

export const PlainTextTemplateDesigner: React.FC<PlainTextTemplateDesignerProps> = ({
  value,
  onChange,
  maxChars,
  variables,
  loadingVariables = false,
}) => {
  const [cursorPosition, setCursorPosition] = useState(0);
  const [showVariables, setShowVariables] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const charsRemaining = maxChars !== undefined ? maxChars - value.length : null;
  const usedVariables = extractVariables(value);
  const preview = applyTemplatePreview(value, variables);

  const setCursorSafe = useCallback((pos: number) => {
    const el = textareaRef.current;
    setCursorPosition(Math.max(0, Math.min(pos, el?.value.length ?? pos)));
  }, []);

  const insertVariable = useCallback(
    (key: string) => {
      const token = `{${key}}`;
      const before = value.slice(0, cursorPosition);
      const after = value.slice(cursorPosition);
      onChange(`${before}${token}${after}`);
      const nextPos = cursorPosition + token.length;
      setShowVariables(false);
      requestAnimationFrame(() => {
        textareaRef.current?.focus();
        textareaRef.current?.setSelectionRange(nextPos, nextPos);
      });
      setCursorPosition(nextPos);
    },
    [cursorPosition, onChange, value],
  );

  const removeVariable = useCallback(
    (key: string) => {
      onChange(value.replace(new RegExp(`\\{${key}\\}`, "g"), ""));
    },
    [onChange, value],
  );

  return (
    <div className="grid h-full grid-cols-1 gap-5 lg:grid-cols-2">
      <div className="flex h-full flex-col gap-3">
        <textarea
          ref={textareaRef}
          className="min-h-48 w-full flex-1 resize-none rounded-lg border border-gray-300 bg-transparent p-4 font-mono text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
          placeholder="Escribe el mensaje aquí... Usa {variable} para insertar variables dinámicas."
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
            setCursorSafe(e.target.selectionStart ?? 0);
          }}
          onClick={(e) => setCursorSafe(e.currentTarget.selectionStart ?? 0)}
          onKeyUp={(e) => setCursorSafe(e.currentTarget.selectionStart ?? 0)}
        />

        {charsRemaining !== null && (
          <div className="flex justify-end text-xs">
            <span className={charsRemaining < 0 ? "text-error-500" : "text-gray-500"}>
              {charsRemaining}/{maxChars}
            </span>
          </div>
        )}

        <div className="relative">
          <button
            type="button"
            onClick={() => setShowVariables((v) => !v)}
            disabled={loadingVariables || variables.length === 0}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
          >
            <Plus size={16} />
            {loadingVariables ? "Cargando variables..." : "Añadir variable"}
          </button>

          {showVariables && !loadingVariables && (
            <div className="absolute z-10 mt-2 max-h-56 w-full overflow-y-auto rounded-lg border border-gray-200 bg-white p-2 shadow-lg dark:border-gray-700 dark:bg-gray-900">
              {variables.map((variable) => (
                <button
                  key={variable.key}
                  type="button"
                  onClick={() => insertVariable(variable.key)}
                  className="flex w-full items-center justify-between gap-2 rounded-md p-2 text-left transition hover:bg-gray-50 dark:hover:bg-white/5"
                >
                  <span>
                    <span className="block font-mono text-xs text-brand-600 dark:text-brand-400">{`{${variable.key}}`}</span>
                    <span className="block text-xs text-gray-500 dark:text-gray-400">{variable.label}</span>
                  </span>
                  <Plus size={14} className="text-gray-400" />
                </button>
              ))}
            </div>
          )}
        </div>

        {usedVariables.length > 0 && (
          <div className="rounded-lg border border-brand-200 bg-brand-50 p-3 dark:border-brand-500/20 dark:bg-brand-500/10">
            <p className="mb-2 text-xs font-medium text-gray-600 dark:text-gray-300">Variables en uso</p>
            <div className="flex flex-wrap gap-1.5">
              {usedVariables.map((key) => (
                <span
                  key={key}
                  className="flex items-center gap-1.5 rounded-full border border-brand-300 bg-white px-2.5 py-1 text-xs dark:border-brand-500/30 dark:bg-gray-900"
                >
                  <span className="font-mono text-brand-700 dark:text-brand-400">{`{${key}}`}</span>
                  <button
                    type="button"
                    onClick={() => removeVariable(key)}
                    aria-label={`Eliminar variable ${key}`}
                  >
                    <X size={12} className="text-gray-400 hover:text-error-500" />
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="flex h-full min-h-56 flex-col rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900">
        <p className="mb-3 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
          Vista previa
        </p>
        <div className="flex flex-1 items-start">
          {value ? (
            <div className="max-w-[85%] rounded-2xl rounded-bl-none bg-brand-500 p-4 text-white shadow-md">
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{preview}</p>
            </div>
          ) : (
            <p className="m-auto text-sm text-gray-400">Tu mensaje aparecerá aquí</p>
          )}
        </div>
      </div>
    </div>
  );
};
