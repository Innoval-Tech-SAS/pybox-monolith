import { DropZone } from "@/ui/components/inputs/drop-zone";
import { Button } from "@/ui/components/button/button";
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
        <Button type="button" variant="outline" onClick={onBack}>
          Atrás
        </Button>
        <Button type="button" onClick={onNext} disabled={!canGoNext}>
          Siguiente
        </Button>
      </div>
    </div>
  );
};
