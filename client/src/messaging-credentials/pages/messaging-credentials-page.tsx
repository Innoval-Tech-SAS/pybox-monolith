import { useMemo, useState } from "react";
import { KeyRound } from "lucide-react";
import { useCountries } from "@/hooks/use-countries";
import { useToast } from "@/context/toast-context";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { ModuleBase } from "@/ui/components/common/module-base";
import { useProviderCredentials } from "../hooks/use-provider-credentials";
import { PROVIDER_FIELD_SPECS } from "../constants/provider-field-specs";
import { CredentialForm } from "../components/credential-form";
import { CredentialsTable } from "../components/credentials-table";
import {
  CredentialProvider,
  ProviderCredential,
} from "../types/provider-credential-types";

const GLOBAL = "__global__";

const emptyRecord = (keys: string[]): Record<string, string> =>
  Object.fromEntries(keys.map((k) => [k, ""]));

export const MessagingCredentialsPage: React.FC = () => {
  const { items, loading, saving, upsert, remove } = useProviderCredentials();
  const { countries } = useCountries();
  const toast = useToast();

  const [provider, setProvider] = useState<CredentialProvider>("360NRS_SMS");
  const [countryValue, setCountryValue] = useState<string>(GLOBAL);
  const [secrets, setSecrets] = useState<Record<string, string>>({});
  const [publicConfig, setPublicConfig] = useState<Record<string, string>>({});
  const [isActive, setIsActive] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [credentialToDelete, setCredentialToDelete] = useState<ProviderCredential | null>(null);
  const [deleting, setDeleting] = useState(false);

  const spec = PROVIDER_FIELD_SPECS[provider];

  const resetForm = (nextProvider: CredentialProvider = provider) => {
    const s = PROVIDER_FIELD_SPECS[nextProvider];
    setProvider(nextProvider);
    setCountryValue(GLOBAL);
    setSecrets(emptyRecord(s.secretKeys));
    setPublicConfig(emptyRecord(s.publicKeys));
    setIsActive(true);
    setEditingId(null);
  };

  const startEdit = (row: ProviderCredential) => {
    const s = PROVIDER_FIELD_SPECS[row.provider];
    setProvider(row.provider);
    setCountryValue(row.countryCode ?? GLOBAL);
    setSecrets(emptyRecord(s.secretKeys)); // write-only: nunca se precargan secretos
    setPublicConfig({ ...emptyRecord(s.publicKeys), ...row.publicConfig });
    setIsActive(row.isActive);
    setEditingId(row.id);
  };

  const onChangeProvider = (value: CredentialProvider) => resetForm(value);

  const save = async () => {
    const lookupKey = spec.lookupFrom ? publicConfig[spec.lookupFrom] || null : null;
    const secretsToSend = Object.fromEntries(
      Object.entries(secrets).filter(([, v]) => v.trim() !== ""),
    );
    try {
      await upsert({
        countryCode: countryValue === GLOBAL ? null : countryValue,
        provider,
        secrets: secretsToSend,
        publicConfig,
        lookupKey,
        isActive,
      });
      toast.success?.("Credencial guardada");
      resetForm(provider);
    } catch {
      /* useApiClient ya muestra el error */
    }
  };

  const onDelete = (row: ProviderCredential) => setCredentialToDelete(row);

  const confirmDelete = async () => {
    if (!credentialToDelete) return;
    setDeleting(true);
    try {
      await remove(credentialToDelete.id);
      toast.success?.("Credencial eliminada");
      setCredentialToDelete(null);
    } catch {
      /* manejado por useApiClient */
    } finally {
      setDeleting(false);
    }
  };

  const countryLabel = useMemo(() => {
    const map = new Map(countries.map((c) => [c.code, c.name]));
    return (code: string | null) => (code ? map.get(code) ?? code : "Global");
  }, [countries]);

  return (
    <ModuleBase pageTitle="Credenciales de mensajería" pageIcon={KeyRound} breadcrumbItems={[]} showBack>
      <div className="flex flex-col gap-6">
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Claves de envío (SMS, Email, WhatsApp) cifradas por país. Los secretos nunca se
        muestran: se escriben una vez y para rotarlos se vuelve a escribir el valor.
      </p>

      <CredentialForm
        editingId={editingId}
        provider={provider}
        onChangeProvider={onChangeProvider}
        countryValue={countryValue}
        onChangeCountry={setCountryValue}
        countries={countries}
        spec={spec}
        secrets={secrets}
        onChangeSecret={(key, value) => setSecrets((s) => ({ ...s, [key]: value }))}
        publicConfig={publicConfig}
        onChangePublicConfig={(key, value) => setPublicConfig((p) => ({ ...p, [key]: value }))}
        isActive={isActive}
        onChangeIsActive={setIsActive}
        saving={saving}
        onSave={save}
        onCancelEdit={() => resetForm(provider)}
      />

      <CredentialsTable
        items={items}
        loading={loading}
        countryLabel={countryLabel}
        onEdit={startEdit}
        onDelete={onDelete}
      />

      <ConfirmModal
        isOpen={!!credentialToDelete}
        onClose={() => setCredentialToDelete(null)}
        onConfirm={confirmDelete}
        title="Eliminar credencial"
        message={
          credentialToDelete
            ? `¿Eliminar la credencial de ${PROVIDER_FIELD_SPECS[credentialToDelete.provider].label}? Esto puede detener el envío de comunicaciones que dependen de ella.`
            : ""
        }
        loading={deleting}
      />
      </div>
    </ModuleBase>
  );
};
