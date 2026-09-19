import { Select } from "@/ui/components/inputs/select";
import { Input } from "@/ui/components/inputs/input";
import { PasswordInput } from "@/ui/components/inputs/password-input";
import { Switch } from "@/ui/components/switch";
import { Button } from "@/ui/components/button/button";
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave();
  };

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
      <h2 className="mb-4 text-base font-medium text-gray-800 dark:text-white/90">
        {editingId ? "Editar credencial" : "Nueva credencial"}
      </h2>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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
            <PasswordInput
              key={key}
              label={`${key} · secreto`}
              autoComplete="new-password"
              placeholder={editingId ? "•••• (dejar vacío para no cambiar)" : ""}
              value={secrets[key] ?? ""}
              onChange={(e) => onChangeSecret(key, e.target.value)}
            />
          ))}

          {spec.publicKeys.map((key) => (
            <Input
              key={key}
              label={key}
              type="text"
              value={publicConfig[key] ?? ""}
              onChange={(e) => onChangePublicConfig(key, e.target.value)}
            />
          ))}
        </div>

        <div className="mt-4 flex items-center justify-between">
          <Switch
            checked={isActive}
            onChange={onChangeIsActive}
            label="Activa"
          />
          <div className="flex gap-2">
            {editingId && (
              <Button type="button" size="sm" variant="outline" onClick={onCancelEdit}>
                Cancelar
              </Button>
            )}
            <Button type="submit" size="sm" loading={saving} loadingText="Guardando…">
              Guardar
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};
