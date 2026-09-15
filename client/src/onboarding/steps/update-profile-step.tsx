import React, { useState } from "react";
import { Input } from "@/ui/components/inputs/input";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { useUpdateProfile } from "@/hooks/use-update-profile";
import { useCountries } from "@/hooks/use-countries";
import type { StepDoneProps } from "@/types/props/onboarding-props";

export const UpdateProfileStep: React.FC<StepDoneProps> = ({ onDone }) => {
  const { countries, loading: loadingNat } = useCountries();
  const { updateProfile, loading, error, clearError } = useUpdateProfile();

  const [nationality, setNationality] = useState("");
  const [documentType, setDocumentType] = useState("");
  const [documentNumber, setDocumentNumber] = useState("");

  const selectedNat = countries.find((n) => n.code === nationality);
  const docTypes = selectedNat?.documentTypes ?? [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    await updateProfile({ nationality, documentType, documentNumber });
    onDone();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white/90">Datos del documento</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Completa tu información de identificación para continuar.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          {/* CountrySelect no expone `id`, por lo que no puede enlazarse vía htmlFor
              sin modificar ui/components/inputs/country-select.tsx (fuera de alcance). */}
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Nacionalidad <span className="text-error-500">*</span>
          </label>
          <CountrySelect
            mode="NAME"
            required
            countries={countries}
            placeholder={loadingNat ? "Cargando países..." : "Selecciona tu país"}
            value={nationality}
            onChange={(v) => { setNationality(v); setDocumentType(""); }}
            disabled={loadingNat}
          />
        </div>

        <div>
          <label htmlFor="onboarding-document-type" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Tipo de documento <span className="text-error-500">*</span>
          </label>
          <select
            id="onboarding-document-type"
            required
            aria-required="true"
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
            disabled={!nationality}
            className="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 disabled:opacity-40"
          >
            <option value="">Selecciona el tipo</option>
            {docTypes.map((dt) => (
              <option key={dt} value={dt}>{dt}</option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="onboarding-document-number" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Número de documento <span className="text-error-500">*</span>
          </label>
          <Input
            id="onboarding-document-number"
            placeholder="Ej. 1234567890"
            value={documentNumber}
            onChange={(e) => setDocumentNumber(e.target.value)}
            error={!!error}
            required
          />
          {error && <p className="mt-1 text-xs text-error-500">{error}</p>}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !nationality || !documentType || !documentNumber}
        className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
      >
        {loading ? "Guardando..." : "Continuar"}
      </button>
    </form>
  );
};
