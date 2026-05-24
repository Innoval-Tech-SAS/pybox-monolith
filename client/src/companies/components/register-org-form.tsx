import React from "react";
import { Building2, Hash, Info, Mail, User, UserPlus, Users } from "lucide-react";
import { useCountries } from "@/hooks/use-countries";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { WizardForm } from "@/ui/components/wizard-form";
import { UserPicker } from "@/ui/components/user-picker";
import { DOC_TYPE_LABELS } from "@/constants/countries/doc-type-labels";
import { REP_MODES, WIZARD_STEPS } from "../constants/register-org-form-options";
import { useRegisterOrg } from "../hooks/use-register-org";
import type { UserSummary } from "@/types/users/user-types";

const ICONS: Record<"user" | "users" | "user-plus", React.ReactNode> = {
  user: <User size={16} />,
  users: <Users size={16} />,
  "user-plus": <UserPlus size={16} />,
};

export const RegisterOrgForm: React.FC = () => {
  const {
    isSubmitting,
    name, setName,
    country, setCountry,
    fiscalDocNumber, setFiscalDocNumber,
    description, setDescription,
    fiscalFile, fiscalError, handleFiscalFileChange,
    mercantileFile, mercantileError, handleMercantileFileChange,
    repFile, repFileError, handleRepFileChange,
    repMode, setRepMode,
    selectedUser, setSelectedUser,
    repFirstname, setRepFirstname,
    repLastname, setRepLastname,
    repEmail, setRepEmail,
    repDocType, setRepDocType,
    repDocNumber, setRepDocNumber,
    handleSubmit,
  } = useRegisterOrg();

  const { countries, loading: loadingCountries } = useCountries();
  const selectedCountry = countries.find((c) => c.code === country);
  const repDocTypes = selectedCountry?.documentTypes ?? [];

  const canAdvance = (step: number) => {
    if (step === 0) return !!name.trim() && !!country;
    if (step === 1) return !!fiscalFile && !fiscalError && !!mercantileFile && !mercantileError;
    return false;
  };

  const repModeValid =
    repMode === "self" ||
    (repMode === "select" && !!selectedUser) ||
    (repMode === "create" &&
      !!repFirstname.trim() &&
      !!repLastname.trim() &&
      !!repEmail.trim() &&
      !!repDocType &&
      !!repDocNumber.trim());

  const canSubmit = !!repFile && !repFileError && repModeValid;

  return (
    <WizardForm
      steps={WIZARD_STEPS}
      canAdvance={canAdvance}
      canSubmit={canSubmit}
      onSubmit={handleSubmit}
      loading={isSubmitting}
      submitLabel="Crear organización"
      loadingLabel="Creando organización..."
    >
      {(step) => (
        <>
          {step === 0 && (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <Label>Nombre de la organización <span className="text-error-500">*</span></Label>
                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
                    <Building2 size={16} />
                  </span>
                  <Input
                    name="name"
                    placeholder="Nombre legal o comercial"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={isSubmitting}
                    className="pl-11"
                  />
                </div>
              </div>

              <div>
                <Label>País <span className="text-error-500">*</span></Label>
                <CountrySelect
                  mode="NAME"
                  countries={countries}
                  placeholder={loadingCountries ? "Cargando..." : "Selecciona el país"}
                  value={country}
                  onChange={(v) => { setCountry(v); setRepDocType(""); }}
                  disabled={isSubmitting || loadingCountries}
                />
              </div>

              <div>
                <Label>Número de documento fiscal</Label>
                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
                    <Hash size={16} />
                  </span>
                  <Input
                    name="fiscal_document_number"
                    placeholder="Ej: 901.234.567-8"
                    value={fiscalDocNumber}
                    onChange={(e) => setFiscalDocNumber(e.target.value)}
                    disabled={isSubmitting}
                    className="pl-11"
                  />
                </div>
              </div>

              <div>
                <Label>Descripción</Label>
                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
                    <Info size={16} />
                  </span>
                  <Input
                    name="description"
                    placeholder="Breve descripción"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    disabled={isSubmitting}
                    className="pl-11"
                  />
                </div>
              </div>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-4">
              <DropZone
                label="Documento fiscal (RUT, NIT, etc.)"
                file={fiscalFile}
                onChange={handleFiscalFileChange}
                error={fiscalError ?? undefined}
              />
              <DropZone
                label="Documento mercantil (Cámara de Comercio, etc.)"
                file={mercantileFile}
                onChange={handleMercantileFileChange}
                error={mercantileError ?? undefined}
              />
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div>
                <Label>Representante legal <span className="text-error-500">*</span></Label>
                <div className="flex flex-col gap-2 sm:flex-row">
                  {REP_MODES.map((m) => (
                    <button
                      key={m.value}
                      type="button"
                      onClick={() => setRepMode(m.value)}
                      disabled={isSubmitting}
                      className={`flex flex-1 items-center gap-2 rounded-lg border px-4 py-3 text-sm font-medium transition ${
                        repMode === m.value
                          ? "border-brand-500 bg-brand-50 text-brand-700 dark:border-brand-400 dark:bg-brand-500/10 dark:text-brand-400"
                          : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-400 dark:hover:bg-white/3"
                      }`}
                    >
                      {ICONS[m.iconName]}
                      <span>{m.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {repMode === "select" && (
                <div>
                  <Label>Selecciona el representante <span className="text-error-500">*</span></Label>
                  <UserPicker
                    value={selectedUser?.id ?? null}
                    onChange={(u: UserSummary | null) => setSelectedUser(u)}
                  />
                </div>
              )}

              {repMode === "create" && (
                <div className="rounded-xl border border-gray-200 p-4 dark:border-gray-700">
                  <p className="mb-4 text-sm font-medium text-gray-700 dark:text-gray-300">Datos del nuevo representante</p>
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                      <Label>Nombre <span className="text-error-500">*</span></Label>
                      <Input placeholder="Nombre" value={repFirstname} onChange={(e) => setRepFirstname(e.target.value)} disabled={isSubmitting} />
                    </div>
                    <div>
                      <Label>Apellido <span className="text-error-500">*</span></Label>
                      <Input placeholder="Apellido" value={repLastname} onChange={(e) => setRepLastname(e.target.value)} disabled={isSubmitting} />
                    </div>
                    <div>
                      <Label>Correo <span className="text-error-500">*</span></Label>
                      <div className="relative">
                        <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
                          <Mail size={16} />
                        </span>
                        <Input type="email" placeholder="correo@empresa.com" value={repEmail} onChange={(e) => setRepEmail(e.target.value)} disabled={isSubmitting} className="pl-11" />
                      </div>
                    </div>
                    <div>
                      <Label>Tipo de documento <span className="text-error-500">*</span></Label>
                      <select
                        value={repDocType}
                        onChange={(e) => setRepDocType(e.target.value)}
                        disabled={!repDocTypes.length || isSubmitting}
                        className="h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 disabled:opacity-40"
                      >
                        <option value="">Selecciona el tipo</option>
                        {repDocTypes.map((dt) => (
                          <option key={dt} value={dt}>{DOC_TYPE_LABELS[dt] ?? dt}</option>
                        ))}
                      </select>
                    </div>
                    <div className="sm:col-span-2">
                      <Label>Número de documento <span className="text-error-500">*</span></Label>
                      <div className="relative">
                        <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
                          <Hash size={16} />
                        </span>
                        <Input placeholder="Número de documento" value={repDocNumber} onChange={(e) => setRepDocNumber(e.target.value)} disabled={isSubmitting} className="pl-11" />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <DropZone
                label="Documento de identidad del representante"
                file={repFile}
                onChange={handleRepFileChange}
                error={repFileError ?? undefined}
              />
            </div>
          )}
        </>
      )}
    </WizardForm>
  );
};
