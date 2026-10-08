/** Espejo de `messaging/ivr/schemas/ivr_monitor_schemas.py` del backend. */

export type IvrCallStatus =
  | "QUEUED"
  | "RINGING"
  | "HUMAN_DETECTED"
  | "MACHINE_DETECTED"
  | "IN_IVR"
  | "TRANSFERRING"
  | "COMPLETED"
  | "NO_ANSWER"
  | "FAILED"
  | "CANCELLED";

export interface IvrDtmfEvent {
  digit?: string | null;
  nodeId?: string | null;
  nextNode?: string | null;
  timestamp?: string | null;
}

export interface IvrCollectedItem {
  collected_data?: string | null;
  nodeId?: string | null;
  variable?: string | null;
  timestamp?: string | null;
}

export interface IvrCall {
  interactionId: string;
  bulkId: string;
  campaignId: string | null;
  phone: string;
  customerName: string | null;
  customerDocument: string | null;
  status: IvrCallStatus;
  lastEvent: string | null;
  attemptNumber: number;

  amdStatus: string | null;
  amdCause: string | null;
  dialStatus: string | null;
  transferred: boolean;

  lastDigit: string | null;
  ivrEndNodeId: string | null;
  ivrEndReason: string | null;
  dtmfEvents: IvrDtmfEvent[] | null;
  collectedData: IvrCollectedItem[] | null;

  durationSeconds: number | null;
  startedAt: string | null;
  answeredAt: string | null;
  transferStartedAt: string | null;
  endedAt: string | null;
  updatedAt: string | null;
}

export interface IvrCampaignStats {
  totalCalls: number;
  activeCalls: number;
  humanDetections: number;
  machineDetections: number;
  menuSelections: number;
  transfers: number;
  completed: number;
  failed: number;
  noAnswer: number;
  cancelled: number;
}

export interface IvrSnapshot {
  activeCalls: IvrCall[];
  stats: IvrCampaignStats;
  generatedAt: string;
}

export interface IvrCampaignStatusEvent {
  campaignId: string | null;
  bulkId: string;
  status: string | null;
  quantity: number | null;
  timestamp: string | null;
}

export const EMPTY_STATS: IvrCampaignStats = {
  totalCalls: 0,
  activeCalls: 0,
  humanDetections: 0,
  machineDetections: 0,
  menuSelections: 0,
  transfers: 0,
  completed: 0,
  failed: 0,
  noAnswer: 0,
  cancelled: 0,
};

export const TERMINAL_CALL_STATUSES: IvrCallStatus[] = [
  "COMPLETED",
  "NO_ANSWER",
  "FAILED",
  "CANCELLED",
];

export const isTerminalCall = (status: IvrCallStatus): boolean =>
  TERMINAL_CALL_STATUSES.includes(status);
