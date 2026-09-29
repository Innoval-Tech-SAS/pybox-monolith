import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import {
  ProviderCredential,
  ProviderCredentialUpsert,
} from "../types/provider-credential-types";

const BASE = "/admin/messaging-credentials";

export const useProviderCredentials = () => {
  const { apiClient } = useApiClient();
  const [items, setItems] = useState<ProviderCredential[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiClient<ProviderCredential[]>(BASE, { method: "GET" });
      setItems(data);
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  useEffect(() => {
    load();
  }, [load]);

  const upsert = useCallback(
    async (body: ProviderCredentialUpsert) => {
      setSaving(true);
      try {
        await apiClient(BASE, { method: "PUT", body: JSON.stringify(body) });
        await load();
      } finally {
        setSaving(false);
      }
    },
    [apiClient, load],
  );

  const remove = useCallback(
    async (id: string) => {
      await apiClient(`${BASE}/${id}`, { method: "DELETE" });
      await load();
    },
    [apiClient, load],
  );

  return { items, loading, saving, upsert, remove, reload: load };
};
