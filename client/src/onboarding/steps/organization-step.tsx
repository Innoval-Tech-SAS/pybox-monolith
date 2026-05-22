import React, { useState } from "react";
import { Input } from "@/ui/components/inputs/input";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { useOrganizationOnboarding } from "@/hooks/use-organization-onboarding";

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
  const { saveOrganization, loading, error, clearError } = useOrganizationOnboarding();

  const [name, setName] = useState("");
  const [country, setCountry] = useState("");
  const [fiscalNumber, setFiscalNumber] = useState("");
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
      fiscalDocumentFile: fiscalFile!,
      mercantileDocumentFile: mercantileFile!,
    });
    onDone();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white/90">Datos de la empresa</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Completa la información de tu empresa para activar la cuenta.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Nombre de la empresa
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
          <CountrySelect
            mode="NAME"
            required
            value={country}
            onChange={setCountry}
            placeholder="Selecciona el país"
          />
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
        disabled={loading || !name || !country || !fiscalNumber}
        className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
      >
        {loading ? "Guardando..." : "Finalizar"}
      </button>
    </form>
  );
};
