/** Espejo de `messaging/ivr/schemas/ivr_execution_schemas.py` del backend. */

export type IvrExecutionStatus = "PENDING" | "RUNNING" | "PAUSED" | "CANCELLED" | "FINISHED";

export interface IvrExecution {
  bulkId: string;
  campaignId: string;
  campaignTimeId: string | null;
  status: IvrExecutionStatus;
  quantity: number;
  callsPerSecond: number | null;
  maxConcurrent: number | null;
  dispatchedAt: string;
  finishedAt: string | null;
}

export const TERMINAL_EXECUTION_STATUSES: IvrExecutionStatus[] = ["CANCELLED", "FINISHED"];
