import { applyNamedExamples } from "@/templates/utils/whatsapp-template-components";
import type { WhatsAppMessagePreviewProps } from "@/templates/types/whatsapp-message-preview-props";

export const WhatsAppMessagePreview: React.FC<WhatsAppMessagePreviewProps> = ({
  header,
  body,
  footer,
  variables,
}) => (
  <div className="flex h-full min-h-56 min-w-0 flex-col rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900">
    <p className="mb-3 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
      Vista previa
    </p>
    <div className="flex flex-1 items-start">
      {body.trim() ? (
        <div className="max-w-[85%] min-w-0 rounded-2xl rounded-bl-none bg-brand-500 p-4 text-white shadow-md">
          {header.trim() && (
            <p className="mb-1.5 break-words text-sm font-semibold">{header.trim()}</p>
          )}
          <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">
            {applyNamedExamples(body.trim(), variables)}
          </p>
          {footer.trim() && (
            <p className="mt-2 break-words text-xs text-white/70">{footer.trim()}</p>
          )}
        </div>
      ) : (
        <p className="m-auto text-sm text-gray-400">Tu mensaje aparecerá aquí</p>
      )}
    </div>
  </div>
);
