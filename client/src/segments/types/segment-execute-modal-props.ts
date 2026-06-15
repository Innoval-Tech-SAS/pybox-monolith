import type { SegmentResponse } from "@/segments/types/segment.types";

export interface SegmentExecuteModalProps {
  isOpen: boolean;
  onClose: () => void;
  segment: SegmentResponse;
  orgId: string;
}
