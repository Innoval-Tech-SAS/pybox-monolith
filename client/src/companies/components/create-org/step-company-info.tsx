import { Building2, Hash, Info } from "lucide-react";
import { Label } from "@/ui/components/inputs/label";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { Button } from "@/ui/components/button/button";
import { INPUT_BASE } from "@/companies/constants/create-org-styles";
import type { StepCompanyInfoProps } from "@/companies/types/step-company-info-props";

export const StepCompanyInfo: React.FC<StepCompanyInfoProps> = ({
  form,
  countriesData,
  fiscalLabel,
  canGoNext,
  onNext,
  onCancel,
}) => {
  const {
    isSubmitting,
    name, setName,
    country, setCountry,
    fiscalDocNumber, setFiscalDocNumber,
    description, setDescription,
    setRepDocType,
  } = form;
  const { countries, loading: loadingCountries } = countriesData;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">
          Datos de la empresa
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Información básica de la empresa a registrar.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <Label htmlFor="create-org-name">
            Nombre <span className="text-error-500" aria-hidden="true">*</span>
          </Label>
          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <Building2 size={16} />
            </span>
            <input
              id="create-org-name"
              type="text"
              placeholder="Nombre legal o comercial"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={isSubmitting}
              required
              aria-required="true"
              className={`${INPUT_BASE} pl-11`}
            />
          </div>
        </div>
        <div>
          <Label>
            <span className="mb-1.5 block">
              País <span className="text-error-500" aria-hidden="true">*</span>
            </span>
            <CountrySelect
              mode="NAME"
              countries={countries}
              placeholder={loadingCountries ? "Cargando..." : "Selecciona el país"}
              value={country}
              onChange={(v) => {
                setCountry(v);
                setRepDocType("");
              }}
              disabled={isSubmitting || loadingCountries}
              required
            />
          </Label>
        </div>
        <div>
          <Label htmlFor="create-org-fiscal-doc-number">{fiscalLabel}</Label>
          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <Hash size={16} />
            </span>
            <input
              id="create-org-fiscal-doc-number"
              type="text"
              placeholder="Ej: 901.234.567-8"
              value={fiscalDocNumber}
              onChange={(e) => setFiscalDocNumber(e.target.value)}
              disabled={isSubmitting}
              className={`${INPUT_BASE} pl-11`}
            />
          </div>
        </div>
        <div>
          <Label htmlFor="create-org-description">Descripción</Label>
          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <Info size={16} />
            </span>
            <input
              id="create-org-description"
              type="text"
              placeholder="Breve descripción"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isSubmitting}
              className={`${INPUT_BASE} pl-11`}
            />
          </div>
        </div>
      </div>
      <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="button" onClick={onNext} disabled={!canGoNext}>
          Siguiente
        </Button>
      </div>
    </div>
  );
};
