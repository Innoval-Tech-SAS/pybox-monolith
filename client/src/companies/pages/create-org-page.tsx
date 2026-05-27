import React, { useState } from "react";
import { useNavigate } from "react-router";
import {
  Building2,
  CheckCircle,
  FileText,
  Hash,
  Info,
  Mail,
  User,
  UserPlus,
  Users,
} from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Label } from "@/ui/components/inputs/label";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { UserPicker } from "@/ui/components/user-picker";
import { useCountries } from "@/hooks/use-countries";
import { DOC_TYPE_LABELS } from "@/constants/countries/doc-type-labels";
import {
  ORG_FISCAL_NAMES,
  ORG_MERCANTILE_NAMES,
} from "@/onboarding/constants/organization-documents";
import { REP_MODES } from "../constants/register-org-form-options";
import { useRegisterOrg } from "../hooks/use-register-org";
import type { UserSummary } from "@/types/users/user-types";

const INPUT_BASE =
  "h-11 w-full rounded-lg border appearance-none px-4 py-2.5 text-sm shadow-theme-xs placeholder:text-gray-400 focus:outline-hidden focus:ring-3 bg-transparent text-gray-800 border-gray-300 focus:border-brand-300 focus:ring-brand-500/20 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:border-gray-700 dark:focus:border-brand-800";

const ICONS: Record<"user" | "users" | "user-plus", React.ReactNode> = {
  user: <User size={16} />,
  users: <Users size={16} />,
  "user-plus": <UserPlus size={16} />,
};

interface StepDef {
  label: string;
  description: string;
  icon: React.ReactNode;
}

const StepSidebar: React.FC<{ steps: StepDef[]; current: number }> = ({
  steps,
  current,
}) => (
  <div className="flex flex-col gap-0">
    {steps.map((s, i) => {
      const n = i + 1;
      const done = n < current;
      const active = n === current;
      return (
        <div key={n} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div
              className={`flex size-9 shrink-0 items-center justify-center rounded-full border-2 text-sm font-semibold transition-all ${
                done
                  ? "border-brand-500 bg-brand-500 text-white"
                  : active
                    ? "border-brand-500 bg-white text-brand-600 dark:bg-gray-900"
                    : "border-gray-200 bg-white text-gray-400 dark:border-gray-700 dark:bg-gray-900"
              }`}
            >
              {done ? <CheckCircle size={16} /> : s.icon}
            </div>
            {i < steps.length - 1 && (
              <div
                className={`my-1 min-h-10 w-px flex-1 transition-colors ${
                  done ? "bg-brand-500" : "bg-gray-200 dark:bg-gray-700"
                }`}
              />
            )}
          </div>
          <div className="pb-8">
            <p
              className={`text-sm font-semibold leading-9 ${
                active
                  ? "text-gray-800 dark:text-white/90"
                  : done
                    ? "text-brand-600 dark:text-brand-400"
                    : "text-gray-400 dark:text-gray-600"
              }`}
            >
              {s.label}
            </p>
            <p
              className={`-mt-1 text-xs ${
                active || done
                  ? "text-gray-500 dark:text-gray-400"
                  : "text-gray-300 dark:text-gray-700"
              }`}
            >
              {s.description}
            </p>
          </div>
        </div>
      );
    })}
  </div>
);

