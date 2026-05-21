import React, { useState } from "react";
import { Input } from "@/ui/components/inputs/input";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { useOrganizationOnboarding } from "@/hooks/use-organization-onboarding";
import { useNationalities } from "@/hooks/use-nationalities";

const ORG_FISCAL_NAMES: Record<string, string> = {
  CO: "NIT – Número de Identificación Tributaria",
  MX: "RFC – Registro Federal de Contribuyentes",
  AR: "CUIT – Código Único de Identificación Tributaria",
  PE: "RUC – Registro Único de Contribuyentes",
  VE: "RIF – Registro de Información Fiscal",
};

const ORG_MERCANTILE_NAMES: Record<string, string> = {
  CO: "Cámara de Comercio",
  MX: "Registro Público de Comercio",
  AR: "Inscripción en el IGJ",
  PE: "Partida Registral SUNARP",
  VE: "Registro Mercantil",
};

interface Props {
  onDone: () => void;
}

export const OrganizationStep: React.FC<Props> = ({ onDone }) => {
  const { nationalities, loading: loadingNat } = useNationalities();
  const { saveOrganization, loading, error, clearError } = useOrganizationOnboarding();

  const [name, setName] = useState("");
  const [country, setCountry] = useState("");
  const [fiscalNumber, setFiscalNumber] = useState("");
  const [mercantileNumber, setMercantileNumber] = useState("");
  const [fiscalFile, setFiscalFile] = useState<File | null>(null);
  const [mercantileFile, setMercantileFile] = useState<File | null>(null);
  const [fileErrors, setFileErrors] = useState({ fiscal: "", mercantile: "" });

  const fiscalLabel = country ? ORG_FISCAL_NAMES[country] ?? "Registro fiscal" : "Registro fiscal";
  const mercantileLabel = country ? ORG_MERCANTILE_NAMES[country] ?? "Registro mercantil" : "Registro mercantil";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    const errors = {
      fiscal: fiscalFile ? "" : "Este documento es requerido",
      mercantile: mercantileFile ? "" : "Este documento es requerido",
    };
    setFileErrors(errors);
    if (errors.fiscal || errors.mercantile) return;

    await saveOrganization({
      name,
      country,
      fiscalDocumentNumber: fiscalNumber,
      mercantileDocumentNumber: mercantileNumber,
      fiscalDocumentFile: fiscalFile!,
      mercantileDocumentFile: mercantileFile!,
    });
    onDone();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white/90">Datos de la organización</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Completa la información de tu empresa para activar la cuenta.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Nombre de la organización
          </label>
          <Input
            placeholder="Ej. Mi Empresa S.A.S."
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            País de registro
          </label>
          <select
            required
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            disabled={loadingNat}
            className="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
          >
            <option value="">Selecciona el país</option>
            {nationalities.map((n) => (
              <option key={n.code} value={n.code}>{n.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            {fiscalLabel}
          </label>
          <Input
            placeholder="Número del registro fiscal"
            value={fiscalNumber}
            onChange={(e) => setFiscalNumber(e.target.value)}
          />
        </div>

        <DropZone
          label={`Documento: ${fiscalLabel}`}
          file={fiscalFile}
          onChange={setFiscalFile}
          error={fileErrors.fiscal}
        />

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            {mercantileLabel}
          </label>
          <Input
            placeholder="Número del registro mercantil"
            value={mercantileNumber}
            onChange={(e) => setMercantileNumber(e.target.value)}
          />
        </div>

        <DropZone
          label={`Documento: ${mercantileLabel}`}
          file={mercantileFile}
          onChange={setMercantileFile}
          error={fileErrors.mercantile}
        />

        {error && <p className="text-xs text-error-500">{error}</p>}
      </div>

      <button
        type="submit"
        disabled={loading || !name || !country || !fiscalNumber || !mercantileNumber}
        className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
      >
        {loading ? "Guardando..." : "Finalizar"}
      </button>
    </form>
  );
};
