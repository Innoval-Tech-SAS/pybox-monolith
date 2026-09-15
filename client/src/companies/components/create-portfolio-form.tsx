import { Bell, FolderPlus, UploadCloud } from "lucide-react";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { Button } from "@/ui/components/button/button";
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
          <Button type="button" className="w-full" onClick={handleSuccessModalClose}>
            Entendido
          </Button>
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
          <Label htmlFor="create-portfolio-name">Nombre del portafolio <span className="text-error-500" aria-hidden="true">*</span></Label>
          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <FolderPlus size={16} />
            </span>
            <Input
              id="create-portfolio-name"
              name="portfolioName"
              placeholder="Nombre descriptivo"
              value={portfolioName}
              onChange={(e) => setPortfolioName(e.target.value)}
              className="pl-11"
              required
              aria-required="true"
            />
          </div>
        </div>

        <div>
          <Label>
            <span className="mb-1.5 block">País de origen</span>
            <CountrySelect mode="NAME" value={selectedCountry} onChange={setSelectedCountry} />
          </Label>
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
        <Button type="button" variant="outline" onClick={handleReset}>
          Limpiar
        </Button>
        <Button type="submit" startIcon={<UploadCloud size={16} />}>
          Crear portafolio
        </Button>
      </div>
    </form>
  );
};
