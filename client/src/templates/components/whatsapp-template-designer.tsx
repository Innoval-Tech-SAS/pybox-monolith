import { useCallback, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Plus, X } from "lucide-react";
import { Input } from "@/ui/components/inputs/input";
import { usePortalDropdown } from "@/hooks/use-portal-dropdown";
import { WhatsAppMessagePreview } from "@/templates/components/whatsapp-message-preview";
import {
  WHATSAPP_BODY_MAX_CHARS,
  WHATSAPP_FOOTER_MAX_CHARS,
  WHATSAPP_HEADER_MAX_CHARS,
} from "@/templates/constants/whatsapp-template-options";
import { extractNamedVariables, toVariableToken } from "@/templates/utils/whatsapp-template-components";
import type { WhatsAppTemplateDesignerProps } from "@/templates/types/whatsapp-template-designer-props";

export const WhatsAppTemplateDesigner: React.FC<WhatsAppTemplateDesignerProps> = ({
  form,
  issues,
  variables,
  loadingVariables,
  onHeaderChange,
  onBodyChange,
  onFooterChange,
}) => {
  const [cursorPosition, setCursorPosition] = useState(0);
  const [showVariables, setShowVariables] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { triggerRef, dropdownRef, dropdownStyle } = usePortalDropdown<
    HTMLButtonElement,
    HTMLDivElement
  >({ open: showVariables, onClose: () => setShowVariables(false) });

  const body = form.bodyText;
  const charsRemaining = WHATSAPP_BODY_MAX_CHARS - body.length;
  const usedVariables = extractNamedVariables(body);

  const setCursorSafe = useCallback((pos: number) => {
    const el = textareaRef.current;
    setCursorPosition(Math.max(0, Math.min(pos, el?.value.length ?? pos)));
  }, []);

  const insertVariable = useCallback(
    (key: string) => {
      const token = toVariableToken(key);
      onBodyChange(`${body.slice(0, cursorPosition)}${token}${body.slice(cursorPosition)}`);
      const nextPos = cursorPosition + token.length;
      setShowVariables(false);
      requestAnimationFrame(() => {
        textareaRef.current?.focus();
        textareaRef.current?.setSelectionRange(nextPos, nextPos);
      });
      setCursorPosition(nextPos);
    },
    [body, cursorPosition, onBodyChange],
  );

  const removeVariable = useCallback(
    (key: string) => {
      onBodyChange(body.split(toVariableToken(key)).join(""));
    },
    [body, onBodyChange],
  );

  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
      <div className="flex flex-col gap-4">
        <Input
          label="Encabezado (opcional)"
          id="wa-header"
          value={form.headerText}
          onChange={(e) => onHeaderChange(e.target.value)}
          placeholder="Ej: Recordatorio de pago"
          error={issues.headerTooLong || issues.headerHasVariables}
          hint={
            issues.headerHasVariables
              ? "El encabezado no admite variables."
              : `${form.headerText.length}/${WHATSAPP_HEADER_MAX_CHARS} caracteres`
          }
        />

        <div>
          <label
            htmlFor="wa-body"
            className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400"
          >
            Cuerpo del mensaje *
          </label>
          <textarea
            id="wa-body"
            ref={textareaRef}
            className="min-h-48 w-full resize-none rounded-lg border border-gray-300 bg-transparent p-4 font-mono text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
            placeholder="Escribe el mensaje aquí... Usa {{variable}} para insertar datos del deudor o crédito."
            value={body}
            onChange={(e) => {
              onBodyChange(e.target.value);
              setCursorSafe(e.target.selectionStart ?? 0);
            }}
            onClick={(e) => setCursorSafe(e.currentTarget.selectionStart ?? 0)}
            onKeyUp={(e) => setCursorSafe(e.currentTarget.selectionStart ?? 0)}
          />
          <div className="mt-1.5 flex justify-end text-xs">
            <span className={charsRemaining < 0 ? "text-error-500" : "text-gray-500 dark:text-gray-400"}>
              {body.length}/{WHATSAPP_BODY_MAX_CHARS}
            </span>
          </div>
        </div>

        <div className="relative">
          <button
            ref={triggerRef}
            type="button"
            onClick={() => setShowVariables((v) => !v)}
            disabled={loadingVariables || variables.length === 0}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
          >
            <Plus size={16} />
            {loadingVariables ? "Cargando variables..." : "Añadir variable"}
          </button>

          {showVariables && !loadingVariables && dropdownStyle &&
            createPortal(
              <div
                ref={dropdownRef}
                style={dropdownStyle}
                className="max-h-56 overflow-y-auto rounded-lg border border-gray-200 bg-white p-2 shadow-lg dark:border-gray-700 dark:bg-gray-900"
              >
                {variables.map((variable) => (
                  <button
                    key={variable.key}
                    type="button"
                    onClick={() => insertVariable(variable.key)}
                    className="flex w-full items-center justify-between gap-2 rounded-md p-2 text-left transition hover:bg-gray-50 dark:hover:bg-white/5"
                  >
                    <span>
                      <span className="block font-mono text-xs text-brand-600 dark:text-brand-400">
                        {toVariableToken(variable.key)}
                      </span>
                      <span className="block text-xs text-gray-500 dark:text-gray-400">{variable.label}</span>
                    </span>
                    <Plus size={14} className="text-gray-400" />
                  </button>
                ))}
              </div>,
              document.body,
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
                  <span className="font-mono text-brand-700 dark:text-brand-400">{toVariableToken(key)}</span>
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

        {issues.unknownVariables.length > 0 && (
          <div className="rounded-lg border border-error-200 bg-error-50 px-3 py-2 text-xs text-error-700 dark:border-error-500/20 dark:bg-error-500/15 dark:text-error-400">
            Variables sin columna asociada:{" "}
            <span className="font-mono">
              {issues.unknownVariables.map((key) => toVariableToken(key)).join(", ")}
            </span>
            . Usa «Añadir variable» para elegir una disponible.
          </div>
        )}

        {issues.variableAtEdge && (
          <div className="rounded-lg border border-warning-200 bg-warning-50 px-3 py-2 text-xs text-warning-700 dark:border-warning-500/20 dark:bg-warning-500/15 dark:text-orange-400">
            Meta suele rechazar plantillas cuyo cuerpo empieza o termina con una variable. Agrega texto
            antes y después para evitarlo.
          </div>
        )}

        <Input
          label="Pie de mensaje (opcional)"
          id="wa-footer"
          value={form.footerText}
          onChange={(e) => onFooterChange(e.target.value)}
          placeholder="Ej: Responde STOP para dejar de recibir mensajes"
          error={issues.footerTooLong || issues.footerHasVariables}
          hint={
            issues.footerHasVariables
              ? "El pie de mensaje no admite variables."
              : `${form.footerText.length}/${WHATSAPP_FOOTER_MAX_CHARS} caracteres`
          }
        />
      </div>

      <WhatsAppMessagePreview
        header={form.headerText}
        body={form.bodyText}
        footer={form.footerText}
        variables={variables}
      />
    </div>
  );
};
