import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { PaymentMethod, PaymentMethodCreatePayload, PaymentMethodUpdatePayload } from "@/types/payment-methods/payment-method-types";

export const usePaymentMethods = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [items, setItems] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchItems = useCallback(() => {
    if (!organizationId) return;
    setLoading(true);
    apiClient(`/payment-methods/?organizationId=${organizationId}`, { method: "GET" })
      .then((data: PaymentMethod[]) => setItems(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [organizationId, apiClient]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

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

  const update = async (id: number, payload: PaymentMethodUpdatePayload): Promise<PaymentMethod | null> => {
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

  const remove = async (id: number): Promise<boolean> => {
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

  return { items, loading, saving, refetch: fetchItems, create, update, remove };
};
