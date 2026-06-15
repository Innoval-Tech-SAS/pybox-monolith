import type { SegmentResponse } from "@/segments/types/segment.types";

export interface SegmentExecutionsHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  segment: SegmentResponse;
  orgId: string;
}
