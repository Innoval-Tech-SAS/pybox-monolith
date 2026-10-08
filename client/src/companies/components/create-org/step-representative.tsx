import { Hash, Mail } from "lucide-react";
import { Label } from "@/ui/components/inputs/label";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { Select } from "@/ui/components/inputs/select";
import { Input } from "@/ui/components/inputs/input";
import { UserPicker } from "@/ui/components/user-picker";
import { Button } from "@/ui/components/button/button";
import { useDocumentTypes } from "@/hooks/use-document-types";
import { REP_MODES } from "@/companies/constants/register-org-form-options";
import { REPRESENTATIVE_MODE_ICONS } from "@/companies/constants/representative-mode-icons";
import { INPUT_BASE } from "@/companies/constants/create-org-styles";
import type { StepRepresentativeProps } from "@/companies/types/step-representative-props";
import type { UserSummary } from "@/types/users/user-types";

export const StepRepresentative: React.FC<StepRepresentativeProps> = ({
  form,
  repDocTypes,
  canSubmit,
  onBack,
}) => {
  const {
    isSubmitting,
    repFile, repFileError, handleRepFileChange,
    repMode, setRepMode,
    selectedUser, setSelectedUser,
    repFirstname, setRepFirstname,
    repLastname, setRepLastname,
    repEmail, setRepEmail,
    repDocType, setRepDocType,
    repDocNumber, setRepDocNumber,
    handleSubmit,
  } = form;
  const { labels: docTypeLabels } = useDocumentTypes();

  return (
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
                {REPRESENTATIVE_MODE_ICONS[m.iconName]}
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
                <Label htmlFor="create-org-rep-firstname">
                  Nombre <span className="text-error-500" aria-hidden="true">*</span>
                </Label>
                <Input
                  id="create-org-rep-firstname"
                  type="text"
                  placeholder="Nombre"
                  value={repFirstname}
                  onChange={(e) => setRepFirstname(e.target.value)}
                  disabled={isSubmitting}
                  required
                />
              </div>
              <div>
                <Label htmlFor="create-org-rep-lastname">
                  Apellido <span className="text-error-500" aria-hidden="true">*</span>
                </Label>
                <Input
                  id="create-org-rep-lastname"
                  type="text"
                  placeholder="Apellido"
                  value={repLastname}
                  onChange={(e) => setRepLastname(e.target.value)}
                  disabled={isSubmitting}
                  required
                />
              </div>
              <div>
                <Label htmlFor="create-org-rep-email">
                  Correo <span className="text-error-500" aria-hidden="true">*</span>
                </Label>
                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
                    <Mail size={16} />
                  </span>
                  <input
                    id="create-org-rep-email"
                    type="email"
                    placeholder="correo@empresa.com"
                    value={repEmail}
                    onChange={(e) => setRepEmail(e.target.value)}
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
                    Tipo de documento <span className="text-error-500" aria-hidden="true">*</span>
                  </span>
                  <Select
                    options={repDocTypes.map((dt) => ({ value: dt, label: docTypeLabels[dt] ?? dt }))}
                    value={repDocType}
                    onChange={setRepDocType}
                    disabled={!repDocTypes.length || isSubmitting}
                    placeholder="Selecciona el tipo"
                  />
                </Label>
              </div>
              <div className="sm:col-span-2">
                <Label htmlFor="create-org-rep-doc-number">
                  Número de documento <span className="text-error-500" aria-hidden="true">*</span>
                </Label>
                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
                    <Hash size={16} />
                  </span>
                  <input
                    id="create-org-rep-doc-number"
                    type="text"
                    placeholder="Número de documento"
                    value={repDocNumber}
                    onChange={(e) => setRepDocNumber(e.target.value)}
                    disabled={isSubmitting}
                    required
                    aria-required="true"
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
        <Button type="button" variant="outline" onClick={onBack} disabled={isSubmitting}>
          Atrás
        </Button>
        <Button type="submit" disabled={!canSubmit} loading={isSubmitting} loadingText="Creando empresa...">
          Crear empresa
        </Button>
      </div>
    </form>
  );
};
