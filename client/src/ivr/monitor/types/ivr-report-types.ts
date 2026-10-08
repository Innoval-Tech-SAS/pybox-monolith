/** Espejo de `messaging/ivr/schemas/ivr_report_schemas.py` del backend. */

export interface IvrOutcomeRow {
  key: string;
  label: string | null;
  count: number;
  percentage: number;
}

export interface IvrBreakdownRow {
  value: string | null;
  count: number;
}

export interface IvrFunnel {
  dialed: number;
  answered: number;
  human: number;
  interacted: number;
  transferred: number;
}

export interface IvrDuration {
  totalSeconds: number;
  averageSeconds: number;
  billableSeconds: number;
}

export interface IvrCampaignReport {
  campaignId: string;
  totalCalls: number;
  typifiedCalls: number;
  outcomes: IvrOutcomeRow[];
  byAmd: IvrBreakdownRow[];
  byEndNode: IvrBreakdownRow[];
  byAttempt: IvrBreakdownRow[];
  funnel: IvrFunnel;
  duration: IvrDuration;
}

export const FUNNEL_STEPS: Array<{ key: keyof IvrFunnel; label: string }> = [
  { key: "dialed", label: "Marcadas" },
  { key: "answered", label: "Contestaron" },
  { key: "human", label: "Persona detectada" },
  { key: "interacted", label: "Interactuaron" },
  { key: "transferred", label: "Transferidas" },
];
