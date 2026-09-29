import { useCallback, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type {
  PaymentGatewayCredential,
  PaymentGatewayCredentialCreatePayload,
  PaymentGatewayCredentialUpdatePayload,
} from "@/companies/types/payment-gateway-credential-types";

export const usePaymentGatewayCredentials = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [saving, setSaving] = useState(false);

  const fetchItems = useCallback(() => {
    if (!organizationId) return Promise.resolve([]);
    return apiClient(`/payment-gateway-credentials/?organizationId=${organizationId}`, {
      method: "GET",
    }) as Promise<PaymentGatewayCredential[]>;
  }, [organizationId, apiClient]);

  const { data: items, loading, error, refetch, setData: setItems } = useAsyncResource<PaymentGatewayCredential[]>(
    fetchItems,
    [],
    [organizationId],
  );

  const create = async (payload: PaymentGatewayCredentialCreatePayload): Promise<PaymentGatewayCredential | null> => {
    setSaving(true);
    try {
      const created: PaymentGatewayCredential = await apiClient(
        `/payment-gateway-credentials/?organizationId=${organizationId}`,
        { method: "POST", body: JSON.stringify(payload) },
      );
      setItems((prev) => [...prev, created]);
      return created;
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  const update = async (
    id: string,
    payload: PaymentGatewayCredentialUpdatePayload,
  ): Promise<PaymentGatewayCredential | null> => {
    setSaving(true);
    try {
      const updated: PaymentGatewayCredential = await apiClient(
        `/payment-gateway-credentials/${id}?organizationId=${organizationId}`,
        { method: "PATCH", body: JSON.stringify(payload) },
      );
      setItems((prev) => prev.map((c) => (c.id === id ? updated : c)));
      return updated;
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id: string): Promise<boolean> => {
    setSaving(true);
    try {
      await apiClient(`/payment-gateway-credentials/${id}?organizationId=${organizationId}`, { method: "DELETE" });
      setItems((prev) => prev.filter((c) => c.id !== id));
      return true;
    } catch {
      return false;
    } finally {
      setSaving(false);
    }
  };

  return { items, loading, error, saving, refetch, create, update, remove };
};
