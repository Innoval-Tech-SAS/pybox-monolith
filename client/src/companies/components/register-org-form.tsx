import { Building2, Hash, Info, Mail, Users } from "lucide-react";
import { useNationalities } from "@/hooks/use-nationalities";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { Select } from "@/ui/components/inputs/select";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { FileInput } from "@/ui/components/inputs/file-input";
import {
  DOC_TYPE_OPTIONS,
  REP_MODES,
} from "../constants/register-org-form-options";
import { useRegisterOrg } from "../hooks/use-register-org";

export const RegisterOrgForm: React.FC = () => {
  const {
    isSubmitting,
    name, setName,
    country, setCountry,
    fiscalDocNumber, setFiscalDocNumber,
    description, setDescription,
    mercantileFile, mercantileError, handleMercantileFileChange,
    repFile, repFileError, handleRepFileChange,
    repMode, setRepMode,
    selectedUserId, setSelectedUserId,
    repFirstname, setRepFirstname,
    repLastname, setRepLastname,
    repEmail, setRepEmail,
    repDocType, setRepDocType,
    repDocNumber, setRepDocNumber,
    formRef,
    handleSubmit,
    handleReset,
  } = useRegisterOrg();

  const { nationalities, loading: loadingCountries } = useNationalities();

  return (
    <form ref={formRef} onSubmit={handleSubmit} className="space-y-6">

      {/* Org data */}
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
            nationalities={nationalities}
            placeholder={loadingCountries ? "Cargando..." : "Selecciona el país"}
            value={country}
            onChange={setCountry}
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

      {/* Mercantile document file */}
      <div>
        <Label>Documento mercantil (Cámara de Comercio, etc.) <span className="text-error-500">*</span></Label>
        <FileInput
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={(e) => handleMercantileFileChange(e.target.files?.[0] ?? null)}
          disabled={isSubmitting}
        />
        {mercantileFile && (
          <p className="mt-1.5 text-xs text-gray-500">{mercantileFile.name} — {(mercantileFile.size / 1024 / 1024).toFixed(2)} MB</p>
        )}
        {mercantileError && <p className="mt-1.5 text-xs text-error-500">{mercantileError}</p>}
      </div>

      {/* Representative mode selector */}
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
              {m.icon}
              <span>{m.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* SELECT mode */}
      {repMode === "select" && (
        <div>
          <Label>ID del usuario representante <span className="text-error-500">*</span></Label>
          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              <Users size={16} />
            </span>
            <Input
              placeholder="ID del usuario"
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              disabled={isSubmitting}
              className="pl-11"
            />
          </div>
        </div>
      )}

      {/* CREATE mode */}
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
              <Select options={DOC_TYPE_OPTIONS} value={repDocType} onChange={setRepDocType} disabled={isSubmitting} />
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

      {/* Representative document file */}
      <div>
        <Label>Documento de identidad del representante <span className="text-error-500">*</span></Label>
        <FileInput
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={(e) => handleRepFileChange(e.target.files?.[0] ?? null)}
          disabled={isSubmitting}
        />
        {repFile && (
          <p className="mt-1.5 text-xs text-gray-500">{repFile.name} — {(repFile.size / 1024 / 1024).toFixed(2)} MB</p>
        )}
        {repFileError && <p className="mt-1.5 text-xs text-error-500">{repFileError}</p>}
      </div>

      {/* Actions */}
      <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button
          type="button"
          onClick={handleReset}
          disabled={isSubmitting}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-4 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 disabled:opacity-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3 dark:hover:text-gray-300"
        >
          Limpiar
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:bg-brand-300"
        >
          <Building2 size={16} />
          {isSubmitting ? "Creando organización..." : "Crear organización"}
        </button>
      </div>
    </form>
  );
};
