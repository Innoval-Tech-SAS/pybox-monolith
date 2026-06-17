import type { ReportFormState } from "@/reports/types/report.types";

export interface StepBasicInfoProps {
  state: ReportFormState;
  update: (patch: Partial<ReportFormState>) => void;
}
