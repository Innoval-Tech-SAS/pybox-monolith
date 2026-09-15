import { useCallback, useEffect, useReducer, useRef } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useIvrMonitorStream } from "./use-ivr-monitor-stream";
import {
  initialMonitorState,
  monitorReducer,
  type CallEntry,
} from "../utils/call-monitor-reducer";
import type {
  IvrCall,
  IvrCampaignStats,
  IvrCampaignStatusEvent,
  IvrSnapshot,
} from "../types/ivr-monitor-types";

export const useCallMonitor = (campaignId: string) => {
  const { apiClient } = useApiClient();
  const [state, dispatch] = useReducer(monitorReducer, initialMonitorState);

  // Evita pedir el snapshot dos veces en el arranque: el primer `onopen` del
  // stream llega justo después del fetch inicial.
  const initialFetchPending = useRef(false);

  const fetchSnapshot = useCallback(async () => {
    if (!campaignId) return;
    try {
      const snapshot: IvrSnapshot = await apiClient(
        `/ivr/monitor/snapshot?campaignId=${campaignId}`,
        { method: "GET" },
      );
      if (snapshot) dispatch({ type: "SNAPSHOT", snapshot });
    } catch {
      dispatch({
        type: "SNAPSHOT_ERROR",
        message: "No se pudo cargar el estado de la campaña.",
      });
    }
  }, [apiClient, campaignId]);

  useEffect(() => {
    initialFetchPending.current = true;
    fetchSnapshot();
  }, [fetchSnapshot]);

  useIvrMonitorStream(campaignId, {
    onCallUpdated: (data) => dispatch({ type: "CALL_UPDATED", call: data as IvrCall }),
    onStatsUpdated: (data) =>
      dispatch({ type: "STATS_UPDATED", stats: data as IvrCampaignStats }),
    onCampaignStatus: (data) =>
      dispatch({ type: "CAMPAIGN_STATUS", event: data as IvrCampaignStatusEvent }),
    onOpen: () => {
      dispatch({ type: "CONNECTED" });
      // Al reconectar hay que reconstruir el estado: los eventos emitidos
      // mientras el stream estuvo caído no se reenvían.
      if (initialFetchPending.current) {
        initialFetchPending.current = false;
        return;
      }
      fetchSnapshot();
    },
    onError: () => dispatch({ type: "DISCONNECTED" }),
  });

  // El cronómetro solo corre si hay algo en pantalla, para no re-renderizar una
  // tabla vacía cada segundo.
  const hasCalls = state.calls.length > 0;
  useEffect(() => {
    if (!hasCalls) return;
    const id = window.setInterval(() => dispatch({ type: "TICK" }), 1000);
    return () => window.clearInterval(id);
  }, [hasCalls]);

  return {
    calls: state.calls,
    stats: state.stats,
    campaignStatus: state.campaignStatus,
    loading: state.loading,
    connected: state.connected,
    error: state.error,
    tick: state.tick,
    refresh: fetchSnapshot,
  };
};

export type { CallEntry };
