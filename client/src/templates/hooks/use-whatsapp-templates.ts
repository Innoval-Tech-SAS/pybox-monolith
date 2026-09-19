import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useToast } from "@/context/toast-context";
import type {
  WhatsAppTemplateData,
  WhatsAppTemplateListResponse,
  WhatsAppTemplateResponse,
} from "@/types/templates/whatsapp-template-types";

// Tope de `pageSize` del backend. Los datos de Meta se piden en una sola llamada por
// portafolio y se cruzan por id con el listado genérico, en vez de una llamada por fila.
const META_DATA_PAGE_SIZE = 100;

export const useWhatsAppTemplates = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const { success } = useToast();
  const [dataByTemplateId, setDataByTemplateId] = useState<Record<string, WhatsAppTemplateData>>({});
  const [refreshingId, setRefreshingId] = useState<string | null>(null);

  useEffect(() => {
    if (!portfolioId) return;
    let cancelled = false;
    const params = new URLSearchParams({ portfolioId, page: "1", pageSize: String(META_DATA_PAGE_SIZE) });
    apiClient(`/whatsapp/templates/?${params}`, { method: "GET" })
      .then((data: WhatsAppTemplateListResponse) => {
        if (cancelled) return;
        setDataByTemplateId(
          Object.fromEntries((data?.items ?? []).map((row) => [row.whatsapp.templateId, row.whatsapp])),
        );
      })
      .catch(() => {
        if (!cancelled) setDataByTemplateId({});
      });
    return () => {
      cancelled = true;
    };
  }, [portfolioId, apiClient]);

  const refreshStatus = async (templateId: string): Promise<WhatsAppTemplateResponse | null> => {
    setRefreshingId(templateId);
    try {
      const updated: WhatsAppTemplateResponse = await apiClient(
        `/whatsapp/templates/${templateId}/refresh-status?portfolioId=${portfolioId}`,
        { method: "POST" },
      );
      setDataByTemplateId((prev) => ({ ...prev, [templateId]: updated.whatsapp }));
      success("Estado actualizado", `Meta reporta la plantilla como ${updated.whatsapp.metaStatus}.`);
      return updated;
    } catch {
      return null;
    } finally {
      setRefreshingId(null);
    }
  };

  const remove = useCallback(
    async (templateId: string): Promise<boolean> => {
      try {
        await apiClient(`/whatsapp/templates/${templateId}?portfolioId=${portfolioId}`, { method: "DELETE" });
        setDataByTemplateId((prev) => {
          const next = { ...prev };
          delete next[templateId];
          return next;
        });
        return true;
      } catch {
        return false;
      }
    },
    [apiClient, portfolioId],
  );

  return { dataByTemplateId, refreshingId, refreshStatus, remove };
};
