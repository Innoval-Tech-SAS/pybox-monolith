import type { EntityFormState, EntityJoin } from "@/query-builder/types/query-builder-types";

export interface StepJoinsProps {
  state: EntityFormState;
  addJoin: (join: EntityJoin) => void;
  removeJoin: (index: number) => void;
  updateJoin: (index: number, patch: Partial<EntityJoin>) => void;
  allTableAliases: { alias: string; label: string }[];
}

export interface JoinRowProps {
  join: EntityJoin;
  tables: { alias: string; name: string }[];
  onChange: (patch: Partial<EntityJoin>) => void;
  onRemove: () => void;
}
