import type { SegmentResponse } from "@/segments/types/segment.types";

export interface SegmentFormProps {
  orgId: string;
  onSuccess: () => void;
  onCancel: () => void;
  existing?: SegmentResponse;
}
