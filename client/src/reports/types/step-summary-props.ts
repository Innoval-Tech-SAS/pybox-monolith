import type { ReportFormState } from "@/reports/types/report.types";

export interface StepSummaryProps {
  state: ReportFormState;
}

export interface SectionProps {
  title: string;
  children: React.ReactNode;
}

export interface RowProps {
  label: string;
  value: string;
}
