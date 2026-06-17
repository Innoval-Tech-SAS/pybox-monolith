import type { ReportFormState, ReportJoin } from "@/reports/types/report.types";

export interface StepJoinsProps {
  state: ReportFormState;
  addJoin: (join: ReportJoin) => void;
  removeJoin: (index: number) => void;
  updateJoin: (index: number, patch: Partial<ReportJoin>) => void;
  allTableAliases: { alias: string; label: string }[];
}

export interface JoinRowProps {
  join: ReportJoin;
  tables: { alias: string; name: string }[];
  onChange: (patch: Partial<ReportJoin>) => void;
  onRemove: () => void;
}
