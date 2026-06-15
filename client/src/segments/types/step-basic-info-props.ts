import type { SegmentFormState } from "@/segments/types/segment.types";

export interface StepBasicInfoProps {
  state: SegmentFormState;
  update: (patch: Partial<SegmentFormState>) => void;
}
