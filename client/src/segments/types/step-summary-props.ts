import type { SegmentFormState } from "@/segments/types/segment.types";

export interface StepSummaryProps {
  state: SegmentFormState;
}

export interface SectionProps {
  title: string;
  children: React.ReactNode;
}

export interface RowProps {
  label: string;
  value: string;
}
