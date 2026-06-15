export interface SegmentsTableProps {
  segments: import("@/segments/types/segment.types").SegmentResponse[];
  loading: boolean;
  onEdit: (segment: import("@/segments/types/segment.types").SegmentResponse) => void;
  onExecute: (segment: import("@/segments/types/segment.types").SegmentResponse) => void;
  onHistory: (segment: import("@/segments/types/segment.types").SegmentResponse) => void;
  onDelete: (segment: import("@/segments/types/segment.types").SegmentResponse) => void;
}

export interface ActionBtnProps {
  title: string;
  onClick: () => void;
  icon: React.ReactNode;
  danger?: boolean;
}