export const CreateOrgPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);

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
  const fiscalLabel = (country && ORG_FISCAL_NAMES[country]) ?? "Documento fiscal";
  const mercantileLabel = (country && ORG_MERCANTILE_NAMES[country]) ?? "Documento mercantil";

  const stepDefs: StepDef[] = [
    { label: "Empresa", description: "Información general", icon: <Building2 size={14} /> },
    { label: "Documentos", description: "Archivos requeridos", icon: <FileText size={14} /> },
    { label: "Representante", description: "Persona legal", icon: <User size={14} /> },
  ];

  const canGoStep2 = !!name.trim() && !!country;
  const canGoStep3 =
    !!fiscalFile && !fiscalError && !!mercantileFile && !mercantileError;
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

  const renderStep1 = () => (
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
          <Label>
            Nombre <span className="text-error-500">*</span>
          </Label>
          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <Building2 size={16} />
            </span>
            <input
              type="text"
              placeholder="Nombre legal o comercial"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={isSubmitting}
              className={`${INPUT_BASE} pl-11`}
            />
          </div>
        </div>
        <div>
          <Label>
            País <span className="text-error-500">*</span>
          </Label>
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
          />
        </div>
        <div>
          <Label>Número de documento fiscal</Label>
          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <Hash size={16} />
            </span>
            <input
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
          <Label>Descripción</Label>
          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <Info size={16} />
            </span>
            <input
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
        <button
          type="button"
          onClick={() => navigate("/my-companies")}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3"
        >
          Cancelar
        </button>
        <button
          type="button"
          onClick={() => setStep(2)}
          disabled={!canGoStep2}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:opacity-50"
        >
          Siguiente
        </button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">
          Documentos de la empresa
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Sube los documentos requeridos para la verificación.
        </p>
      </div>
      <div className="space-y-4">
        <DropZone
          label={fiscalLabel}
          file={fiscalFile}
          onChange={handleFiscalFileChange}
          error={fiscalError ?? undefined}
        />
        <DropZone
          label={mercantileLabel}
          file={mercantileFile}
          onChange={handleMercantileFileChange}
          error={mercantileError ?? undefined}
        />
      </div>
      <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
        <button
          type="button"
          onClick={() => setStep(1)}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3"
        >
          Atrás
        </button>
        <button
          type="button"
          onClick={() => setStep(3)}
          disabled={!canGoStep3}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:opacity-50"
        >
          Siguiente
        </button>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">
          Representante legal
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Designa al representante legal de la empresa.
        </p>
      </div>
      <div className="space-y-4">
        <div>
          <Label>
            Representante legal <span className="text-error-500">*</span>
          </Label>
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
            <Label>
              Selecciona el representante <span className="text-error-500">*</span>
            </Label>
            <UserPicker
              value={selectedUser?.id ?? null}
              onChange={(u: UserSummary | null) => setSelectedUser(u)}
            />
          </div>
        )}

        {repMode === "create" && (
          <div className="rounded-xl border border-gray-200 p-4 dark:border-gray-700">
            <p className="mb-4 text-sm font-medium text-gray-700 dark:text-gray-300">
              Datos del nuevo representante
            </p>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <Label>
                  Nombre <span className="text-error-500">*</span>
                </Label>
                <input
                  type="text"
                  placeholder="Nombre"
                  value={repFirstname}
                  onChange={(e) => setRepFirstname(e.target.value)}
                  disabled={isSubmitting}
                  className={INPUT_BASE}
                />
              </div>
              <div>
                <Label>
                  Apellido <span className="text-error-500">*</span>
                </Label>
                <input
                  type="text"
                  placeholder="Apellido"
                  value={repLastname}
                  onChange={(e) => setRepLastname(e.target.value)}
                  disabled={isSubmitting}
                  className={INPUT_BASE}
                />
              </div>
              <div>
                <Label>
                  Correo <span className="text-error-500">*</span>
                </Label>
                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
                    <Mail size={16} />
                  </span>
                  <input
                    type="email"
                    placeholder="correo@empresa.com"
                    value={repEmail}
                    onChange={(e) => setRepEmail(e.target.value)}
                    disabled={isSubmitting}
                    className={`${INPUT_BASE} pl-11`}
                  />
                </div>
              </div>
              <div>
                <Label>
                  Tipo de documento <span className="text-error-500">*</span>
                </Label>
                <select
                  value={repDocType}
                  onChange={(e) => setRepDocType(e.target.value)}
                  disabled={!repDocTypes.length || isSubmitting}
                  className={INPUT_BASE}
                >
                  <option value="">Selecciona el tipo</option>
                  {repDocTypes.map((dt) => (
                    <option key={dt} value={dt}>
                      {DOC_TYPE_LABELS[dt] ?? dt}
                    </option>
                  ))}
                </select>
              </div>
              <div className="sm:col-span-2">
                <Label>
                  Número de documento <span className="text-error-500">*</span>
                </Label>
                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
                    <Hash size={16} />
                  </span>
                  <input
                    type="text"
                    placeholder="Número de documento"
                    value={repDocNumber}
                    onChange={(e) => setRepDocNumber(e.target.value)}
                    disabled={isSubmitting}
                    className={`${INPUT_BASE} pl-11`}
                  />
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
      <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
        <button
          type="button"
          onClick={() => setStep(2)}
          disabled={isSubmitting}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3"
        >
          Atrás
        </button>
        <button
          type="submit"
          disabled={!canSubmit || isSubmitting}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:opacity-50"
        >
          {isSubmitting ? "Creando empresa..." : "Crear empresa"}
        </button>
      </div>
    </form>
  );

  const currentContent =
    step === 1 ? renderStep1() : step === 2 ? renderStep2() : renderStep3();

  return (
    <ModuleBase
      pageTitle="Crear empresa"
      breadcrumbItems={[{ label: "Mis Empresas", path: "/my-companies" }]}
    >
      <div className="flex gap-10">
        <aside className="hidden w-52 shrink-0 pt-1 lg:block">
          <StepSidebar steps={stepDefs} current={step} />
        </aside>
        <div className="hidden w-px self-stretch bg-gray-100 dark:bg-white/5 lg:block" />
        <div className="min-w-0 flex-1">{currentContent}</div>
      </div>
    </ModuleBase>
  );
};
