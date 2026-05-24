import React, { useState } from "react";
import { User, UserPlus } from "lucide-react";
import { Input } from "@/ui/components/inputs/input";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { WizardForm } from "@/ui/components/wizard-form";
import { useOrganizationOnboarding } from "@/hooks/use-organization-onboarding";
import { useCountries } from "@/hooks/use-countries";
import { DOC_TYPE_LABELS } from "@/constants/countries/doc-type-labels";
import { REP_MODES, WIZARD_STEPS } from "@/onboarding/constants/organization-form";
import {
  ORG_FISCAL_NAMES,
  ORG_MERCANTILE_NAMES,
} from "@/onboarding/constants/organization-documents";
import type { OnboardingRepMode } from "@/types/onboarding/onboarding-types";
import type { StepDoneProps } from "@/types/props/onboarding-props";

const ICONS: Record<"user" | "user-plus", React.ReactNode> = {
  user: <User size={16} />,
  "user-plus": <UserPlus size={16} />,
};

export const OrganizationStep: React.FC<StepDoneProps> = ({ onDone }) => {
  const { saveOrganization, loading, error, clearError } = useOrganizationOnboarding();
  const { countries, loading: loadingCountries } = useCountries();

  const [name, setName] = useState("");
  const [country, setCountry] = useState("");
  const [fiscalNumber, setFiscalNumber] = useState("");
  const [fiscalFile, setFiscalFile] = useState<File | null>(null);
  const [mercantileFile, setMercantileFile] = useState<File | null>(null);
  const [repMode, setRepMode] = useState<OnboardingRepMode>("self");
  const [repFile, setRepFile] = useState<File | null>(null);
  const [repFirstname, setRepFirstname] = useState("");
  const [repLastname, setRepLastname] = useState("");
  const [repEmail, setRepEmail] = useState("");
  const [repDocType, setRepDocType] = useState("");
  const [repDocNumber, setRepDocNumber] = useState("");

  const selectedCountry = countries.find((c) => c.code === country);
  const fiscalLabel = country ? ORG_FISCAL_NAMES[country] ?? "Registro fiscal" : "Registro fiscal";
  const mercantileLabel = country ? ORG_MERCANTILE_NAMES[country] ?? "Registro mercantil" : "Registro mercantil";
  const repDocTypes = selectedCountry?.documentTypes ?? [];

  const canAdvance = (step: number) => {
    if (step === 0) return !!name.trim() && !!country && !!fiscalNumber.trim();
    if (step === 1) return !!fiscalFile && !!mercantileFile;
    return false;
  };

  const canSubmit =
    !!repFile &&
    (repMode === "self" ||
      (!!repFirstname.trim() && !!repLastname.trim() && !!repEmail.trim() && !!repDocType && !!repDocNumber.trim()));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    if (!repFile) return;
    await saveOrganization({
      name,
      country,
      fiscalDocumentNumber: fiscalNumber,
      fiscalDocumentFile: fiscalFile!,
      mercantileDocumentFile: mercantileFile!,
      representativeMode: repMode,
      representativeDocumentFile: repFile,
      repFirstname,
      repLastname,
      repEmail,
      repDocType,
      repDocNumber,
    });
    onDone();
  };

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white/90">Datos de la empresa</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Completa la información de tu empresa para activar la cuenta.
        </p>
      </div>

      <WizardForm
        steps={WIZARD_STEPS}
        canAdvance={canAdvance}
        canSubmit={canSubmit}
        onSubmit={handleSubmit}
        onBack={clearError}
        loading={loading}
      >
        {(step) => (
          <>
            {step === 0 && (
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
                    countries={countries}
                    value={country}
                    onChange={(v) => { setCountry(v); setRepDocType(""); }}
                    placeholder={loadingCountries ? "Cargando países..." : "Selecciona el país"}
                    disabled={loadingCountries}
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
              </div>
            )}

            {step === 1 && (
              <div className="space-y-4">
                <DropZone
                  label={`Documento: ${fiscalLabel}`}
                  file={fiscalFile}
                  onChange={setFiscalFile}
                />
                <DropZone
                  label={`Documento: ${mercantileLabel}`}
                  file={mercantileFile}
                  onChange={setMercantileFile}
                />
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Representante legal
                  </label>
                  <div className="flex flex-col gap-2 sm:flex-row">
                    {REP_MODES.map((m) => (
                      <button
                        key={m.value}
                        type="button"
                        onClick={() => setRepMode(m.value)}
                        className={`flex flex-1 items-center gap-2 rounded-lg border px-4 py-3 text-sm font-medium transition ${
                          repMode === m.value
                            ? "border-brand-500 bg-brand-50 text-brand-700 dark:border-brand-400 dark:bg-brand-500/10 dark:text-brand-400"
                            : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-400"
                        }`}
                      >
                        {ICONS[m.iconName]}
                        <span>{m.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {repMode === "create" && (
                  <div className="rounded-xl border border-gray-200 p-4 space-y-4 dark:border-gray-700">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Datos del representante</p>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Nombre</label>
                        <Input placeholder="Nombre" value={repFirstname} onChange={(e) => setRepFirstname(e.target.value)} />
                      </div>
                      <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Apellido</label>
                        <Input placeholder="Apellido" value={repLastname} onChange={(e) => setRepLastname(e.target.value)} />
                      </div>
                      <div className="sm:col-span-2">
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Correo</label>
                        <Input type="email" placeholder="correo@empresa.com" value={repEmail} onChange={(e) => setRepEmail(e.target.value)} />
                      </div>
                      <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Tipo de documento</label>
                        <select
                          value={repDocType}
                          onChange={(e) => setRepDocType(e.target.value)}
                          disabled={!repDocTypes.length}
                          className="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 disabled:opacity-40"
                        >
                          <option value="">Selecciona el tipo</option>
                          {repDocTypes.map((dt) => (
                            <option key={dt} value={dt}>{DOC_TYPE_LABELS[dt] ?? dt}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Número de documento</label>
                        <Input placeholder="Número" value={repDocNumber} onChange={(e) => setRepDocNumber(e.target.value)} />
                      </div>
                    </div>
                  </div>
                )}

                <DropZone
                  label="Documento de identidad del representante"
                  file={repFile}
                  onChange={setRepFile}
                />

                {error && <p className="text-xs text-error-500">{error}</p>}
              </div>
            )}
          </>
        )}
      </WizardForm>
    </div>
  );
};
