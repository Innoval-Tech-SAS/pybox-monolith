import { DropZone } from "@/ui/components/inputs/drop-zone";
import type { StepDocumentsProps } from "@/companies/types/step-documents-props";

export const StepDocuments: React.FC<StepDocumentsProps> = ({
  form,
  fiscalLabel,
  mercantileLabel,
  canGoNext,
  onNext,
  onBack,
}) => {
  const {
    fiscalFile, fiscalError, handleFiscalFileChange,
    mercantileFile, mercantileError, handleMercantileFileChange,
  } = form;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">
          Documentos de la empresa
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Sube los documentos requeridos para la verificación.
        </p>
      </div>
      <div className="space-y-4">
        <DropZone
          label={fiscalLabel}
          file={fiscalFile}
          onChange={handleFiscalFileChange}
          error={fiscalError ?? undefined}
        />
        <DropZone
          label={mercantileLabel}
          file={mercantileFile}
          onChange={handleMercantileFileChange}
          error={mercantileError ?? undefined}
        />
      </div>
      <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3"
        >
          Atrás
        </button>
        <button
          type="button"
          onClick={onNext}
          disabled={!canGoNext}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:opacity-50"
        >
          Siguiente
        </button>
      </div>
    </div>
  );
};
