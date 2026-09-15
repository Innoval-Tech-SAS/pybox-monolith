import {
  EMPTY_STATS,
  isTerminalCall,
  type IvrCall,
  type IvrCampaignStats,
  type IvrCampaignStatusEvent,
  type IvrSnapshot,
} from "../types/ivr-monitor-types";

/**
 * Una llamada que termina se mantiene visible este tiempo antes de salir de la
 * tabla de activas. Sin esto, las llamadas cortas aparecen y desaparecen sin
 * que dé tiempo a leerlas (mismo criterio que el monitor de collectia).
 */
export const TERMINAL_DISPLAY_MS = 10_000;

export interface CallEntry extends IvrCall {
  /** Momento (reloj del navegador) en que se vio terminal por primera vez. */
  terminalAt: number | null;
}

export interface MonitorState {
  calls: CallEntry[];
  stats: IvrCampaignStats;
  campaignStatus: string | null;
  loading: boolean;
  connected: boolean;
  error: string | null;
  /** Se incrementa cada segundo para refrescar los cronómetros en pantalla. */
  tick: number;
}

export const initialMonitorState: MonitorState = {
  calls: [],
  stats: EMPTY_STATS,
  campaignStatus: null,
  loading: true,
  connected: false,
  error: null,
  tick: 0,
};

export type MonitorAction =
  | { type: "SNAPSHOT"; snapshot: IvrSnapshot }
  | { type: "SNAPSHOT_ERROR"; message: string }
  | { type: "CALL_UPDATED"; call: IvrCall }
  | { type: "STATS_UPDATED"; stats: IvrCampaignStats }
  | { type: "CAMPAIGN_STATUS"; event: IvrCampaignStatusEvent }
  | { type: "CONNECTED" }
  | { type: "DISCONNECTED" }
  | { type: "TICK" };

const withTerminalAt = (call: IvrCall, previous?: CallEntry): CallEntry => {
  if (!isTerminalCall(call.status)) return { ...call, terminalAt: null };
  // Se conserva el `terminalAt` original: un evento repetido sobre una llamada
  // ya cerrada no debe reiniciar su cuenta de permanencia en pantalla.
  return { ...call, terminalAt: previous?.terminalAt ?? Date.now() };
};

const upsert = (calls: CallEntry[], incoming: IvrCall): CallEntry[] => {
  const index = calls.findIndex((c) => c.interactionId === incoming.interactionId);
  if (index < 0) return [withTerminalAt(incoming), ...calls];

  const next = [...calls];
  next[index] = withTerminalAt(incoming, calls[index]);
  return next;
};

export const monitorReducer = (state: MonitorState, action: MonitorAction): MonitorState => {
  switch (action.type) {
    case "SNAPSHOT": {
      // El snapshot es la verdad: reemplaza la lista en vez de fusionarla, así
      // una reconexión no arrastra llamadas que ya no existen. Se conserva el
      // `terminalAt` de las que ya estaban para no reiniciar su temporizador.
      const previous = new Map(state.calls.map((c) => [c.interactionId, c]));
      return {
        ...state,
        calls: action.snapshot.activeCalls.map((c) =>
          withTerminalAt(c, previous.get(c.interactionId)),
        ),
        stats: action.snapshot.stats,
        loading: false,
        error: null,
      };
    }

    case "SNAPSHOT_ERROR":
      return { ...state, loading: false, error: action.message };

    case "CALL_UPDATED":
      return { ...state, calls: upsert(state.calls, action.call) };

    case "STATS_UPDATED":
      return { ...state, stats: action.stats };

    case "CAMPAIGN_STATUS":
      return { ...state, campaignStatus: action.event.status ?? state.campaignStatus };

    case "CONNECTED":
      return { ...state, connected: true };

    case "DISCONNECTED":
      return { ...state, connected: false };

    case "TICK": {
      const cutoff = Date.now() - TERMINAL_DISPLAY_MS;
      const calls = state.calls.filter((c) => c.terminalAt === null || c.terminalAt > cutoff);
      return {
        ...state,
        tick: state.tick + 1,
        // Si no expiró ninguna se conserva la referencia previa del array para
        // no re-renderizar la tabla en cada segundo sin motivo.
        calls: calls.length === state.calls.length ? state.calls : calls,
      };
    }

    default:
      return state;
  }
};
