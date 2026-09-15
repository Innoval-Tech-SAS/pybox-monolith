import { Select } from "@/ui/components/inputs/select";
import { PROVIDER_OPTIONS } from "@/provider-credentials/constants/provider-field-specs";
import type { CredentialFormProps } from "@/provider-credentials/types/props/credential-form-props";
import type { CredentialProvider } from "@/provider-credentials/types/provider-credential-types";

const GLOBAL = "__global__";

export const CredentialForm: React.FC<CredentialFormProps> = ({
  editingId,
  provider,
  onChangeProvider,
  countryValue,
  onChangeCountry,
  countries,
  spec,
  secrets,
  onChangeSecret,
  publicConfig,
  onChangePublicConfig,
  isActive,
  onChangeIsActive,
  saving,
  onSave,
  onCancelEdit,
}) => {
  const countryOptions = [
    { value: GLOBAL, label: "Global (todos los países)" },
    ...countries.map((c) => ({ value: c.code, label: c.name })),
  ];

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
      <h2 className="mb-4 text-base font-medium text-gray-800 dark:text-white/90">
        {editingId ? "Editar credencial" : "Nueva credencial"}
      </h2>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-1">
          <span className="text-sm text-gray-600 dark:text-gray-400">Proveedor</span>
          <Select
            options={PROVIDER_OPTIONS}
            value={provider}
            onChange={(v) => onChangeProvider(v as CredentialProvider)}
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm text-gray-600 dark:text-gray-400">País</span>
          <Select
            options={countryOptions}
            value={countryValue}
            onChange={onChangeCountry}
          />
        </label>

        {spec.secretKeys.map((key) => (
          <label key={key} className="flex flex-col gap-1">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {key} <span className="text-warning-500">· secreto</span>
            </span>
            <input
              type="password"
              autoComplete="new-password"
              placeholder={editingId ? "•••• (dejar vacío para no cambiar)" : ""}
              className="rounded-lg border border-gray-300 bg-transparent px-3 py-2 text-sm dark:border-gray-700"
              value={secrets[key] ?? ""}
              onChange={(e) => onChangeSecret(key, e.target.value)}
            />
          </label>
        ))}

        {spec.publicKeys.map((key) => (
          <label key={key} className="flex flex-col gap-1">
            <span className="text-sm text-gray-600 dark:text-gray-400">{key}</span>
            <input
              type="text"
              className="rounded-lg border border-gray-300 bg-transparent px-3 py-2 text-sm dark:border-gray-700"
              value={publicConfig[key] ?? ""}
              onChange={(e) => onChangePublicConfig(key, e.target.value)}
            />
          </label>
        ))}
      </div>

      <div className="mt-4 flex items-center justify-between">
        <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <input
            type="checkbox"
            checked={isActive}
            onChange={(e) => onChangeIsActive(e.target.checked)}
          />
          Activa
        </label>
        <div className="flex gap-2">
          {editingId && (
            <button
              type="button"
              onClick={onCancelEdit}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm dark:border-gray-700"
            >
              Cancelar
            </button>
          )}
          <button
            type="button"
            onClick={onSave}
            disabled={saving}
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          >
            {saving ? "Guardando…" : "Guardar"}
          </button>
        </div>
      </div>
    </div>
  );
};
