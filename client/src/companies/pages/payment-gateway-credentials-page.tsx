import { useState } from "react";
import { KeyRound } from "lucide-react";
import { useToast } from "@/context/toast-context";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { ModuleBase } from "@/ui/components/common/module-base";
import { PAYMENT_GATEWAY_FIELD_SPECS } from "@/companies/constants/payment-gateway-field-specs";
import type {
  PaymentGatewayCredential,
  PaymentGatewayProvider,
} from "@/companies/types/payment-gateway-credential-types";
import { usePaymentGatewayCredentials } from "../hooks/use-payment-gateway-credentials";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { PaymentGatewayCredentialForm } from "../components/payment-gateway-credential-form";
import { PaymentGatewayCredentialsTable } from "../components/payment-gateway-credentials-table";

const emptyRecord = (keys: string[]): Record<string, string> =>
  Object.fromEntries(keys.map((k) => [k, ""]));

export const PaymentGatewayCredentialsPage: React.FC = () => {
  const { orgId } = useOrgModule();
  const { build } = useBreadcrumb();
  const toast = useToast();
  const { items, loading, saving, create, update, remove } = usePaymentGatewayCredentials(orgId);

  const [provider, setProvider] = useState<PaymentGatewayProvider>("WOMPI");
  const [secrets, setSecrets] = useState<Record<string, string>>({});
  const [publicConfig, setPublicConfig] = useState<Record<string, string>>({});
  const [isActive, setIsActive] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [credentialToDelete, setCredentialToDelete] = useState<PaymentGatewayCredential | null>(null);
  const [deleting, setDeleting] = useState(false);

  const spec = PAYMENT_GATEWAY_FIELD_SPECS[provider];

  const resetForm = (nextProvider: PaymentGatewayProvider = provider) => {
    const s = PAYMENT_GATEWAY_FIELD_SPECS[nextProvider];
    setProvider(nextProvider);
    setSecrets(emptyRecord(s.secretKeys));
    setPublicConfig(emptyRecord(s.publicKeys));
    setIsActive(true);
    setEditingId(null);
  };

  const startEdit = (row: PaymentGatewayCredential) => {
    const s = PAYMENT_GATEWAY_FIELD_SPECS[row.provider];
    setProvider(row.provider);
    setSecrets(emptyRecord(s.secretKeys)); // write-only: nunca se precargan secretos
    setPublicConfig({ ...emptyRecord(s.publicKeys), ...row.publicConfig });
    setIsActive(row.isActive);
    setEditingId(row.id);
  };

  const save = async () => {
    const secretsToSend = Object.fromEntries(Object.entries(secrets).filter(([, v]) => v.trim() !== ""));
    if (editingId) {
      const result = await update(editingId, { secrets: secretsToSend, publicConfig, isActive });
      if (result) {
        toast.success?.("Credencial actualizada");
        resetForm(provider);
      }
      return;
    }
    const result = await create({ provider, secrets: secretsToSend, publicConfig, lookupKey: null, isActive });
    if (result) {
      toast.success?.("Pasarela conectada");
      resetForm(provider);
    }
  };

  const confirmDelete = async () => {
    if (!credentialToDelete) return;
    setDeleting(true);
    const ok = await remove(credentialToDelete.id);
    setDeleting(false);
    if (ok) {
      toast.success?.("Credencial eliminada");
      setCredentialToDelete(null);
    }
  };

  return (
    <ModuleBase pageTitle="Pasarelas de Cobro" pageIcon={KeyRound} breadcrumbItems={build()}>
      <div className="flex flex-col gap-6">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Conecta la cuenta propia de tu empresa en cada pasarela para cobrarle a tus
          deudores. PYBOX nunca recibe ni dispersa esos fondos: usa tus credenciales solo
          para armar el cobro directamente en tu cuenta. Los secretos nunca se muestran:
          se escriben una vez y para rotarlos se vuelve a escribir el valor.
        </p>

        <PaymentGatewayCredentialForm
          editingId={editingId}
          provider={provider}
          onChangeProvider={(v) => resetForm(v)}
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

        <PaymentGatewayCredentialsTable
          items={items}
          loading={loading}
          onEdit={startEdit}
          onDelete={setCredentialToDelete}
        />

        <ConfirmModal
          isOpen={!!credentialToDelete}
          onClose={() => setCredentialToDelete(null)}
          onConfirm={confirmDelete}
          title="Eliminar credencial"
          message={
            credentialToDelete
              ? `¿Eliminar la credencial de ${PAYMENT_GATEWAY_FIELD_SPECS[credentialToDelete.provider].label}? Esto detendrá el cobro de cuotas a través de esta pasarela.`
              : ""
          }
          loading={deleting}
        />
      </div>
    </ModuleBase>
  );
};
