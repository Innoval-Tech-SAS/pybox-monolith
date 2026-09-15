import { useEffect, useState } from "react";
import { Modal } from "@/ui/components/modal/modal";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { Loader } from "@/ui/components/loader/loader";
import { Button } from "@/ui/components/button/button";
import { extractVariables } from "@/templates/utils/template-variables";
import type { TemplatePreviewResponse } from "@/types/templates/template-types";
import type { TemplatePreviewModalProps } from "@/templates/types/template-preview-modal-props";

export const TemplatePreviewModal: React.FC<TemplatePreviewModalProps> = ({
  isOpen,
  template,
  variableOptions,
  onClose,
  onPreview,
}) => {
  const isEmail = template?.channel === "EMAIL";
  const variables = template
    ? extractVariables((template.body ?? "") + " " + (template.subject ?? ""))
    : [];
  const exampleSub = variables.reduce<Record<string, string>>((acc, key) => {
    const option = variableOptions.find((v) => v.key === key);
    if (option) acc[key] = option.example;
    return acc;
  }, {});
  const [sub, setSub] = useState<Record<string, string>>({});
  const [result, setResult] = useState<TemplatePreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handlePreview = async () => {
    if (!template) return;
    setLoading(true);
    const res = await onPreview(template.id, sub);
    setResult(res);
    setLoading(false);
  };

  const handleClose = () => {
    setResult(null);
    setSub({});
    onClose();
  };

  useEffect(() => {
    if (isOpen && template && isEmail) {
      setLoading(true);
      onPreview(template.id, exampleSub)
        .then(setResult)
        .finally(() => setLoading(false));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, template, isEmail]);

  return (
    <Modal isOpen={isOpen} onClose={handleClose} className="max-w-3xl mx-4 p-6 sm:p-8">
      <h2 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">
        Vista previa — {template?.name}
      </h2>

      {!isEmail && variables.length > 0 && (
        <div className="mb-4">
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
            Variables detectadas
          </p>
          <div className="grid grid-cols-2 gap-3">
            {variables.map((v) => (
              <div key={v}>
                <Label htmlFor={`prev-${v}`}>{`{ ${v} }`}</Label>
                <Input
                  id={`prev-${v}`}
                  value={sub[v] ?? ""}
                  placeholder={`Valor para ${v}`}
                  onChange={(e) => setSub((prev) => ({ ...prev, [v]: e.target.value }))}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {!isEmail && (
        <div className="mb-4 flex justify-end">
          <Button type="button" size="sm" onClick={handlePreview} loading={loading} loadingText="Renderizando…">
            Renderizar
          </Button>
        </div>
      )}

      {isEmail && loading && (
        <div className="py-10"><Loader loaderText="Renderizando…" /></div>
      )}

      {result && (
        isEmail ? (
          <div className="rounded-xl border border-gray-200 dark:border-gray-700">
            {result.subject && (
              <div className="border-b border-gray-200 px-4 py-2.5 dark:border-gray-700">
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Asunto: </span>
                <span className="text-sm text-gray-800 dark:text-white/90">{result.subject}</span>
              </div>
            )}
            <iframe
              srcDoc={result.html}
              title="Preview"
              className="h-96 w-full rounded-b-xl"
              sandbox="allow-same-origin"
            />
          </div>
        ) : (
          <div className="flex min-h-40 items-start rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900">
            <div className="max-w-[85%] rounded-2xl rounded-bl-none bg-brand-500 p-4 text-white shadow-md">
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{result.html}</p>
            </div>
          </div>
        )
      )}
    </Modal>
  );
};
