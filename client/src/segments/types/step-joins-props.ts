import type { SegmentFormState, SegmentJoin, JoinHow } from "@/segments/types/segment.types";

export interface StepJoinsProps {
  state: SegmentFormState;
  addJoin: (join: SegmentJoin) => void;
  removeJoin: (index: number) => void;
  updateJoin: (index: number, patch: Partial<SegmentJoin>) => void;
  allTableAliases: { alias: string; label: string }[];
}

export interface JoinRowProps {
  join: SegmentJoin;
  tables: { alias: string; name: string }[];
  onChange: (patch: Partial<SegmentJoin>) => void;
  onRemove: () => void;
}
