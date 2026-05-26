import { Bell, FolderPlus, UploadCloud } from "lucide-react";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { CSV_TYPES } from "../constants/portfolio-file-types";
import { useCreatePortfolio } from "../hooks/use-create-portfolio";

export const CreatePortfolioForm: React.FC = () => {
  const {
    showSuccessModal,
    handleSuccessModalClose,
    portfolioName, setPortfolioName,
    selectedFile, setSelectedFile,
    selectedCountry, setSelectedCountry,
    formRef,
    handleReset,
    handleSubmit,
  } = useCreatePortfolio();

  if (showSuccessModal) {
    return (
      <div className="flex flex-1 items-center justify-center py-20">
        <div className="flex flex-col items-center gap-6 text-center max-w-md">
          <div className="flex size-20 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10">
            <Bell className="size-10 text-brand-500" />
          </div>
          <div>
            <h5 className="mb-2 text-xl font-semibold text-gray-800 dark:text-white/90">
              Portafolio en procesamiento
            </h5>
            <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
              Tu archivo está siendo procesado. Recibirás una notificación cuando el portafolio esté listo.
            </p>
          </div>
          <button
            type="button"
            onClick={handleSuccessModalClose}
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
        <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">Cargar portafolio</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Sube un archivo CSV con los datos de los clientes del portafolio.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <Label>Nombre del portafolio <span className="text-error-500">*</span></Label>
          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <FolderPlus size={16} />
            </span>
            <Input
              name="portfolioName"
              placeholder="Nombre descriptivo"
              value={portfolioName}
              onChange={(e) => setPortfolioName(e.target.value)}
              className="pl-11"
              required
            />
          </div>
        </div>

        <div>
          <Label>País de origen</Label>
          <CountrySelect mode="NAME" value={selectedCountry} onChange={setSelectedCountry} />
        </div>
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
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3 dark:hover:text-gray-300"
        >
          Limpiar
        </button>
        <button
          type="submit"
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600"
        >
          <UploadCloud size={16} />
          Crear portafolio
        </button>
      </div>
    </form>
  );
};
