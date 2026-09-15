import { Bell, Download, RefreshCw, UploadCloud } from "lucide-react";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { Spinner } from "@/ui/components/loader/spinner";
import { API_URL } from "@/config/api";
import { CSV_TYPES } from "../constants/portfolio-file-types";
import { useUploadPortfolioCsv } from "../hooks/use-upload-portfolio-csv";
import type { EditPortfolioFormProps } from "@/companies/types/edit-portfolio-form-props";
import { MODE_META } from "../constants/portfolio-upload-mode-meta";

export const EditPortfolioForm: React.FC<EditPortfolioFormProps> = ({ mode }) => {
  const {
    selectedFile, setSelectedFile,
    submitting,
    processing,
    formRef,
    handleReset,
    handleSubmit,
    handleDismiss,
  } = useUploadPortfolioCsv(mode);

  const meta = MODE_META[mode];

  if (processing) {
    return (
      <div className="flex flex-1 items-center justify-center py-20">
        <div className="flex flex-col items-center gap-6 text-center max-w-md">
          <div className="flex size-20 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10">
            <Bell className="size-10 text-brand-500" />
          </div>
          <div>
            <h5 className="mb-2 text-xl font-semibold text-gray-800 dark:text-white/90">
              Procesando archivo
            </h5>
            <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
              El archivo está siendo procesado en segundo plano. Recibirás una notificación cuando termine.
            </p>
          </div>
          <button
            type="button"
            onClick={handleDismiss}
            className="w-full rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white hover:bg-brand-600 transition"
          >
            Entendido
          </button>
        </div>
      </div>
    );
  }

  return (
    <form ref={formRef} onSubmit={handleSubmit} className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">{meta.title}</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{meta.description}</p>
        <a
          href={`${API_URL}/portfolios/upload-csv/template`}
          download
          className="mt-2 inline-flex items-center gap-1.5 text-sm font-medium text-brand-500 hover:text-brand-600"
        >
          <Download size={14} />
          Descargar plantilla CSV
        </a>
      </div>

      <DropZone
        label="Archivo CSV *"
        file={selectedFile}
        onChange={setSelectedFile}
        allowed={CSV_TYPES}
        hint="CSV o XLSX · máx. 10 MB"
        error={undefined}
      />

      <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end pt-2">
        <button
          type="button"
          onClick={handleReset}
          disabled={submitting}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 disabled:opacity-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700"
        >
          <RefreshCw size={15} />
          Limpiar
        </button>
        <button
          type="submit"
          disabled={submitting || !selectedFile}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:opacity-50"
        >
          {submitting ? (
            <Spinner size="xs" tone="white" />
          ) : (
            <UploadCloud size={16} />
          )}
          {meta.buttonLabel}
        </button>
      </div>
    </form>
  );
};
