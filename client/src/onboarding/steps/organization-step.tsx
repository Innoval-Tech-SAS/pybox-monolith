import React, { useState } from "react";
import { CheckCircle, User, UserPlus } from "lucide-react";
import { Input } from "@/ui/components/inputs/input";
import { PasswordInput } from "@/ui/components/inputs/password-input";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { WizardForm } from "@/ui/components/wizard-form";
import { useOrganizationOnboarding } from "@/hooks/use-organization-onboarding";
import { useCountries } from "@/hooks/use-countries";
import { useEntitySectors } from "@/companies/hooks/use-entity-sectors";
import { useDocumentTypes } from "@/hooks/use-document-types";
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
  const { sectors, loading: loadingSectors } = useEntitySectors();
  const { labels: docTypeLabels } = useDocumentTypes();
  const [submitted, setSubmitted] = useState(false);

  const [name, setName] = useState("");
  const [sector, setSector] = useState("");
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
  const [repPassword, setRepPassword] = useState("");

  const selectedCountry = countries.find((c) => c.code === country);
  const fiscalLabel = country ? ORG_FISCAL_NAMES[country] ?? "Registro fiscal" : "Registro fiscal";
  const mercantileLabel = country ? ORG_MERCANTILE_NAMES[country] ?? "Registro mercantil" : "Registro mercantil";
  const repDocTypes = selectedCountry?.documentTypes ?? [];

  const canAdvance = (step: number) => {
    if (step === 0) return !!name.trim() && !!sector && !!country && !!fiscalNumber.trim();
    if (step === 1) return !!fiscalFile && !!mercantileFile;
    return false;
  };

  const canSubmit =
    !!repFile &&
    (repMode === "self" ||
      (!!repFirstname.trim() && !!repLastname.trim() && !!repEmail.trim() && !!repDocType && !!repDocNumber.trim() && !!repPassword.trim()));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    if (!repFile) return;
    const ok = await saveOrganization({
      name,
      sector,
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
      repPassword,
    });
    if (ok) setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="flex flex-col items-center gap-6 py-8 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-success-50 dark:bg-success-500/10">
          <CheckCircle size={32} className="text-success-500" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white/90">¡Empresa registrada!</h2>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Tu solicitud fue enviada. Creamos un ticket de verificación para revisar los documentos.
            Te notificaremos cuando sea aprobada.
          </p>
        </div>
        <button
          onClick={onDone}
          className="rounded-lg bg-brand-500 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600"
        >
          Entendido
        </button>
      </div>
    );
  }

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
                  <label htmlFor="org-name" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Nombre de la empresa <span className="text-error-500">*</span>
                  </label>
                  <Input
                    id="org-name"
                    placeholder="Ej. Mi Empresa S.A.S."
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label htmlFor="org-sector" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Sector <span className="text-error-500">*</span>
                  </label>
                  <select
                    id="org-sector"
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}
                    disabled={loadingSectors}
                    required
                    aria-required="true"
                    className="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 disabled:opacity-40"
                  >
                    <option value="">
                      {loadingSectors ? "Cargando sectores..." : "Selecciona el sector"}
                    </option>
                    {sectors.map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  {/* CountrySelect no expone `id`, por lo que no puede enlazarse vía htmlFor
                      sin modificar ui/components/inputs/country-select.tsx (fuera de alcance). */}
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    País de registro <span className="text-error-500">*</span>
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
                  <label htmlFor="org-fiscal-number" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {fiscalLabel} <span className="text-error-500">*</span>
                  </label>
                  <Input
                    id="org-fiscal-number"
                    placeholder="Número del registro fiscal"
                    value={fiscalNumber}
                    onChange={(e) => setFiscalNumber(e.target.value)}
                    required
                  />
                </div>
              </div>
            )}

            {step === 1 && (
              <div className="space-y-6">
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
                        <label htmlFor="rep-firstname" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Nombre <span className="text-error-500">*</span>
                        </label>
                        <Input id="rep-firstname" placeholder="Nombre" value={repFirstname} onChange={(e) => setRepFirstname(e.target.value)} required />
                      </div>
                      <div>
                        <label htmlFor="rep-lastname" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Apellido <span className="text-error-500">*</span>
                        </label>
                        <Input id="rep-lastname" placeholder="Apellido" value={repLastname} onChange={(e) => setRepLastname(e.target.value)} required />
                      </div>
                      <div className="sm:col-span-2">
                        <label htmlFor="rep-email" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Correo <span className="text-error-500">*</span>
                        </label>
                        <Input id="rep-email" type="email" placeholder="correo@empresa.com" value={repEmail} onChange={(e) => setRepEmail(e.target.value)} required />
                      </div>
                      <div>
                        <label htmlFor="rep-doc-type" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Tipo de documento <span className="text-error-500">*</span>
                        </label>
                        <select
                          id="rep-doc-type"
                          value={repDocType}
                          onChange={(e) => setRepDocType(e.target.value)}
                          disabled={!repDocTypes.length}
                          required
                          aria-required="true"
                          className="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 disabled:opacity-40"
                        >
                          <option value="">Selecciona el tipo</option>
                          {repDocTypes.map((dt) => (
                            <option key={dt} value={dt}>{docTypeLabels[dt] ?? dt}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label htmlFor="rep-doc-number" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                          Número de documento <span className="text-error-500">*</span>
                        </label>
                        <Input id="rep-doc-number" placeholder="Número" value={repDocNumber} onChange={(e) => setRepDocNumber(e.target.value)} required />
                      </div>
                      <div className="sm:col-span-2">
                        <PasswordInput
                          id="rep-password"
                          label="Contraseña temporal *"
                          placeholder="Debe cambiarla en su primer acceso"
                          value={repPassword}
                          onChange={(e) => setRepPassword(e.target.value)}
                          required
                          autoComplete="new-password"
                        />
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
