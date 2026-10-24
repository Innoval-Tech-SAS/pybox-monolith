import { useEffect, useRef } from "react";
import { API_URL } from "@/config/api";

interface StreamHandlers {
  onCallUpdated: (data: unknown) => void;
  onStatsUpdated: (data: unknown) => void;
  onCampaignStatus: (data: unknown) => void;
  onOpen: () => void;
  onError: () => void;
}

/**
 * Suscripción SSE al monitor de una campaña IVR.
 *
 * El access token vive en una cookie httpOnly, así que `EventSource` la adjunta
 * sola con `withCredentials` (mismo patrón que `utils/notification-stream.ts`).
 *
 * `EventSource` reconecta solo, por eso `onerror` NO cierra la conexión: hacerlo
 * mataría la reconexión automática del navegador. El consumidor usa `onOpen`
 * para volver a pedir el snapshot y no quedarse con estado viejo.
 */
export const useIvrMonitorStream = (campaignId: string, handlers: StreamHandlers) => {
  // Los handlers se guardan en un ref para no reabrir el stream en cada render
  // cuando el consumidor pasa funciones nuevas.
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;

  useEffect(() => {
    if (!campaignId) return;

    const es = new EventSource(
      `${API_URL}/ivr/monitor/stream?campaignId=${campaignId}`,
      { withCredentials: true },
    );

    const parse = (raw: string, handle: (data: unknown) => void) => {
      try {
        handle(JSON.parse(raw));
      } catch {
        // evento malformado: se ignora, el snapshot corrige el estado
      }
    };

    es.addEventListener("ivr:call-updated", (e) =>
      parse((e as MessageEvent).data, handlersRef.current.onCallUpdated),
    );
    es.addEventListener("ivr:stats-updated", (e) =>
      parse((e as MessageEvent).data, handlersRef.current.onStatsUpdated),
    );
    es.addEventListener("ivr:campaign-status", (e) =>
      parse((e as MessageEvent).data, handlersRef.current.onCampaignStatus),
    );
    // `ivr:heartbeat` no necesita handler: basta con que llegue para que la
    // conexión no se considere ociosa.

    es.onopen = () => handlersRef.current.onOpen();
    es.onerror = () => handlersRef.current.onError();

    return () => es.close();
  }, [campaignId]);
};
