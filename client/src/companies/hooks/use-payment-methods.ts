import { useCallback, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { PaymentMethod, PaymentMethodCreatePayload, PaymentMethodUpdatePayload } from "@/types/payment-methods/payment-method-types";

export const usePaymentMethods = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [saving, setSaving] = useState(false);

  const fetchItems = useCallback(() => {
    if (!organizationId) return Promise.resolve([]);
    return apiClient(`/payment-methods/?organizationId=${organizationId}`, { method: "GET" }) as Promise<PaymentMethod[]>;
  }, [organizationId, apiClient]);

  const { data: items, loading, error, refetch, setData: setItems } = useAsyncResource<PaymentMethod[]>(
    fetchItems,
    [],
    [organizationId],
  );

  const create = async (payload: PaymentMethodCreatePayload): Promise<PaymentMethod | null> => {
    setSaving(true);
    try {
      const created: PaymentMethod = await apiClient("/payment-methods/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setItems((prev) => [...prev, created]);
      return created;
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  const update = async (id: string, payload: PaymentMethodUpdatePayload): Promise<PaymentMethod | null> => {
    setSaving(true);
    try {
      const updated: PaymentMethod = await apiClient(
        `/payment-methods/${id}?organizationId=${organizationId}`,
        { method: "PATCH", body: JSON.stringify(payload) },
      );
      setItems((prev) => prev.map((m) => (m.id === id ? updated : m)));
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
      await apiClient(`/payment-methods/${id}?organizationId=${organizationId}`, { method: "DELETE" });
      setItems((prev) => prev.filter((m) => m.id !== id));
      return true;
    } catch {
      return false;
    } finally {
      setSaving(false);
    }
  };

  return { items, loading, error, saving, refetch, create, update, remove };
};
